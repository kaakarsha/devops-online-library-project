# pylint: disable=no-member

"""
Views module for handling book management, authentication, and user/admin operations.
"""
import os
from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Count
from . import models
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse
from django.core.mail import send_mail

from bookapp.forms import UserRegistrationForm
from bookapp import models


def index(_request):
    return HttpResponse("Hello, world. You're at the polls index.")


def check_if_admin_or_user(view_func):
    def wrapper(request, *_args, **_kwargs):
        if not request.user.is_staff and request.path in [
            "/admin-book-list/",
            "/admin-book-detail/",
            "/admin-book-request-list/",
        ]:
            logout(request)
            return redirect("login_page")

        if request.user.is_staff and request.path not in [
            "/admin-book-list/",
            "/admin-book-detail/",
            "/admin-book-request-list/",
        ]:
            logout(request)
            return redirect("login_page")

        request.access = True
        return view_func(request, *_args, **_kwargs)

    return wrapper


class LogoutView(View):
    def get(self, request, *_args, **_kwargs):
        logout(request)
        return redirect("login_page")


class LoginView(View):
    def get(self, request, *_args, **_kwargs):
        return render(request, template_name="login.html")

    def post(self, request, *_args, **_kwargs):
        user_obj = authenticate(
            request,
            username=request.POST.get("email-username"),
            password=request.POST.get("password"),
        )

        if not user_obj:
            return render(
                request,
                template_name="login.html",
                context={"error": "Invalid Credentials"},
            )

        if user_obj and user_obj.is_staff and user_obj.is_active:
            login(request, user_obj)
            return redirect("admin_book_list")

        if user_obj and user_obj.is_active:
            login(request, user_obj)
            return redirect("user_book_list")

        return redirect("login_page")


class RegisterView(View):
    def get(self, request, *_args, **_kwargs):
        form = UserRegistrationForm()
        return render(request, "register.html", {"form": form})

    def post(self, request, *_args, **_kwargs):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            return redirect("login_page")
        return render(request, "register.html", {"form": form})


class IndexView(View):
    def get(self, request, *_args, **_kwargs):
        return render(request, template_name="index.html")


@method_decorator(check_if_admin_or_user, name="dispatch")
class AdminBookListView(View):
    def get(self, request, *_args, **_kwargs):
        if request.GET.get("query"):
            book_obj = models.BookModel.objects.filter(
                book_title__icontains=request.GET.get("query")
            ).values()
        else:
            book_obj = models.BookModel.objects.values()

        for obj in book_obj:
            if models.BookAllotmentModel.objects.filter(
                book=obj.get("id"), status="approved"
            ).exists():
                obj["available"] = False
            else:
                obj["available"] = True

            obj["book_img"] = obj.get("book_img").split("/")[1]

        return render(
            request,
            template_name="admin_book_list.html",
            context={"book_list": book_obj},
        )

    def post(self, request, *_args, **_kwargs):
        if request.POST.get("deletesubmit") and request.POST.get("book_id"):
            models.BookModel.objects.filter(id=request.POST.get("book_id")).delete()

        if request.POST.get("releasesubmit") and request.POST.get("book_id"):
            models.BookAllotmentModel.objects.filter(
                book__id=request.POST.get("book_id")
            ).delete()

        return redirect("admin_book_list")


class AdminBookStatusList(View):
    def get(self, request, *_args, **_kwargs):
        """Show book status."""
        allot_obj = models.BookAllotmentModel.objects.values(
            "user__username", "book__book_title", "modefield_at", "status"
        )
        return render(
            request,
            template_name="admin_book_status.html",
            context={"book_list": allot_obj},
        )

