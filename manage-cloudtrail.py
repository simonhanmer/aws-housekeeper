"""
manage-cloudtrail.py
"""

from __future__ import print_function

import boto3
import pytz
from datetime import datetime, timedelta

def lambda_handler(event, context):

    cloudtrail = boto3.client('cloudtrail')

    retainDays = 10
    cutoff = datetime.now().replace(tzinfo=pytz.utc) - timedelta(retainDays)
    print(cutoff.strftime("%y%m%d"))

    for trail in cloudtrail.describe_trails()['trailList']:
        process_logs(trail, cutoff)

def process_logs(trail, cutoff):
    bucket = trail['S3BucketName']
    prefix = trail['S3KeyPrefix']
    print(bucket + "/" + prefix)

    s3 = boto3.client('s3')

    paginator = s3.get_paginator('list_objects')

    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for object in page['Contents']:
            if object['LastModified'] < cutoff:
                s3.delete_object(Bucket=bucket, Key=object['Key'])

    