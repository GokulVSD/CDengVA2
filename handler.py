#__copyright__   = "Copyright 2024, VISA Lab"
#__license__     = "MIT"

import os
import boto3
import urllib.parse
from splitter import video_splitting_cmdline

s3 = boto3.client('s3')

def handler(event, context):

    s3Record = event['Records'][0]['s3']
    bucket = s3Record['bucket']['name']
    key = urllib.parse.unquote_plus(s3Record['object']['key'], encoding='utf-8')
    downloaded_file = os.path.join("/tmp", key)
    s3.download_file(
        Filename=downloaded_file,
        Bucket=bucket,
        Key=key
    )
    output_dir = video_splitting_cmdline(downloaded_file)

    for root, dirs, files in os.walk(output_dir):
        for filename in files:
            local_path = os.path.join(root, filename)
            s3_path = os.path.join(key.split('.')[0], os.path.relpath(local_path, output_dir))
            s3.upload_file(local_path, '1229503862-stage-1', s3_path)