@method_decorator([login_required, check_if_admin_or_user], name="dispatch")
class UserBookListView(View):
    def get(self, request, *_args, **_kwargs):
        if request.GET.get("query"):
            book_obj = models.BookModel.objects.filter(
                book_title__icontains=request.GET.get("query")
            ).values()
        else:
            book_obj = models.BookModel.objects.values()

        for obj in book_obj:
            allot_obj = models.BookAllotmentModel.objects.filter(
                book=obj.get("id"), user=request.user
            ).first()

            obj["available"] = allot_obj.status if allot_obj else None
            obj["occupied"] = bool(allot_obj and allot_obj.user != request.user)
            
            img_path = obj.get("book_img", "")
            if img_path:
                obj["book_img"] = os.path.basename(img_path)

        # Most requested books
        most_requested_books = (
            models.BookAllotmentModel.objects
            .values("book__id", "book__book_title", "book__book_img")
            .annotate(request_count=Count("id"))
            .order_by("-request_count")[:5]
        )
        
        # Extract filename for most_requested
        for book in most_requested_books:
            if book.get("book__book_img"):
                book["book__book_img"] = os.path.basename(book["book__book_img"])

        # Most read books (approved requests)
        most_read_books = (
            models.BookAllotmentModel.objects
            .filter(status="approved")
            .values("book__id", "book__book_title", "book__book_img")
            .annotate(read_count=Count("id"))
            .order_by("-read_count")[:5]
        )
        
        # Extract filename for most_read
        for book in most_read_books:
            if book.get("book__book_img"):
                book["book__book_img"] = os.path.basename(book["book__book_img"])

        # Trending books (last 7 days)
        trending_books = (
            models.BookAllotmentModel.objects
            .filter(created_at__gte=now() - timedelta(days=7))
            .values("book__id", "book__book_title", "book__book_img")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )
        
        # Extract filename for trending
        for book in trending_books:
            if book.get("book__book_img"):
                book["book__book_img"] = os.path.basename(book["book__book_img"])

        return render(
            request,
            template_name="user_book_list.html",
            context={
                "book_list": book_obj,
                "most_requested": most_requested_books,
                "most_read": most_read_books,
                "trending": trending_books,
            },
        )

    def post(self, request, *_args, **_kwargs):
        models.BookAllotmentModel.objects.filter(user=request.user).delete()

        if request.POST.get("request_book"):
            book_obj = models.BookModel.objects.get(
                id=request.POST.get("request_book")
            )
            models.BookAllotmentModel.objects.create(
                user=request.user, book=book_obj, status="pending"
            )

        return redirect("user_book_list")



@method_decorator(check_if_admin_or_user, name="dispatch")
class UserHistoryList(View):
    def get(self, request, *_args, **_kwargs):
        """Show user activity."""
        allot_obj = models.BookAllotmentModel.objects.filter(user=request.user).values(
            "user__username", "book__book_title", "modefield_at", "status"
        )
        return render(
            request,
            template_name="user_book_status.html",
            context={"book_list": allot_obj},
        )


@method_decorator(check_if_admin_or_user, name="dispatch")
class AdminBookDetailView(View):

    def get(self, request, *_args, **_kwargs):
        book_obj = None
        if request.GET.get("book"):
            book_obj = (
                models.BookModel.objects.filter(id=request.GET.get("book"))
                .values()
                .first()
            )
            book_obj["book_img"] = book_obj.get("book_img").split("/")[1]

        return render(
            request,
            template_name="admin_book_detail.html",
            context={"book_obj": book_obj},
        )

    def post(self, request, *_args, **_kwargs):
        """Save book details."""
        if request.GET.get("book"):
            book_obj = models.BookModel.objects.get(id=request.GET.get("book"))
            book_obj.book_title = request.POST.get("title")
            book_obj.activity_desc = request.POST.get("desc")
            if request.FILES.get("fileinput"):
                book_obj.book_img = request.FILES.get("fileinput")
            book_obj.save()
            return redirect("admin_book_list")

        models.BookModel.objects.create(
            book_title=request.POST.get("title"),
            activity_desc=request.POST.get("desc"),
            book_img=request.FILES.get("fileinput"),
        )
        return redirect("admin_book_list")


@method_decorator(check_if_admin_or_user, name="dispatch")
class AdminBookRequestListView(View):
    def get(self, request, *_args, **_kwargs):
        book_list = models.BookAllotmentModel.objects.filter(status="pending").values(
            "id", "created_at", "modefield_at", "user__username", "book__book_title"
        )
        return render(
            request,
            template_name="admin_book_request.html",
            context={"book_lst": book_list},
        )

    def post(self, request, *_args, **_kwargs):
        """Approve/reject requests and send emails."""
        reject_lst, approve_lst = [], []

        for ele in request.POST:
            if "reject" in ele:
                reject_lst.append(request.POST.get(ele))
            elif "approved" in ele:
                approve_lst.append(request.POST.get(ele))

        models.BookAllotmentModel.objects.filter(id__in=reject_lst).update(
            status="rejected"
        )

        approved_objs = models.BookAllotmentModel.objects.filter(id__in=approve_lst)
        approved_objs.update(status="approved")

        for obj in approved_objs:
            if obj.user.email:
                send_mail(
                    subject="Book Request Approved",
                    message=(
                        f"Hello {obj.user.username}, your request for "
                        f"'{obj.book.book_title}' is approved."
                    ),
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[obj.user.email],
                    fail_silently=False,
                )

        return redirect("admin_book_request_list")
        