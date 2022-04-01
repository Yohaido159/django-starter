from django.db.models import QuerySet, Count, Sum, Case, When
from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.apps import apps
from django.db.models import Value, Count, F, Q
from django.db.models.functions import Concat, Substr


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **kwargs):
        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **kwargs):
        user = self.create_user(email, password, **kwargs)
        user.is_staff = True
        user.is_superuser = True
        user.is_instructor = True
        user.save(using=self._db)
        return user
