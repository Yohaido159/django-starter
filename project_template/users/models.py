from django.db import models
from django.contrib.auth.models import AbstractBaseUser,  PermissionsMixin
from django.contrib.auth.models import AnonymousUser

from dj_rql.drf import RQLFilterBackend


from .querysets import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.CharField(max_length=225, blank=True, null=True)
    first_name = models.CharField(max_length=225, blank=True, null=True)
    last_name = models.CharField(max_length=225, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<User name={self.name}/>"


class AnonymousUser(AnonymousUser):
    first_name = ""
    last_name = ""
    email = None
    image = None
    image_big = None
    is_instructor = False
    is_active = False
    is_staff = False
    is_superuser = False
    how_couse_he_can = 0
    short_description = None
