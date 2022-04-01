from rest_framework.exceptions import APIException
from rest_framework import status


class UserExceptionNoMoreCredit(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Yoy must have more credit to make more courses"
    default_code = 'error'
