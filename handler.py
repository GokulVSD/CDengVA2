#__copyright__   = "Copyright 2024, VISA Lab"
#__license__     = "MIT"

import os
import boto3
import urllib.parse
import subprocess

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
    output_dir = split_video(downloaded_file)

    for root, dirs, files in os.walk(output_dir):
        for filename in files:
            local_path = os.path.join(root, filename)
            s3_path = os.path.join(key.split('.')[0], os.path.relpath(local_path, output_dir))
            s3.upload_file(local_path, '1229503862-stage-1', s3_path)


def split_video(video_path):
    filename = os.path.basename(video_path)
    name = os.path.splitext(filename)[0]
    output_dir = os.path.join("/tmp", name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    split_cmd = f'/usr/bin/ffmpeg -ss 0 -r 1 -i {video_path} -vf fps=1/10 -start_number 0 -vframes 10 {output_dir}/output-%02d.jpg -y'
    subprocess.check_call(split_cmd, shell=True)

    return output_dir