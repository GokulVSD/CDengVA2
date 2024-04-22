#__copyright__   = "Copyright 2024, VISA Lab"
#__license__     = "MIT"

import os
import boto3
import urllib.parse
import subprocess

s3 = boto3.client('s3')

def lambda_handler(event, context):

    s3Record = event['Records'][0]['s3']
    bucket = s3Record['bucket']['name']
    key = urllib.parse.unquote_plus(s3Record['object']['key'], encoding='utf-8')
    downloaded_file = os.path.join("/tmp", key)
    s3.download_file(
        Filename=downloaded_file,
        Bucket=bucket,
        Key=key
    )
    output_path, filename = split_video(downloaded_file)
    s3.upload_file(output_path, '1229503862-stage-1', filename)

    return {
        'statusCode': 200,
        'body': {
            "bucket_name": "1229503862-stage-1",
            "image_file_name": filename
        }
    }


def split_video(video_path):
    filename = os.path.basename(video_path)
    name = os.path.splitext(filename)[0]
    output_filename = name + ".jpg"
    output_path = os.path.join("/tmp", output_filename)

    split_cmd = f'/opt/ffmpeg -i {video_path} -vframes 1 {output_path}'

    subprocess.check_call(split_cmd, shell=True)

    return output_path, output_filename