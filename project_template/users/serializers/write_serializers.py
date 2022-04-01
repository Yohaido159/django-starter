from rest_framework import serializers

from ..models import *
from ..serializers.read_serializers import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
