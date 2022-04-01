from rest_framework.decorators import action
from rest_framework import viewsets,  status

from dj_rest_auth.utils import jwt_encode
from dj_rest_auth.views import LoginView, PasswordChangeView
from django_rest_passwordreset.views import ResetPasswordConfirm
from django_auto_prefetching import AutoPrefetchViewSetMixin
from dj_rql.drf import RQLFilterBackend

from ..models import *
from ..filters import *
from ..serializers.read_serializers import *
from ..serializers.write_serializers import *
from {{project_name}}.utils import Response


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
