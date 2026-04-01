# pylint: disable=no-member
"""
Basic Django tests for bookapp (simple & stable).
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from bookapp import models


class BasicViewTests(TestCase):
    """Basic tests that avoid complex failures."""

    def setUp(self):
        """Setup test data."""
        self.client = Client()

        # Create users
        self.user = User.objects.create_user(
            username="user", password="pass123"
        )
        self.admin = User.objects.create_user(
            username="admin", password="pass123", is_staff=True
        )

        self.book = models.BookModel.objects.create(
            book_title="Test Book",
            book_img="media/test.jpg",  # ensures split("/") works
            activity_desc="Test desc",
        )

    def test_index(self):
        """Index page should load."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_login_page_load(self):
        """Login page loads."""
        response = self.client.get(reverse("login_page"))
        self.assertEqual(response.status_code, 200)

    def test_user_login(self):
        """User can login."""
        response = self.client.post(
            reverse("login_page"),
            {"email-username": "user", "password": "pass123"},
        )
        self.assertEqual(response.status_code, 302)

    def test_admin_login(self):
        """Admin can login."""
        response = self.client.post(
            reverse("login_page"),
            {"email-username": "admin", "password": "pass123"},
        )
        self.assertEqual(response.status_code, 302)

    def test_user_book_list_requires_login(self):
        """User book list requires login."""
        response = self.client.get(reverse("user_book_list"))
        self.assertEqual(response.status_code, 302)

    def test_user_book_list_logged_in(self):
        """Logged-in user can access book list."""
        self.client.login(username="user", password="pass123")
        response = self.client.get(reverse("user_book_list"))
        self.assertEqual(response.status_code, 200)

    def test_admin_book_list_access(self):
        """Admin can access admin book list."""
        self.client.login(username="admin", password="pass123")
        response = self.client.get(reverse("admin_book_list"))
        self.assertEqual(response.status_code, 200)

    def test_book_request(self):
        """User can request a book."""
        self.client.login(username="user", password="pass123")

        response = self.client.post(
            reverse("user_book_list"),
            {"request_book": self.book.id},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            models.BookAllotmentModel.objects.filter(user=self.user).exists()
        )
        