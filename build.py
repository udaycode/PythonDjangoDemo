""" 
Build file for a django app to upload the zip to s3
It takes latest tag as the version and create the build
as project-version.tar.gz
Put this script in the project folder in the root location
and configure Jenkins to execute this
"""
import os
import subprocess
import boto3

KEY = os.environ['S3_BUILD_KEY']
SECRET = os.environ['S3_BUILD_SECRET']
BUCKET = os.environ['S3_BUILD_BUCKET']
REGION = os.environ['S3_REGION']

output = subprocess.check_output(['git', 'tag'])
tags = output.decode().split("\n")
latest = tags[-2]
print("### working on tag ... {} ####".format(latest))
# Make the archive file using the system commands
build_file = "project-{}.tar.gz".format(latest)
os.system("tar -cvf {} project".format(build_file))
print("#### uploading ...######")
client = boto3.client("s3", config= boto3.session.Config(signature_version='s3v4'),
                            aws_access_key_id=KEY,
                            region_name=REGION,
                            aws_secret_access_key=SECRET)
client.upload_file(build_file, BUCKET, build_file)
print("####### removing archive #######")
os.system("rm {}".format(build_file))
print("####### deplying in dev #########")
#os.system("ansible-playbook deploy.yml --extra-vars 'tag={}'".format(latest))