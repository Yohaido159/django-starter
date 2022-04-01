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

users_user_metadata = urls.users.get("user-metadata")


def to_path(path, id):
    return f"{path}{id}/"


# @pytest.mark.teclass
class BaseViewUserMetadata(AbstractBaseTest, TestCase):

    url = users_user_metadata

    patch = {
        "data": {"last_view_courses": json.dumps([{"id": "2"}])},
        "path": "data.last_view_courses",
        "res_data": [{"id": "2"}]
    }
    create = {
        "data": {"first_name": "hello", },
    }

    def setUp(self):
        super().setUp()
        user_metadata = self.instructor.User_UserMetadata
        self.id = user_metadata.id

    def test_post_success(self):
        data = self.create.get("data")
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_success(self):
        data = self.create.get("data")
        res = self.client.delete(to_path(self.url, self.id), data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_response_delete(self):
        pass
