from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login_page"),
    path("", views.LoginView.as_view(), name="login_page"),
    path("logout/", views.LoginView.as_view(), name="logout_page"),
    path("register/", views.RegisterView.as_view(), name="register_page"),
    path("index/", views.IndexView.as_view(), name="index_page"),
    path("admin-book-list/", views.AdminBookListView.as_view(), name="admin_book_list"),
    path("user-book-list/", views.UserBookListView.as_view(), name="user_book_list"),
    path(
        "user-history-list/", views.UserHistoryList.as_view(), name="user_book_history"
    ),
    path(
        "admin-book-status-list/",
        views.AdminBookStatusList.as_view(),
        name="admin_book_status_list",
    ),
    path(
        "admin-book-detail/",
        views.AdminBookDetailView.as_view(),
        name="admin_book_detail",
    ),
    path(
        "admin-book-request-list/",
        views.AdminBookRequestListView.as_view(),
        name="admin_book_request_list",
    ),
    # path('register/', views.UserRegisterView.as_view(), name='user_register'),
    # path('user-details/', views.UpdateUserDetailsView.as_view(), name='user_details'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
