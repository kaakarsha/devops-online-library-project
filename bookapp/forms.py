"""
Forms module for handling user registration.
"""
from django import forms
from django.contrib.auth.models import User

class UserRegistrationForm(forms.ModelForm):
    """User registration form"""
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        """meta class"""
        model = User
        fields = ["username", "email", "password"]

    def clean_email(self):
        """Clean Email function"""
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def clean_username(self):
        """Clean Username Function"""
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username
        