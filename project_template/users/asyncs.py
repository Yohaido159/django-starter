import boto3
import base64

import time
import json
from pprint import pprint

from rest_framework.decorators import api_view, authentication_classes, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from zappa.asynchronous import task
from dj_rest_auth.jwt_auth import JWTCookieAuthentication

from .utils import GenSignCookie
from utils.utils import remove_brackets_from_list, remove_quotes_regex

s3_client = boto3.client("s3")
bucket = "coursestar-deps"


def run_get_signed_cookie(user, course_id):
    key_pem = s3_client.get_object(
        Bucket=bucket, Key="secret_pem/cloudfront1.pem")["Body"].read()

    url = "http*://dns.coursestar.net/course_videos/*"
    id = "KNLOJIMFDOJ4D"

    genCookie = GenSignCookie(key_pair_id=id, key=key_pem, url=url)
    cookies = genCookie.generate_signed_cookies()
    cookies_list = genCookie.make_response()
    # user_enrollment_db = user.User_UserEnrollment.UserEnrollment_UserEnrollmentDB.get(course_id=course_id)

    # cookies_list = [f"{key}={value}; Path=/" for key, value in cookies.items()]
    # cookies_string = ", ".join(cookies_list)
    # print("cookies_string", cookies_string)
    # user_enrollment_db.cookie = cookies_string

    # # user_enrollment_db.cookie = f"[{remove_quotes_regex(remove_brackets_from_list(json.dumps(cookies_list)))}]"
    # user_enrollment_db.save(update_fields=["cookie"])
    # cookie = user_enrollment_db.cookie
    ret = cookies_list
    return Response(ret)


@ api_view(["GET"])
# @ authentication_classes([JWTCookieAuthentication])
# @ permission_classes([IsAuthenticated])
def gen_signed_cookie(request):
    user = request.user
    return run_get_signed_cookie(user, 7)
