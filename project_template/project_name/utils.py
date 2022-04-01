import serpy
from rest_framework.response import Response


class Response(Response):
    def __init__(self, *, more_data=dict(), **kwargs):
        super().__init__(**kwargs)
        self.res_dict = {}
        self.res_dict['more_data'] = more_data
        self.res_dict['data'] = self.data
        self.data = self.res_dict


class NestedField(serpy.Field):
    def __init__(self,  nested=None, many=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nested = nested
        self.many = many

    def to_value(self, value):
        if self.many:
            res = self.nested(value.all(), many=self.many).data
        else:
            res = self.nested(value, many=self.many).data
        return res
