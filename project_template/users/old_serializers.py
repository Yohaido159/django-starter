import serpy
from urllib.parse import quote, urlencode
from django.conf import settings
from base64 import b32encode

from dj_rest_auth.registration.serializers import RegisterSerializer as DefaultRegisterSerializer
from dj_rest_auth.serializers import LoginSerializer as DefaultLoginSerializer
# from django_otp.plugins.otp_totp.models import TOTPDevice
from users.models import TOTPDevice

from .models import UserEnrollment, UserEnrollmentDB, UserMetadata, User
from courses.serializers.get_serializers import SerializerUserCreateCourse
from courses.models import Course
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied
from rest_framework import fields, serializers
from utils import utils
from utils.utils import QuickExit201
from utils.serpy_my import JSONField, NestedField, SerpyDateTimeField, NestedFieldDict


class SerializerUserEnrollmentDB(serializers.ModelSerializer):
    class Meta:
        model = UserEnrollmentDB
        fields = "__all__"


class SerializerUserEnrollmentDBRead(serpy.Serializer):
    id = serpy.Field()
    name = serpy.Field(attr="course.name")
    image = serpy.Field(attr="course.image")
    description_short = serpy.Field(attr="course.description_short")
    course = serpy.Field(attr="course.id")
    is_rating = serpy.Field(attr="is_rating")
    enroll_at = SerpyDateTimeField(attr="enroll_at")
    last_view = serpy.Field(attr="last_view")
    watch_list = serpy.Field(attr="watch_list")
    question = serpy.Field(attr="question")
    is_review = serpy.Field(attr="is_review")
    review = serpy.Field(attr="review")
    rating = serpy.Field(attr="rating")
    user = serpy.Field(attr="user.id")


class SerializerUserEnrollment(serializers.ModelSerializer):
    class Meta:
        model = UserEnrollment
        fields = "__all__"


class SerializerUserEnrollmentReadDict(serpy.DictSerializer):
    id = serpy.Field()
    courses = serpy.Field()


class SerializerTOTPDeviceReadDict(serpy.DictSerializer):
    id = serpy.Field(required=False)
    config_url = serpy.MethodField(required=False)

    def get_config_url(self, value):
        if value:
            # from django_otp.plugins.otp_totp.models import TOTPDevice
            from users.models import TOTPDevice

            totp_device = TOTPDevice.objects.get(id=value.get('id'))
            return totp_device.config_url
        return None


class SerializerUserMetadataReadDict(serpy.DictSerializer):
    id = serpy.Field()
    last_view_courses = JSONField()
    # user = serpy.Field(attr="user.id")
    paypal_instructor = JSONField()


class SerializerUserMetadata(serializers.ModelSerializer):
    class Meta:
        model = UserMetadata
        fields = "__all__"

    def update(self, instance, validated_data):
        res = super().update(instance, validated_data)
        return res


class SerializerUserMeReadDict(serpy.DictSerializer):
    id = serpy.Field()
    draft = serpy.Field()
    name = serpy.Field()
    first_and_last = serpy.Field()
    first_name = serpy.Field()
    last_name = serpy.Field()
    email = serpy.Field()
    image = serpy.Field()
    image_big = serpy.Field()

    num_total_users = serpy.Field()
    num_courses_create = serpy.Field()
    num_courses_buy = serpy.Field()

    is_instructor = serpy.Field()
    is_active = serpy.Field()
    is_staff = serpy.Field()
    is_superuser = serpy.Field()

    how_couse_he_can = serpy.Field()

    user_metadata = NestedFieldDict(nested=SerializerUserMetadataReadDict)
    user_create_course = NestedFieldDict(nested=SerializerUserCreateCourse, many=True)
    user_enrollment = NestedFieldDict(nested=SerializerUserEnrollmentReadDict)
    short_description = JSONField()
    mfa_config = NestedFieldDict(nested=SerializerTOTPDeviceReadDict, required=False)


class SerializerUserMeWrite(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = "__all__"

    def update(self, instance, validated_data):
        if "is_superuser" in validated_data:
            raise PermissionDenied
        if "is_staff" in validated_data:
            raise PermissionDenied
        if "is_active" in validated_data:
            raise PermissionDenied
        if "how_couse_he_can" in validated_data:
            raise PermissionDenied
        if "is_instructor" in validated_data:
            raise PermissionDenied
        if "email" in validated_data:
            pass
            # TODO need to make email validation

        res = super().update(instance, validated_data)
        return res


class SerializerTOTPDevice(serializers.ModelSerializer):
    user = serializers.CharField(required=False, write_only=True)
    name = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = TOTPDevice
        fields = "__all__"

    def create(self, validated_data):
        user = self.context['request'].user
        totp_device = TOTPDevice.objects.create(user=user, name="MFACode", confirmed=False)

        raise QuickExit201({
            "data": {
                "id": totp_device.id,
                "config_url": totp_device.config_url
            },
            "more_data": {
                "is_confirmed": False, "has_mfa": True
            }
        })


class SerializerUser(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class SerializerUserGet(serpy.Serializer):
    id = serpy.Field()
    name = serpy.Field()
    image = serpy.Field()
    image_big = serpy.Field()
    short_description = JSONField()

    num_courses = serpy.Field()
    user_create_course = serpy.MethodField()

    def get_user_create_course(self, instance):
        user_create_course = instance.User_Course.all()
        serializer = SerializerUserCreateCourse(user_create_course, many=True).data
        serializer = utils.make_list_dict_serpy(serializer)
        return serializer


class SerializerRegister(DefaultRegisterSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    class Meta:
        model = get_user_model()
        fields = [
            "email",
            "first_name",
            "last_name",
            "image",
            "password1",
            "password2",
        ]

    def save(self, request, *args, **kwargs):
        print("self.validated_data", self.validated_data)
        user = get_user_model()(
            email=self.validated_data['email'],
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
