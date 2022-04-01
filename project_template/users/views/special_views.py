import json
from time import sleep
from django.utils import timezone


from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.db import connection

from rest_framework import viewsets,  status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.decorators import api_view, authentication_classes, permission_classes, action
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView

from django_rest_passwordreset.views import ResetPasswordConfirm as ResetPasswordConfirmOrginal, ResetPasswordRequestToken
from dj_rest_auth.jwt_auth import JWTCookieAuthentication
from dj_rest_auth.views import LoginView as LoginViewOrginal, PasswordChangeView as PasswordChangeViewOrginal
from dj_rest_auth.utils import jwt_encode
from django_rest_passwordreset.signals import reset_password_token_created
from zappa.asynchronous import task

from users.models import TOTPDevice

from ..serializers.get_serializers import *
from ..serializers.write_serializers import *
from ..serializers.special_serializers import *
from ..models import *
from ..permissions import *
from courses.permissions import IsOwnerOrNot
from courses.models import Course
from utils.mixins import *
from exceptions.api_exceptions import RequestExceptionFieldError
from ..sql_querys.build_responses import me_response
from ..views.base_views import BaseViewset
# from utils.utils import run_in_lambda


from courses_pro import types


class ResetPasswordConfirm(ResetPasswordConfirmOrginal):
    def post(self, request, *args, **kwargs):
        res = super().post(request, *args, **kwargs)
        return res


class PasswordChangeView(PasswordChangeViewOrginal):
    pass


class LoginView(LoginViewOrginal):

    def set_jwt_access_cookie(self, response, access_token):
        from rest_framework_simplejwt.settings import api_settings as jwt_settings
        cookie_name = getattr(settings, 'JWT_AUTH_COOKIE', None)
        access_token_expiration = (
            timezone.now() + jwt_settings.ACCESS_TOKEN_LIFETIME)
        cookie_secure = getattr(settings, 'JWT_AUTH_SECURE', False)
        cookie_httponly = getattr(settings, 'JWT_AUTH_HTTPONLY', True)
        cookie_samesite = getattr(settings, 'JWT_AUTH_SAMESITE', 'Lax')
        cookie_domin = getattr(settings, 'JWT_AUTH_DOMAIN', None)

        if cookie_name and not cookie_domin:
            response.set_cookie(
                cookie_name,
                access_token,
                expires=access_token_expiration,
                secure=cookie_secure,
                httponly=cookie_httponly,
                samesite=cookie_samesite,
            )
        if cookie_name and cookie_domin:
            response.set_cookie(
                cookie_name,
                access_token,
                expires=access_token_expiration,
                secure=cookie_secure,
                httponly=cookie_httponly,
                samesite=cookie_samesite,
                domain=cookie_domin
            )

    def get_response(self):
        orginal_response = super().get_response()
        response = orginal_response.data
        user = self.request.user
        devices = user.totpdevice_set.all()

        mfa_code = self.request.data.get('mfa_code')

        for device in devices:
            if device.confirmed:
                result = device.verify_token(mfa_code)
                if not result:
                    raise APIException('could not perform action')

        with connection.cursor() as cursor:
            user_data = me_response.make_user_full(cursor, user.id)
        user_data = SerializerUserMeReadDict(user_data).data

        response["user"] = user_data
        # token = response["token"]
        # orginal_response.headers['Set-Cookie'] = f"Authorization=JWT {token}"
        access = response["access_token"]
        print("access", access)
        self.set_jwt_access_cookie(orginal_response,  access)
        return orginal_response


class ViewsetTOTPDevice(BaseViewset):
    queryset = TOTPDevice.objects.all()
    serializer_class = SerializerTOTPDevice


class ViewsetUserContact(BaseViewset):
    queryset = UserContact.objects.all()
    serializer_class = SerializerUserContact


class ViewsetAuth(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = SerializerRegister

    @action(detail=False, methods=["POST"], url_path="register")
    def register(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        with connection.cursor() as cursor:
            user_data = me_response.make_user_full(cursor, user.id)
        user_data = SerializerUserMeReadDict(user_data).data
        access_token,  refresh_token = jwt_encode(user)

        return Response({
            "user": user_data,
            "access_token": str(access_token),
            "refresh_token": str(refresh_token),
        }, status=status.HTTP_201_CREATED)


@task
def set_run(email, key):
    url = f"{types.MAIN_HOST}/login/#new&token={key}"
    subject = 'Email Reset Password'
    from_email = 'no-reply@coursestar.net'
    to = email

    text_content = f'אתה מקבל את המייל הזה כיון ששלחת בקשה לאיפוס הסיסמא\n {url}'
    html_content = f"""
    <p>אתה מקבל את המייל הזה כיון ששלחת בקשה לאיפוס הסיסמא</p>
    <p><strong>{url}</strong></p>
    """
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    email = reset_password_token.user.email
    key = reset_password_token.key
    if not check_stage() == "TEST":
        set_run(email, key)
