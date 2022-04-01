import serpy
from rest_framework import viewsets

from ..models import *
from ..serializers.write_serializers import *
from ..serializers.read_serializers import *


class ModelViewset(viewsets.ModelViewSet):
    queryset = Model.objects.all()
    serializer_class = Serializer
    lookup_field = 'id'

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
