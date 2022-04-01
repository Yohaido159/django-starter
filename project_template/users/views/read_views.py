import serpy
from rest_framework import viewsets

from ..models import *
from ..serializers.write_serializers import *
from ..serializers.read_serializers import *


class ModelViewSet(viewsets.ModelViewSet):
    queryset = Model.objects.all()
    serializer_class = Serializer
    lookup_field = 'id'
