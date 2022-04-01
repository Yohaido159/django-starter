import re
import boto3
import base64
import time
import json
from pprint import pprint

from rest_framework.decorators import api_view
from rest_framework.response import Response

from zappa.asynchronous import task


s3_client = boto3.client("s3")
bucket = "coursestar-deps"


def run_get_signed_cookie():
    key_pem = s3_client.get_object(
        Bucket=bucket, Key="secret_pem/cloudfront.pem")["Body"].read()

    url = "https://dns.coursestar.net/course_videos/None/name:%D7%97%D7%93%D7%A9%D7%94-id:7875/%D7%A0%D7%90%D7%95%D7%9E%D7%95-%D7%A9%D7%9C-%D7%97/360/tmp/0_output.ts"
    id = "E1HODZHEJI3DQL"
    cookies = generate_signed_cookies(url, id, key_pem)

    # pprint(generate_curl_cmd(url, cookies))
    ret = generate_curl_cmd(url, cookies)
    return Response(ret)


@api_view(["GET"])
def gen_signed_cookie(request):
    return run_get_signed_cookie()


def _replace_unsupported_chars(some_str):
    """Replace unsupported chars: '+=/' with '-_~'"""
    return some_str.replace("+", "-") \
        .replace("=", "_") \
        .replace("/", "~")


def _in_an_hour():
    """Returns a UTC POSIX timestamp for one hour in the future"""
    return int(time.time()) + (60*60)


def rsa_signer(message, key):
    """
    Based on https://boto3.readthedocs.io/en/latest/reference/services/cloudfront.html#examples
    """
    # private_key = serialization.load_pem_private_key(
    #     key,
    #     password=None,
    #     backend=default_backend()
    # )
    # signer = private_key.signer(padding.PKCS1v15(), hashes.SHA1())
    # signer.update(message)
    # return signer.finalize()


def generate_policy_cookie(url):
    """Returns a tuple: (policy json, policy base64)"""

    policy_dict = {
        "Statement": [
            {
                "Resource": url,
                "Condition": {
                    "DateLessThan": {
                        "AWS:EpochTime": _in_an_hour()
                    }
                }
            }
        ]
    }

    # Using separators=(',', ':') removes seperator whitespace
    policy_json = json.dumps(policy_dict, separators=(",", ":"))
    policy_64 = str(base64.b64encode(policy_json.encode("utf-8")), "utf-8")
    policy_64 = _replace_unsupported_chars(policy_64)
    return policy_json, policy_64


def generate_signature(policy, key):
    """Creates a signature for the policy from the key, returning a string"""
    sig_bytes = rsa_signer(policy.encode("utf-8"), key)
    sig_bytes = re.sub(br"[\n\t\s]*", b"", sig_bytes)
    print("sig_bytes", sig_bytes)
    sig_64 = _replace_unsupported_chars(
        str(base64.b64encode(sig_bytes), "utf-8"))
    return sig_64


def generate_cookies(policy, signature, cloudfront_id):
    """Returns a dictionary for cookie values in the form 'COOKIE NAME': 'COOKIE VALUE'"""
    return {
        "CloudFront-Policy": policy,
        "CloudFront-Signature": signature,
        "CloudFront-Key-Pair-Id": cloudfront_id
    }


def generate_curl_cmd(url, cookies):
    """Generates a cURL command (use for testing)"""
    curl_cmd = "curl -v"
    for k, v in cookies.items():
        curl_cmd += " -H 'Cookie: {}={}'".format(k, v)
    curl_cmd += " {}".format(url)
    return curl_cmd


def generate_signed_cookies(url, cloudfront_id, key):
    policy_json, policy_64 = generate_policy_cookie(url)
    signature = generate_signature(policy_json, key)
    return generate_cookies(policy_64, signature, cloudfront_id)
