from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext as _

from .models import *


class UserAdmin(UserAdmin):
    ordering = ["-id"]
    list_display = ["id", "email", "first_name",
                    "last_name", ]
    search_fields = ["id"]

    fieldsets = (
        (None, {"fields": ["email", "password"]}),
        (_("personal info"), {"fields": [
         "first_name", "last_name", ]}),
        (
            _("Permissions"),
            {"fields": ["is_active", ]}
        ),
        (_("Important Dates"), {"fields": ["last_login"]}),
    )

    add_fieldsets = (
        (None, {
            "classes": ["wide"],
            "fields": ["email", "first_name", "last_name", "password1", "password2", ]
        }),
    )


admin.site.register(User,  UserAdmin)
