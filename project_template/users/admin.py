from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _
# from admin_auto_filters.filters import AutocompleteFilter, AutocompleteSelect

from .models import *
# from django_json_widget.widgets import JSONEditorWidget


class UserAdmin(BaseUserAdmin):
    ordering = ["-id"]
    list_display = ["id", "email", "first_name",
                    "last_name", "is_instructor", "how_couse_he_can"]
    # list_display = ["id", "email", "first_name", "last_name", "image", "image_big", "is_instructor"]
    search_fields = ["id"]

    fieldsets = (
        (None, {"fields": ["email", "password"]}),
        (_("personal info"), {"fields": [
         "first_name", "last_name", "image", "image_big"]}),
        (
            _("Permissions"),
            {"fields": ["is_active", "is_instructor", "how_couse_he_can"]}
        ),
        (_("Important Dates"), {"fields": ["last_login"]}),
        (_("Courses"), {"fields": ["short_description", ]}),
    )

    add_fieldsets = (
        (None, {
            "classes": ["wide"],
            "fields": ["email", "first_name", "last_name", "password1", "password2", ]
        }),
    )


admin.site.register(User,  UserAdmin)
