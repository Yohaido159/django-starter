import serpy

from ..models import *


class UserReadSerializer(serpy.Serializer):
    id = serpy.Field()
    email = serpy.Field()
    first_name = serpy.Field()
    last_name = serpy.Field()
