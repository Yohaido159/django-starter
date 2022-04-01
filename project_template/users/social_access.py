from django.urls import reverse

from rest_framework.viewsets import ViewSet
from rest_framework.views import APIView

from allauth.utils import build_absolute_uri
from allauth.account.views import ConfirmEmailView
from allauth.account.utils import perform_login

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter

from dj_rest_auth.registration.serializers import (
    SocialConnectSerializer,
)
from dj_rest_auth.registration.views import VerifyEmailView as VerifyEmailViewOrginal, RegisterView


from rest_framework.response import Response
from dj_rest_auth.registration.views import SocialLoginView, SocialConnectView
from .models import UserEnrollment, UserMetadata, User
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


from dj_rest_auth.views import PasswordResetView
import threading


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        url = reverse("users:account_confirm_email", args=[emailconfirmation.key])
        ret = build_absolute_uri(request, url)
        return ret


class CustomAccountAdapterSocial(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        user = sociallogin.user
        if user.id:
            return
        try:
            user = User.objects.get(email=user.email)
            sociallogin.state['process'] = 'connect'
            perform_login(request, user, 'none')
        except User.DoesNotExist:
            pass


class GoogleLoginConnect(SocialConnectView):
    adapter_class = GoogleOAuth2Adapter
    permission_classes = []
    authentication_classes = []
    client_class = OAuth2Client


class VerifyEmailView(VerifyEmailViewOrginal):
    def get(self,  *args, **kwargs):
        confirmation = self.get_object()
        confirmation.confirm(self.request)
        return Response({'detail': 'ok'}, status=200)
