from courses.serializers.write_serializers import SerializerCourse
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
from utils.utils import QuickExit201, SerpyDictSerializerGroup
from utils.serpy_my import JSONField, NestedField, SerpyDateTimeField, NestedFieldDict, FactorDictSerializer, MyDictSerializer


class SerializerTOTPDeviceRead(serpy.Serializer):
    id = serpy.Field(required=True)
    config_url = serpy.MethodField(required=False)

    def get_config_url(self, value):
        if value:

            assert False
            return value
            # from django_otp.plugins.otp_totp.models import TOTPDevice
            # from users.models import TOTPDevice
            # assert False
            # totp_device = TOTPDevice.objects.get(id=value.get('otp_totp_totpdevice_id'))
            # return totp_device.config_url
        return None


class SerializerTOTPDeviceReadDict(SerializerTOTPDeviceRead, serpy.DictSerializer):
    pass
    # @property
    # def data(self):
    #     res = super().data
    #     assert False


class SerializerUserMetadataRead(serpy.Serializer):
    id = serpy.Field()
    last_view_courses = JSONField()
    paypal_instructor = JSONField()


class SerializerUserMetadataReadDict(SerializerUserMetadataRead, MyDictSerializer):
    pass


class SerializerUserEnrollmentDBRead(serpy.Serializer):
    id = serpy.Field()
    user = serpy.Field(attr="user.user.name")
    course_id = serpy.Field(attr="course.id")
    name_slug = serpy.Field(attr="course.name_slug")
    name = serpy.Field(attr="course.name")
    description_short = serpy.Field(attr="course.description_short")
    course_status = serpy.Field(attr="course.Course_CourseActiveRequest.status")
    image = serpy.Field(attr="course.image")
    enroll_at = serpy.Field()
    last_view = JSONField()
    watch_list = JSONField()
    question = JSONField()
    is_review = serpy.Field()
    status = serpy.Field()
    review = JSONField()
    rating = serpy.Field()
    is_rating = serpy.Field(required=False)


class SerializerUserEnrollmentDBReadDict(SerializerUserEnrollmentDBRead, serpy.DictSerializer):
    pass


class SerializerUserEnrollmentDBReadDictNew(SerializerUserEnrollmentDBRead, serpy.DictSerializer):
    id = serpy.Field()
    user = serpy.Field()
    course_id = serpy.Field()
    name_slug = serpy.Field()
    name = serpy.Field()
    description_short = serpy.Field()
    course_status = serpy.Field()
    image = serpy.Field()
    watch_list = JSONField(required=False)
    last_view = serpy.Field(required=False)


class SerializerUserEnrollmentRead(serpy.Serializer):
    id = serpy.Field()
    courses = NestedFieldDict(nested=SerializerUserEnrollmentDBReadDictNew, many=True, key_str="course_id")


class SerializerUserEnrollmentReadDict(SerializerUserEnrollmentRead, MyDictSerializer):
    pass


class SerializerUserReadBase(serpy.Serializer):
    id = serpy.Field()
    email = serpy.Field()
    first_name = serpy.Field()
    last_name = serpy.Field()
    image = serpy.Field()
    image_big = serpy.Field()
    is_instructor = serpy.Field()
    is_active = serpy.Field()
    is_staff = serpy.Field()
    is_superuser = serpy.Field()
    how_couse_he_can = serpy.Field()
    short_description = JSONField()


class SerializerUserDict(SerializerUserReadBase, serpy.DictSerializer):
    pass

################################################################
# Special
################################################################


class SerializerUserMeReadDict(MyDictSerializer):
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

    how_courses_instroctor_can = serpy.Field()
    how_users_instructor_can_in_course = serpy.Field()
    updated_at = serpy.Field()
    is_active = serpy.Field()

    # user_metadata = FactorDictSerializer(nested=SerializerUserMetadataReadDict, default={"id": None,
    #                                                                                      "last_view_courses": [],
    #                                                                                      "paypal_instructor": {},
    #                                                                                      "lastCourses": {},
    #                                                                                      })
    # user_create_course = FactorDictSerializer(nested=SerializerUserCreateCourse, many=True, default={"id": None,
    #                                                                                                  "courses": {},
    #                                                                                                  })
    # user_enrollment = FactorDictSerializer(nested=SerializerUserEnrollmentReadDict, default={})

    user_metadata = NestedFieldDict(nested=SerializerUserMetadataReadDict, default={"id": None,
                                                                                    "last_view_courses": [],
                                                                                    "paypal_instructor": {},
                                                                                    "lastCourses": {},
                                                                                    })

    user_create_course = NestedFieldDict(nested=SerializerUserCreateCourse, many=True)
    user_enrollment = NestedFieldDict(nested=SerializerUserEnrollmentReadDict)

    short_description = JSONField()
    mfa_config = serpy.MethodField()

    def get_mfa_config(self, value):
        from django_otp.plugins.otp_totp.models import TOTPDevice
        from users.models import TOTPDevice

        if value:
            otp_totp_totpdevice_id = value.get("otp_totp_totpdevice_id")
            try:
                totp_device = TOTPDevice.objects.get(id=value.get('otp_totp_totpdevice_id'))
                return {
                    "id": otp_totp_totpdevice_id,
                    "config_url": totp_device.config_url
                }
            except TOTPDevice.DoesNotExist:
                return {
                }

        return None


################################################################
