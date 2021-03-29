from django.db import models
from django.contrib.auth.models import AbstractUser
import dbsettings
from datetime import timedelta
from .managers import CustomUserManager


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField('email address', unique=True)
    activation_mail_date = models.DateTimeField('activation mail date',null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class ActivationEmailOptions(dbsettings.Group):
    expiration_time = dbsettings.DurationValue(
        'The ammount of time that has to pass before the activation email becomes invalid',
        default=timedelta(minutes=2))

