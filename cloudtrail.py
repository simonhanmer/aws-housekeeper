from __future__ import print_function

import boto3
import pytz
import os
from datetime import datetime, timedelta

def lambda_handler(event, context):

    retainDays = 90

    # See if we have a retention env. var
    if os.environ.has_key('RETAINDAYS'):
        if int(os.environ['RETAINDAYS']) > 0:
            retainDays = int(os.environ['RETAINDAYS'])
    
    cloudtrail = boto3.client('cloudtrail')

    cutoff = datetime.now().replace(tzinfo=pytz.utc) - timedelta(retainDays)

    # Get list of cloudtrails
    for trail in cloudtrail.describe_trails()['trailList']:
        process_logs(trail, cutoff)


def process_logs(trail, cutoff):
    bucket = trail['S3BucketName']
    prefix = trail['S3KeyPrefix']

    oldObjects = []

    s3 = boto3.client('s3')

    paginator = s3.get_paginator('list_objects')

    # Get list of S3 objects. If they are older than retain_days, add
    # the object name to oldObjects

    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for object in page['Contents']:
            if object['LastModified'] < cutoff:
                oldObjects.append({ 'Key' : object['Key']})

    # We can only delete 1000 items at a time with s3.delete_objects, so
    # iterate over oldObjects grabbing that many items at a time and send
    # the list to delete_objects
    items = 1000

    print("Deleting " + str(len(oldObjects)) + " objects from " + bucket + "/" + prefix)

    while len(oldObjects) > 0:
        actionObjects=oldObjects[:items]
        del oldObjects[:items]
        response = s3.delete_objects(Bucket=bucket, Delete={ "Objects" : actionObjects} )



