import os
import base64
import time
import json

from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth import get_user_model
from django.core import signing
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver

from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from django_rest_passwordreset.signals import reset_password_token_created

from courses_pro import types


def send_to_reset(email):
    try:
        user = get_user_model().objects.get(email=email)
    except get_user_model().DoesNotExist:
        raise NotFound


class GenSignCookie:
    def __init__(self, url, key_pair_id, key):
        self.key = key
        self.key_pair_id = key_pair_id
        self.url = url

        self.cookies = None

    def generate_signed_cookies(self):
        policy_json, policy_64 = self.generate_policy_cookie()
        signature = self.generate_signature(policy_json)
        self.cookies = self.generate_cookies(policy_64, signature)
        return self.cookies

    def generate_policy_cookie(self):
        """Returns a tuple: (policy json, policy base64)"""

        url = self.url

        policy_dict = {
            "Statement": [
                {
                    "Resource": url,
                    "Condition": {
                        "DateLessThan": {
                            "AWS:EpochTime": self._in_an_hour()
                        }
                    }
                }
            ]
        }

        # Using separators=(',', ':') removes seperator whitespace
        policy_json = json.dumps(policy_dict, separators=(",", ":"))
        policy_64 = str(base64.b64encode(policy_json.encode("utf-8")), "utf-8")
        policy_64 = self._replace_unsupported_chars(policy_64)
        print("policy_64", policy_64)
        return policy_json, policy_64

    def generate_signature(self, policy):
        """Creates a signature for the policy from the key, returning a string"""

        sig_bytes = self.rsa_signer(policy.encode("utf-8"))
        sig_64 = self._replace_unsupported_chars(
            str(base64.b64encode(sig_bytes), "utf-8"))
        return sig_64

    def generate_cookies(self, policy, signature):
        """Returns a dictionary for cookie values in the form 'COOKIE NAME': 'COOKIE VALUE'"""
        key_pair_id = self.key_pair_id

        return {
            "CloudFront-Policy": policy,
            "CloudFront-Signature": signature,
            "CloudFront-Key-Pair-Id": key_pair_id
        }

    def rsa_signer(self, message):
        """
        Based on https://boto3.readthedocs.io/en/latest/reference/services/cloudfront.html#examples
        """
        # key = self.key

        # private_key = serialization.load_pem_private_key(
        #     key,
        #     password=None,
        #     backend=default_backend()
        # )
        # signer = private_key.signer(padding.PKCS1v15(), hashes.SHA1())
        # signer.update(message)
        # return signer.finalize()

    @staticmethod
    def _replace_unsupported_chars(some_str):
        """Replace unsupported chars: '+=/' with '-_~'"""
        return some_str.replace("+", "-") \
            .replace("=", "_") \
            .replace("/", "~")

    @staticmethod
    def _in_an_hour():
        """Returns a UTC POSIX timestamp for one hour in the future"""
        return int(time.time()) + (60*60) * 60 * 60

    def make_response(self):
        cookies = self.cookies
        # cookies_list = [f"{key}={value}; Domain:.coursestar.net" for key, value in cookies.items()]
        cookies_list = [f"{key}={value}" for key, value in cookies.items()]
        print("cookies_list", cookies_list)
        return cookies_list

    # def generate_curl_cmd(self, url, cookies):
    #     """Generates a cURL command (use for testing)"""
    #     curl_cmd = "curl -v"
    #     for k, v in cookies.items():
    #         curl_cmd += " -H 'Cookie: {}={}'".format(k, v)
    #     # curl_cmd += " {}".format(url)
    #     new_url = "https://dns.coursestar.net/course_videos/None/name:חדשה-id:7875/נאומו-של-ח/360/tmp/0_output.ts"
    #     curl_cmd += f" {new_url}"
    #     return curl_cmd
