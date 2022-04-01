import operator
from functools import reduce
import json

from django.db import connection
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from django.core import signing
from django.core.mail import EmailMultiAlternatives
from django_otp.models import SideChannelDevice
from django.contrib.auth import get_user_model
from django.db.models import Q

from rest_framework import viewsets, mixins, status
from dj_rest_auth.jwt_auth import JWTCookieAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.decorators import api_view, authentication_classes, permission_classes, action
from rest_framework.exceptions import APIException, MethodNotAllowed

from django_rest_passwordreset.views import ResetPasswordConfirm as ResetPasswordConfirmOrginal, ResetPasswordRequestToken
from dry_rest_permissions.generics import DRYPermissions, DRYObjectPermissions

from permissions.base_permissions import DRYObjectPermissionsCustom, DRYPermissionsCustom
from .get_views import *
from ..serializers.get_serializers import *
from ..serializers.write_serializers import *
from ..serializers.special_serializers import *
from ..models import *
from ..permissions import *
from courses.permissions import IsOwnerOrNot
from courses.models import Course
from utils.mixins import *
from payments.braintree.gateway import BrainTreeClient
from exceptions.api_exceptions import RequestExceptionFieldError
from ..sql_querys.build_responses import me_response


class BaseViewset(viewsets.GenericViewSet, mixins.CreateModelMixin, PatchModelMixin, mixins.DestroyModelMixin):
    authentication_classes = (JWTCookieAuthentication,)
    # permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [DRYObjectPermissions()]
        elif self.request.method in ["PUT"]:
            raise MethodNotAllowed("PUT")
        else:
            return [DRYPermissions()]


class ViewsetUser(BaseViewset):
    serializer_class = SerializerUser
    queryset = User.objects.all()

    class ValidateSendMail(serializers.Serializer):
        email_obj = serializers.DictField(required=True)

    @action(detail=False, methods=["POST"], url_path="update-user-payment")
    def update_user_payment(self, request, *args, **kwargs):
        user = request.user
        result = BrainTreeClient().customers.update_customer(request)
        return Response(data={"data": {"is_instructor": user.is_instructor, "result": result.is_success}})

    @action(detail=False, methods=["POST"], url_path="send-mail-to-users")
    def send_mail_to_users(self, request, *args, **kwargs):
        self.ValidateSendMail(data=request.data).is_valid(raise_exception=True)
        email_obj = request.data.get('email_obj')
        emails = send_email_to_users(email_obj)
        return Response({"message": "Email sent Successfully", "emails": emails})


def replace_content(html, courses_ids):
    courses_detail = []
    for idx, course_id in enumerate(courses_ids):
        idx += 1
        course = Course.objects.get(id=course_id)
        courses_detail.append({
            f"\u007b{{course_{idx}_title}}\u007d": course.name,
            f"\u007b{{course_{idx}_desc}}\u007d": course.description_short,
            f"\u007b{{course_{idx}_image}}\u007d": course.image,
            f"\u007b{{course_{idx}_url}}\u007d": f"https://www.coursestar.net/course/{course.name_slug}",
        })

    for course in courses_detail:
        for key, value in course.items():
            html = html.replace(key, value)

    return html


@task
def send_email_to_users(email_obj, user_id):
    from_email = 'contact@coursestar.net'

    courses_ids = email_obj.get('courses_ids')
    title = email_obj.get('title')
    html_content = email_obj.get('html')
    user = User.objects.get(id=user_id)
    html_content = replace_content(html_content, courses_ids)
    html_content = html_content.replace("{{first_name}}", user.name)
    msg = EmailMultiAlternatives(title, "", from_email,  to=[user.email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


class ViewsetUserContact(BaseViewset):
    serializer_class = SerializerUserContact
    queryset = UserContact.objects.all()

    class ValidateSendMail(serializers.Serializer):
        title = serializers.CharField()
        html = serializers.CharField()

    @action(detail=False, methods=["POST"], url_path="send-mail-to-contact")
    def send_mail_to_contact(self, request, *args, **kwargs):
        self.ValidateSendMail(data=request.data).is_valid(raise_exception=True)
        user = request.user
        title = request.data.get('title')
        html = request.data.get('html')
        html = html

        run_send_mail_to_contact(user.id, title, html)
        return Response({"message": "Email sent Successfully"})


class ViewsetRequestInstructor(BaseViewset):
    serializer_class = SerializerRequestInstructor
    queryset = RequestInstructor.objects.all()


@task(remote_aws_lambda_function_name="django-dev")
# @task
def run_send_mail_to_contact(user_id, title, html):
    user = User.objects.get(id=user_id)
    UserContact.objects.create(user=user, title=title, html=html)

    subject = f' מאת:{user.name} | {title}'
    from_email = 'contact@coursestar.net'
    to = ["the.course.il@gmail.com"]
    html += f"""
        <p> 
        user_detail:<br/>
        id:  {user.id} <br/>
        name: {user.name} <br/>
        email: {user.email} <br/>
        </p> 
    """
    html_content = html

    msg = EmailMultiAlternatives(subject, "", from_email,  bcc=to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()


class ViewsetUserEnrollment(BaseViewset):
    serializer_class = SerializerUserEnrollment
    queryset = UserEnrollment.objects.all()


class ViewsetUserEnrollmentDB(BaseViewset):
    serializer_class = SerializerUserEnrollmentDB
    queryset = UserEnrollmentDB.objects.all()

    class ValidateIsUserEnrolled(serializers.Serializer):
        course_id = serializers.IntegerField()

    @action(detail=False, methods=["POST", "GET"], url_path="check-if-user-enrolled")
    def check_if_user_enrolled(self, request, *args, **kwargs):
        self.ValidateIsUserEnrolled(data=request.data).is_valid(raise_exception=True)
        user = request.user
        print("user", user)
        course_id = request.data.get('course_id')
        is_user_enrollment_db_exists = UserEnrollmentDB.objects.filter(user__user=user, course_id=course_id).exists()
        return Response({"more_data": {
            "is_enroll": is_user_enrollment_db_exists
        }})


class ViewsetUserMetadata(BaseViewset):
    serializer_class = SerializerUserMetadata
    queryset = UserMetadata.objects.all()
