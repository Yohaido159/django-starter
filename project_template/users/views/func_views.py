import json
import requests

from django.db import connection
from django.db.models import Prefetch
from django.core import signing
from django_otp.models import SideChannelDevice
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.urls import reverse_lazy
from django.conf import settings

from rest_framework import viewsets, mixins, status
from dj_rest_auth.jwt_auth import JWTCookieAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.exceptions import APIException, ValidationError

from django_rest_passwordreset.views import ResetPasswordConfirm as ResetPasswordConfirmOrginal, ResetPasswordRequestToken

from ..serializers import *
from ..models import *
from ..permissions import *
from courses.permissions import IsOwnerOrNot
from courses.models import Course
from utils.mixins import *
from exceptions.api_exceptions import RequestExceptionFieldError
from ..sql_querys.build_responses import me_response
from ..views.special_views import LoginView


@permission_classes([])
@api_view(["post"])
def check_user_mfa(request, *args, **kwargs):
    email = request.data.get('email')
    is_login = request.data.get('is_login')
    if not email:
        raise RequestExceptionFieldError("email")

    has_mfa = get_user_model().objects.filter(email=email, totpdevice__isnull=False).exists()
    print("has_mfa", has_mfa)
    is_confirmed = get_user_model().objects.filter(email=email, totpdevice__isnull=False, totpdevice__confirmed=True).exists()

    # if not is_confirmed and is_login:
    #     pass
    #     HOSTNAME = settings.HOSTNAME
    #     url = f"{HOSTNAME}{reverse_lazy('users:custom_login_view')}"
    #     res = requests.post(url, request.data)
    #     if res.status_code >= 400:
    #         raise ValidationError(res.json())
    #     return Response({"more_data": {"has_mfa": has_mfa, "is_confirmed": is_confirmed, "is_logged": True}, "data": res.json()})

    # return Response({"more_data": {"has_mfa": has_mfa, "is_confirmed": is_confirmed, "is_logged": False}})
    return Response({"more_data": {"has_mfa": has_mfa, "is_confirmed": is_confirmed}})
