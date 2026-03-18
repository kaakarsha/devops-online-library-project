"""
Forms module for handling user registration.
"""
from django import forms
from django.contrib.auth.models import User

class UserRegistrationForm(forms.ModelForm):
    """
    Form for registering a new user with username, email, and password.
    """
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        """
        Meta configuration for UserRegistrationForm.
        """
        model = User
        fields = ["username", "email", "password"]

    def clean_email(self):
        """
        Validate that the email is unique.
        """
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def clean_username(self):
        """
        Validate that the username is unique.
        """
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username
        