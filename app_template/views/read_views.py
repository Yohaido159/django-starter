import serpy
from rest_framework import viewsets

from ..models import *
from ..serializers.write_serializers import *
from ..serializers.read_serializers import *
from {{project_name}}.utils import Response
