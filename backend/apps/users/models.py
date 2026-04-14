from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    resume_text = models.TextField(blank=True)
    skills = models.JSONField(default=list)
    preferred_role = models.CharField(max_length=100, blank=True)
    preferred_location = models.CharField(max_length=100, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
