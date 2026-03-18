"""Django Apps here"""
from django.apps import AppConfig
class BookappConfig(AppConfig):
    """Book App Config"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bookapp'
