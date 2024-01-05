#!/usr/bin/env python3

# -*-coding:utf-8 -*-

import boto3  # REQUIRED! - Details here: https://pypi.org/project/boto3/
from botocore.exceptions import ClientError
from botocore.config import Config
from dotenv import load_dotenv  # Project Must install Python Package:  python-dotenv
import os
import sys

BUCKET_NAME = 'lit-apps'

LOCAL_DIR = '/Users/litritt/Ignited-Source/bucket'  # <-- Make sure this directory exists on your local machine; adjust name per your operating system

WEEK_IN_SECONDS = 604800

# Delete the specified objects from B2
def delete_files(bucket, keys, b2):
    objects = []
    for key in keys:
        objects.append({'Key': key})
    try:
        b2.Bucket(bucket).delete_objects(Delete={'Objects': objects})
    except ClientError as ce:
        print('error', ce)


# Delete the specified object from B2 - all versions
def delete_files_all_versions(bucket, keys, client):
    objects = []
    for key in keys:
        objects.append({'Key': key})
    try:
        # SOURCE re LOGIC FOLLOWING:  https://stackoverflow.com/questions/46819590/delete-all-versions-of-an-object-in-s3-using-python
        paginator = client.get_paginator('list_object_versions')
        response_iterator = paginator.paginate(Bucket=bucket)
        for response in response_iterator:
            versions = response.get('Versions', [])
            versions.extend(response.get('DeleteMarkers', []))
            for version_id in [x['VersionId'] for x in versions
                               if x['Key'] == key and x['VersionId'] != 'null']:
                print('Deleting {} version {}'.format(key, version_id))
                client.delete_object(Bucket=bucket, Key=key, VersionId=version_id)

    except ClientError as ce:
        print('error', ce)

# Download the specified object from B2 and write to local file system
def download_file(bucket, directory, local_name, key_name, b2):
    file_path = directory + '/' + local_name
    try:
        b2.Bucket(bucket).download_file(key_name, file_path)
    except ClientError as ce:
        print('error', ce)


# Return a boto3 client object for B2 service
def get_b2_client(endpoint, keyID, applicationKey):
        b2_client = boto3.client(service_name='s3',
                                 endpoint_url=endpoint,                # Backblaze endpoint
                                 aws_access_key_id=keyID,              # Backblaze keyID
                                 aws_secret_access_key=applicationKey) # Backblaze applicationKey
        return b2_client


# Return a boto3 resource object for B2 service
def get_b2_resource(endpoint, key_id, application_key):
    b2 = boto3.resource(service_name='s3',
                        endpoint_url=endpoint,                # Backblaze endpoint
                        aws_access_key_id=key_id,              # Backblaze keyID
                        aws_secret_access_key=application_key, # Backblaze applicationKey
                        config = Config(
                            signature_version='s3v4',
                    ))
    return b2

# Upload specified file into the specified bucket
def upload_file(bucket, directory, file, b2, mime=None, b2path=None):
    file_path = directory + '/' + file
    remote_path = b2path
    if remote_path is None:
        remote_path = file
    try:
        if mime is None:
            response = b2.Bucket(bucket).upload_file(file_path, remote_path)
        else:
            response = b2.Bucket(bucket).upload_file(file_path, remote_path,
                                                 ExtraArgs={
        'ContentType': mime})
    except ClientError as ce:
        print('error', ce)

    return response

# Main program logic
def main():
    args = sys.argv[1:]  # retrieve command-line arguments passed to the script

    load_dotenv()   # load environment variables from file .env

    endpoint = os.getenv("ENDPOINT_URL_YOUR_BUCKET")  # getting environment variables from file .env
    key_id = os.getenv("KEY_ID_YOUR_ACCOUNT")  # getting environment variables from file .env
    application_key = os.getenv("APPLICATION_KEY_YOUR_ACCOUNT")  # getting environment variables from file .env
    # Call function to return reference to B2 service
    b2 = get_b2_resource(endpoint, key_id, application_key)

    file = "ignited/" + args[0] + "/manifest.plist"
    mime = "text/xml"

    response = upload_file(BUCKET_NAME, LOCAL_DIR, file, b2, mime)

    print('RESPONSE:  ', response)


# Optional (not strictly required)
if __name__ == '__main__':
    main()
