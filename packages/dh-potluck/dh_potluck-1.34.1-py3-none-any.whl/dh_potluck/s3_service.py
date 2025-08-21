import mimetypes
import os
import secrets

import boto3
from flask import current_app

from dh_potluck.types.json_serializable import JSONSerializable

SECONDS_IN_A_YEAR = 3600 * 24 * 365


class S3Service:
    _s3 = None

    @classmethod
    def _get_s3(cls):
        if not cls._s3:
            session = boto3.session.Session(
                aws_access_key_id=current_app.config['DH_POTLUCK_AWS_ACCESS_KEY_ID'],
                aws_secret_access_key=current_app.config['DH_POTLUCK_AWS_SECRET_ACCESS_KEY'],
            )
            cls._s3 = session.resource('s3')
        return cls._s3

    @classmethod
    def upload_file(
        cls,
        local_file_uri: str,
        bucket_name: str,
        s3_file_path: str,
        extra_args: JSONSerializable = None,
        add_secret_to_filename: bool = True,
    ) -> str:
        """
        upload file to s3 bucket and return public s3 url
        @param local_file_uri: full path of file being uploaded
        @param bucket_name: name of bucket to upload to on s3
        @param s3_file_path: full target path of s3 file to upload to
        @param extra_args: additional params such as ContentType and CacheControl
        @param add_secret_to_filename: if to add a secret to the filename. Prehashed filenames
        can override this parameter
        """
        try:
            s3 = cls._get_s3()
            bucket = s3.Bucket(bucket_name)

            if not extra_args:
                type, encoding = mimetypes.guess_type(local_file_uri)
                type = type or 'application/octet-stream'
                extra_args = {
                    'ContentType': type,
                    'ACL': 'public-read',
                    'CacheControl': 'max-age %d' % SECONDS_IN_A_YEAR,
                }

            if add_secret_to_filename:
                s3_file_path = cls.add_secret_to_filename(s3_file_path)
            bucket.upload_file(local_file_uri, s3_file_path, ExtraArgs=extra_args)
            return f'https://{bucket_name}.s3.amazonaws.com/{s3_file_path}'
        except Exception as e:
            raise S3ServiceException(message=f'Error occurred while uploading file to S3: {str(e)}')

    @staticmethod
    def add_secret_to_filename(file_uri: str) -> str:
        name, ext = os.path.splitext(file_uri)
        secret = secrets.token_hex(16)
        return f'{name}-{secret}{ext}'


class S3ServiceException(Exception):
    def __init__(self, message: str = 'Error occurred while uploading file to S3.') -> None:
        self.message = message
        super().__init__(self.message)
