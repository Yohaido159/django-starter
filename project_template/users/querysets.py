from django.db.models import QuerySet, Count, Sum, Case, When
from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.apps import apps
from django.db.models import Value, Count, F, Q
from django.db.models.functions import Concat, Substr


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **kwargs):
        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **kwargs):
        user = self.create_user(email, password, **kwargs)
        user.is_staff = True
        user.is_superuser = True
        user.is_instructor = True
        user.save(using=self._db)
        return user

    def get_custom_qs(self):
        model = apps.get_model("users", "User")
        return UserQueryset(model)


class UserQueryset(QuerySet):
    def with_first_and_last(self):
        queryset = self.annotate(
            first_and_last=Concat(Substr("first_name", 1, 1), Substr("last_name", 1, 1))
        )
        return queryset

    def with_num_total_users(self, user_email):
        with_num_total_users = self.filter(email=user_email).annotate(num_total_users=Count(
            "User_Course__Course_UserEnrollment"
        ))
        return with_num_total_users

    def users_with_courses(self, **kwargs):
        if "id" not in kwargs:
            users_with_courses = self.filter(is_instructor=True, **kwargs).annotate(
                num_courses=Case(
                    When(
                        User_Course__is_active=True,
                        then=Count("User_Course"),
                    ),
                    output_field=models.IntegerField()
                )
            ).filter(num_courses__gt=0)

        elif "id" in kwargs:
            num_courses = self.filter(is_instructor=True, **kwargs).aggregate(
                num_courses=Count(
                    "User_Course", filter=Q(User_Course__is_active=True)
                )
            )
            users_with_courses = self.filter(is_instructor=True, **kwargs).annotate(
                num_courses=Value(num_courses.get("num_courses"), output_field=models.IntegerField())
            )

        return users_with_courses

    def with_num_courses_buy(self, id):
        num_courses_buy = self.filter(id=id).aggregate(
            Count("User_Course__Course_UserEnrollment")
            # Count("User_UserEnrollment__User_UserEnrollmentDB")
        )

        return num_courses_buy.get("User_Course__Course_UserEnrollment__count")

    def with_num_courses_create(self, id):
        num_courses_create = self.filter(id=id).aggregate(
            Count("User_Course")
        )
        return num_courses_create.get("User_Course__count")


class UserEnrollmentDBQueryset(QuerySet):
    def get_queryset(self):
        return self.select_related("user__user", "course")

    def with_first_and_last(self):
        queryset = self.annotate(
            first_and_last=Concat(Substr("user__user__first_name", 1, 1), Substr("user__user__last_name", 1, 1))
        )
        return queryset


class UserEnrollmentQueryset(models.Manager):
    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        qs = qs.select_related("user")
        return qs
