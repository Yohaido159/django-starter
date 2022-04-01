from django.contrib.auth import get_user_model

from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer

from ..models import *
from ..serializers.read_serializers import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


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


class UserLoginSerializer(LoginSerializer):
    email = EmailFieldLower(required=True)
