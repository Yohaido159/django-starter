from dj_rql.filter_cls import RQLFilterClass

from .models import *


class UserFilterClass(RQLFilterClass):
    MODEL = User
    FILTERS = ['email', 'first_name', 'last_name']
