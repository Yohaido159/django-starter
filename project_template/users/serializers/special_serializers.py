import serpy
from urllib.parse import quote, urlencode
from django.conf import settings
from base64 import b32encode

from dj_rest_auth.registration.serializers import RegisterSerializer as DefaultRegisterSerializer
from dj_rest_auth.serializers import LoginSerializer as DefaultLoginSerializer
# from django_otp.plugins.otp_totp.models import TOTPDevice
from users.models import TOTPDevice

from ..models import UserEnrollment, UserEnrollmentDB, UserMetadata, User
from courses.serializers.get_serializers import SerializerUserCreateCourse
from courses.models import Course
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied
from rest_framework import fields, serializers
from utils import utils
from utils.utils import QuickExit201
from utils.serpy_my import JSONField, NestedField, SerpyDateTimeField, NestedFieldDict


class EmailFieldLower(serializers.EmailField):
    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        return value.lower()


class SerializerRegister(DefaultRegisterSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = EmailFieldLower(required=True)

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "image",
            "password1",
            "password2",
        ]

    def save(self):
        email = self.validated_data['email']
        user = get_user_model()(
            email=email,
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],
        )

        password1 = self.validated_data['password1']
        password2 = self.validated_data['password2']

        if password1 != password2:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        user.set_password(password1)
        user.save()
        return user


class SerializerUserLogin(DefaultLoginSerializer):
    mfa_code = serializers.IntegerField(required=False)
    email = EmailFieldLower(required=True)
