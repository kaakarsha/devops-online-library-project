from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
from datetime import datetime
from django.utils import timezone


class BookModel(models.Model):
    book_title = models.CharField(max_length=256)
    book_img = models.ImageField(upload_to="media")
    activity_desc = models.TextField()


class BookAllotmentModel(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    book = models.ForeignKey(BookModel, models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    modefield_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=256)
