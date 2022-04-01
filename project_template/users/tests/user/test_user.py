import json
import random
from unittest.mock import patch

from django.test import TestCase
from django.test import TestCase
from django.shortcuts import reverse
from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from django.test.client import encode_multipart

from rest_framework.test import APIClient
from rest_framework import status

import pytest
from faker import Faker

from helper.exceptions import RequestErrorNotProvideInfo
from users.serializers import *
from users.models import *
from my_types import urls

from users import defaults
from helper import helper
from helper.test.base_class import AbstractBaseTest

users_user = urls.users.get("user")


def to_path(path, id):
    return f"{path}{id}/"


# @pytest.mark.teclass
class BaseViewUser(AbstractBaseTest, TestCase):

    url = users_user

    patch = {
        "data": {"first_name": "yohai"},
        "path": "data.first_name",
        "res_data": "yohai"
    }
    create = {
        "data": {"first_name": "hello", },
    }

    def setUp(self):
        super().setUp()
        self.id = self.instructor.id

    def test_post_success(self):
        data = self.create.get("data")
        path = self.create.get("path")
        res_data = self.create.get("res_data")

        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_success(self):
        res = self.client.delete(to_path(self.url, self.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_response_delete(self):
        pass


@pytest.mark.teclass
class TestUserLogin(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_login_success(self):
        password = "123456789"
        self.instructor = helper.create_user(password=password)
        data = {
            "email": self.instructor.email,
            "password": password,
        }
        res = self.client.post(urls.users.get("auth/login"), data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_login_success_with_upper_email(self):
        password = "123456789Idd"
        self.instructor = helper.create_user(password=password)
        data = {
            "email": self.instructor.email.upper(),
            "password": password,
        }
        res = self.client.post(urls.users.get("auth/login"), data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = {
            "email": self.instructor.email,
            "password": password.upper(),
        }
        res = self.client.post(urls.users.get("auth/login"), data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_success(self):
        password1 = "123456789Idd"
        password2 = "123456789Idd"
        email = "exemple@gmail.com"
        first_name = "John"
        last_name = "Doe"

        data = {
            "email": email,
            "password1": password1,
            "password2": password2,
            "first_name": first_name,
            "last_name": last_name,
        }
        res = self.client.post(urls.users.get("auth/register"), data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_register_fail_password(self):
        password1 = "123456789Idd"
        password2 = "123456789Idd11"
        email = "exemple@gmail.com"
        first_name = "John"
        last_name = "Doe"

        data = {
            "email": email,
            "password1": password1,
            "password2": password2,
            "first_name": first_name,
            "last_name": last_name,
        }
        res = self.client.post(urls.users.get("auth/register"), data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_fail_2_users(self):
        password1 = "123456789Idd"
        password2 = "123456789Idd"
        email = "exemple@gmail.com"
        first_name = "John"
        last_name = "Doe"

        data = {
            "email": email,
            "password1": password1,
            "password2": password2,
            "first_name": first_name,
            "last_name": last_name,
        }
        res = self.client.post(urls.users.get("auth/register"), data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        res = self.client.post(urls.users.get("auth/register"), data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_fail_without_first_last_name(self):
        password1 = "123456789Idd"
        password2 = "123456789Idd"
        email = "exemple@gmail.com"

        data = {
            "email": email,
            "password1": password1,
            "password2": password2,
        }
        res = self.client.post(urls.users.get("auth/register"), data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_success(self):
        password = "123456789Idd"
        new_password = "newPassword123"
        self.instructor = helper.create_user(password=password)
        self.client.force_authenticate(user=self.instructor)

        data = {
            "email": self.instructor.email,
            "password": password,
        }
        res = self.client.post(urls.users.get("auth/login"), data)
        print("res.data", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = {
            "old_password": password,
            "new_password1": new_password,
            "new_password2": new_password,
        }
        res = self.client.post(urls.users.get("change-password"), data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = {
            "email": self.instructor.email,
            "password": password.upper(),
        }
        res = self.client.post(urls.users.get("auth/login"), data)
        print("res", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            "email": self.instructor.email,
            "password": new_password,
        }
        res = self.client.post(urls.users.get("auth/login"), data)
        print("res", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_change_password_fail(self):
        password = "123456789Idd"
        new_password = "newPassword123"
        self.instructor = helper.create_user(password=password)
        self.client.force_authenticate(user=self.instructor)

        data = {
            "email": self.instructor.email,
            "password": password,
        }
        res = self.client.post(urls.users.get("auth/login"), data)
        print("res.data", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = {
            "old_password": password,
            "new_password1": new_password,
            "new_password2": new_password.upper(),
        }
        res = self.client.post(urls.users.get("change-password"), data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_fail_unauthorized(self):
        password = "123456789Idd"
        new_password = "newPassword123"
        self.instructor = helper.create_user(password=password)
        data = {
            "old_password": password,
            "new_password1": new_password,
            "new_password2": new_password,
        }
        res = self.client.post(urls.users.get("change-password"), data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
