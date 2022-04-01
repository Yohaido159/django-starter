from rest_framework import viewsets

from django_auto_prefetching import AutoPrefetchViewSetMixin
import serpy


from ..models import *
from ..filters import *
from ..serializers.write_serializers import *
from ..serializers.read_serializers import *
