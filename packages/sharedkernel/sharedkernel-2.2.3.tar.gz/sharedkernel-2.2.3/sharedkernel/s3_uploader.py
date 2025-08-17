import requests
import boto3
from io import BytesIO
import uuid
import os

class S3Uploader:
    def __init__(self, endpoint_url, bucket, access_key, secret_key):
        """
        Initializes the S3Uploader with credentials and optional endpoint/region.

        :param endpoint_url: Custom endpoint URL (for S3-compatible services like MinIO)
        :param bucket: Name of S3 bucket
        :param access_key: Access key
        :param secret_key: Secret key
        """
        self.endpoint_url = endpoint_url
        self.bucket = bucket
        self.access_key = access_key
        self.secret_key = secret_key

        # Initialize the S3 client
        self.s3 = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        )

    def upload_file_object(self, file_obj, object_name=None, file_extension=None, folder_name=None):
        """
        Uploads a file object to an S3 bucket and returns its URL.

        :param file_obj: File object to upload
        :param object_name: S3 file name to save as (optional)
        :param file_extension: File extension to append to object name (optional)
        :param folder_name: Optional folder name to save the file in
        :return: URL of the uploaded file if successful, else False
        """
        # Use uuid4 to generate a unique object_name if not provided
        if object_name is None:
            object_name = str(uuid.uuid4())

        # Append the file extension to the object_name
        if file_extension:
            object_name += file_extension

        # Prefix the object name with the folder if provided
        if folder_name:
            object_name = f"{folder_name}/{object_name}"

        # Upload the file object
        self.s3.upload_fileobj(file_obj, self.bucket, object_name, ExtraArgs={'ACL':'public-read'})

        # Construct the URL of the uploaded file
        file_url = f"{self.endpoint_url}/{self.bucket}/{object_name}"

        return file_url

    def upload_file_from_url(self, file_url, object_name=None, folder_name=None):
        """
        Downloads a file from a URL and uploads it to an S3 bucket, returning its URL.

        :param file_url: URL of the file to download
        :param object_name: S3 file name to save as (optional)
        :param folder_name: Optional folder name to save the file in
        :return: URL of the uploaded file if successful, else False
        """
        # Step 1: Download the file from the provided URL
        response = requests.get(file_url)
        response.raise_for_status()  # Check if the request was successful

        # Extract file extension from the URL if available
        file_extension = os.path.splitext(file_url)[1]  # Get extension from URL (e.g., .jpg, .mp3, etc.)
        
        # Use the filename from the URL if no object_name is provided, otherwise use uuid4
        if object_name is None:
            object_name = str(uuid.uuid4())  # Default to UUID if filename can't be extracted

        # Step 2: Upload the file to S3
        file_obj = BytesIO(response.content)
        return self.upload_file_object(file_obj=file_obj, object_name=object_name, file_extension=file_extension, folder_name=folder_name)
