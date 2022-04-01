import json
import boto3
import os

# from celery import shared_task


# @shared_task
# def send_email_task(userEmail, courseId):
#     ses = boto3.client("ses", aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
#                        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"), verify=False, region_name="us-east-1"
#                        )

#     response = ses.send_email(
#         Destination={
#             'ToAddresses': ['the.course.il@gmail.com'],
#         },
#         Message={
#             'Body': {
#                 'Text': {
#                     'Charset': 'UTF-8',
#                     'Data': f'{userEmail} want to active the course with {courseId} id url: https: // localhost: 3000/course/{courseId}',
#                 },
#             },
#             'Subject': {
#                 'Charset': 'UTF-8',
#                 'Data': f'Active Course id {userEmail} / {courseId}',
#             },
#         },
#         Source='yohaido159@gmail.com',
#     )
