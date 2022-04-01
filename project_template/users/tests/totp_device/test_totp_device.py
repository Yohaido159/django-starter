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
from utils.utils import deep_get
from users import defaults
from helper import helper
from helper.test.base_class import AbstractBaseTest

users_totp_device = urls.users.get("totp-device")


def to_path(path, id):
    return f"{path}{id}/"


# @pytest.mark.teclass
class BaseViewTOTPDevice(AbstractBaseTest, TestCase):

    url = users_totp_device

    patch = {
    }
    create = {
        "data": {"name": "MyDeviceMFANew", },
        "path": "data.name",
        "res_data": "MyDeviceMFANew"
    }

    def setUp(self):
        super().setUp()
        totp_device = helper.create_totp_device(self.instructor)
        self.id = totp_device.id

    def test_post_success(self):
        data = self.create.get("data")
        TOTPDevice.objects.filter(user=self.instructor).delete()
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_post_success_2(self):
        data = self.create.get("data")
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_success(self):
        data = self.patch.get("data")
        res = self.client.patch(to_path(self.url, self.id), data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_response_delete(self):
        pass

    def test_delete_success(self):
        res = self.client.delete(to_path(self.url, self.id))
        # print("self.url", self.url)
        # print("res.data", res.data)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
