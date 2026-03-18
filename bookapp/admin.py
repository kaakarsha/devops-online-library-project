"""Dajngo Admin here"""
from django.contrib import admin
from bookapp import models

# Register your models here.
admin.site.register(models.BookAllotmentModel)
admin.site.register(models.BookModel)
