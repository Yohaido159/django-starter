import serpy
from rest_framework import serializers

from ..models import *


class ModelRead(serpy.Serializer):
    id = serpy.Field()
    name = serpy.Field()
    description = serpy.Field()
    created_at = serpy.Field()
    updated_at = serpy.Field()
