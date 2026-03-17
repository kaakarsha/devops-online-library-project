from django.test import TestCase
from django.urls import reverse

class MyViewTestCase(TestCase):
    def test_home_view(self):
        """Test if login page returns 200 status"""
        response = self.client.get(reverse('login_page'))
        self.assertEqual(response.status_code, 200)
