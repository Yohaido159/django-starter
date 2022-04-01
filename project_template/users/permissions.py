from rest_framework.permissions import BasePermission
from .models import UserEnrollmentDB


class IsBuyTheCourse(BasePermission):
    message = "You not the owner of this course"

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, UserEnrollmentDB):
            user = obj.user.user.id
            if user == request.user.id:
                return True
            else:
                return False


# class CheckTheUser(AccessPolicy):
#     statements = [{
#         "action": ["*"],
#         "effect": "allow",
#         "principal": ["authenticated"],
#         # "condition": [""]
#     }]
