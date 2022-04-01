from django.db import models
from django.contrib.auth.models import AbstractBaseUser,  PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AnonymousUser


from .querysets import UserManager
# from utils.utils import  authenticated_users, allow_staff_or_superuser


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    image = models.URLField(blank=True, null=True)
    image_big = models.URLField(blank=True, null=True)
    is_instructor = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    # @staticmethod
    # @authenticated_users
    # def has_read_permission(request):
    #     return True

    # @staticmethod
    # @authenticated_users
    # def has_write_permission(request):
    #     return False

    # @authenticated_users
    # def has_object_write_permission(self, request):
    #     return request.user == self

    # @staticmethod
    # @authenticated_users
    # def has_update_user_payment_permission(request):
    #     return True

    # @staticmethod
    # @allow_staff_or_superuser
    # def has_send_mail_to_users_permission(request):
    #     return True

    # @authenticated_users
    # def has_object_destroy_permission(self, request):
    #     return False

    # @authenticated_users
    # def has_object_post_permission(self, request):
    #     return False


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
