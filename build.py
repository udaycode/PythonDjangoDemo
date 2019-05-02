""" 
Build file for a django app to upload the zip to s3
It takes latest tag as the version and create the build
as project-version.tar.gz
Put this script in the project folder in the root location
and configure Jenkins to execute this
"""
import os
import json
import subprocess
import boto3

# JSON file containing the secrets for all builds
CREDFILE_PATH = "/var/lib/creds.json"
CREDS = {}

with open(CREDFILE_PATH, 'r') as f:
	CREDS = json.loads(f.read())

# Default version is branch name
version = "master"

# Lets get version from the branch, if not fall back to the branch
output = subprocess.check_output(['git', 'tag'])
tags = output.decode().split("\n")
try:
	version = tags[-2]
except IndexError:
	output = subprocess.check_output(['git', 'branch'])
	version = output.decode().split()[-1]

print("### working on version ... {} ####".format(version))

# Make the archive file using the system commands
build_file = "project-{}.tar.gz".format(version)
os.system("tar -cvf {} project".format(build_file))
print("#### uploading ...######")
client = boto3.client("s3", config= boto3.session.Config(signature_version='s3v4'),
                            aws_access_key_id=CREDS['S3_BUILD_KEY'],
                            region_name=CREDS['S3_REGION'],
                            aws_secret_access_key=CREDS['S3_BUILD_SECRET'])
client.upload_file(build_file, CREDS['S3_BUILD_BUCKET'], build_file)
print("####### removing archive #######")
os.system("rm {}".format(build_file))
print("####### deploying in dev #########")
os.system("sudo ansible-playbook deploy.yml --extra-vars 'version={}'".format(version))