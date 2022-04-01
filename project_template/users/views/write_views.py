from django.contrib.auth import get_user_model

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets,  status

from dj_rest_auth.utils import jwt_encode
from dj_rest_auth.views import LoginView, PasswordChangeView
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from django_rest_passwordreset.views import ResetPasswordConfirm
from django_auto_prefetching import AutoPrefetchViewSetMixin
from dj_rql.drf import RQLFilterBackend

from ..models import *
from ..filters import *
from ..serializers.read_serializers import *
from ..serializers.write_serializers import *


class EmailFieldLower(serializers.EmailField):
    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        return value.lower()


class SerializerRegister(RegisterSerializer):
    password2 = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)
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
            raise serializers.ValidationError(
                {'password': 'Passwords must match.'})
        user.set_password(password1)
        user.save()
        return user


class SerializerUserLogin(LoginSerializer):
    email = EmailFieldLower(required=True)


class UserViewset(AutoPrefetchViewSetMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (RQLFilterBackend,)
    rql_filter_class = UserFilterClass

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = UserReadSerializer(queryset, many=True)
        return Response(data=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = UserReadSerializer(queryset, many=True)
        return Response(data=serializer.data)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs


class ResetPasswordConfirm(ResetPasswordConfirm):
    def post(self, request, *args, **kwargs):
        res = super().post(request, *args, **kwargs)
        return res


class PasswordChangeView(PasswordChangeView):
    pass


class LoginView(LoginView):

    def get_response(self):
        orginal_response = super().get_response()
        response = orginal_response.data
        user = self.request.user

        user_data = UserReadSerializer(user).data

        response["user"] = user_data
        return response


class ViewsetAuth(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = SerializerRegister

    @action(detail=False, methods=["POST"], url_path="register")
    def register(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user_data = UserReadSerializer(user).data
        access_token,  refresh_token = jwt_encode(user)

        return Response({
            "user": user_data,
            "access_token": str(access_token),
            "refresh_token": str(refresh_token),
        }, status=status.HTTP_201_CREATED)
