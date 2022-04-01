import decimal
import timeit
import datetime
import hashlib
import json

from django.db import connection
from django.db.models import Prefetch
from django.core import signing
from django_otp.models import SideChannelDevice
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404


from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.decorators import action, api_view, authentication_classes, permission_classes
from rest_framework.exceptions import MethodNotAllowed

from dj_rest_auth.jwt_auth import JWTCookieAuthentication
from django_rest_passwordreset.views import ResetPasswordConfirm as ResetPasswordConfirmOrginal, ResetPasswordRequestToken
from dry_rest_permissions.generics import DRYPermissions, DRYObjectPermissions

from ..serializers.get_serializers import *
from ..serializers.write_serializers import *
from ..serializers.special_serializers import *
from ..models import *
from ..permissions import *
from courses.permissions import IsOwnerOrNot
from courses.models import Course
from utils.mixins import *
from utils.utils import with_return_etag_to_headers
from exceptions.api_exceptions import RequestExceptionFieldError
from ..sql_querys.build_responses import me_response


class BaseViewset(viewsets.GenericViewSet, mixins.CreateModelMixin, PatchModelMixin, mixins.DestroyModelMixin):
    authentication_classes = (JWTCookieAuthentication,)

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [DRYObjectPermissions()]
        elif self.request.method in ["PUT"]:
            raise MethodNotAllowed("PUT")
        else:
            return [DRYPermissions()]


class ViewsetUserMe(BaseViewset):
    queryset = User.objects.all()
    serializer_class = SerializerUser

    def get(self, request, *args, **kwargs):
        headers = {
            "cache-control": "no-cache",
        }
        user = request.user
        with connection.cursor() as cursor:
            user = me_response.make_user_full(cursor, user.id)
        user = SerializerUserMeReadDict(user).data
        with_return_etag_to_headers(headers, user, request)

        return Response(user, headers=headers)


class ViewsetUserEnrollmentDBGet(BaseViewset):
    serializer_class = SerializerUserEnrollmentDB
    queryset = UserEnrollmentDB.objects.all()

    class ValidateIsUserEnrolled(serializers.Serializer):
        course_id = serializers.IntegerField()

    @action(detail=False, methods=["GET"], url_path="watch-list")
    def watch_list(self, request, *args, **kwargs):
        user = request.user
        course_id = request.query_params.get("course_id")
        user_enrollment_db = get_object_or_404(
            user.User_UserEnrollment.UserEnrollment_UserEnrollmentDB, course_id=course_id)
        watch_list = user_enrollment_db.watch_list
        watch_list = json.loads(watch_list)

        last_view = user_enrollment_db.last_view

        return Response({
            "data": {
                "watch_list": watch_list,
                "last_view": last_view
            },
            "more_data": {
                "course_id": course_id
            }
        })
