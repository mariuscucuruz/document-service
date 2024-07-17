from environment import LoadEnv
from Service.logg import Log
import os
from datetime import timedelta
from minio import Minio, S3Error
from pathlib2 import Path


class Storage:
    def __init__(self, bucket_name=None):
        self.env = LoadEnv()
        self.logging = Log(self.__class__.__name__)
        self.logging.info("Instantiating Storage.")

        self.bucket_name = (
            bucket_name if bucket_name is not None else self.env.storage_bucket_name
        )

        try:
            self.client = Minio(
                endpoint=self.env.storage_endpoint,
                access_key=self.env.storage_access_key,
                secret_key=self.env.storage_secret_key,
            )
            self.logging.info("S3 Client connected.")

        except S3Error as ex:
            self.logging.error(f"S3 Client connection error: {ex}.")

    def is_ready(self):
        try:
            found = self.client.bucket_exists(self.bucket_name)
            if not found:
                self.client.make_bucket(self.bucket_name)
                self.logging.info(f"Bucket not found! Creating {self.bucket_name}.")
            else:
                self.logging.info(f"Found existing bucket named {self.bucket_name}.")
            return True

        except S3Error as ex:
            self.logging.error(f"Bucket error: {ex}.")
            return False

    def upload_object(self, upload_object_path: Path):
        file_name = Path(upload_object_path).name
        self.logging.info(f"Uploading {file_name} to {self.bucket_name}...")

        try:
            self.client.fput_object(
                bucket_name=self.bucket_name,
                object_name=file_name,
                file_path=upload_object_path,
            )
            self.logging.info(f"Uploaded {file_name} to bucket {self.bucket_name}.")

            try:
                os.remove(upload_object_path)

            except Exception as ex:
                self.logging.warning(
                    f"Unable to delete local {file_name} file after S3 upload: {ex}"
                )

        except S3Error as ex:
            self.logging.error(f"Object upload error {ex}.")

    def share_object_get_url(self, object_name: str, expires_hrs=999):
        try:
            self.is_ready()
            download_url = self.client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                # expires=timedelta(hours=expires_hrs),
            )
            return download_url

        except S3Error as ex:
            self.logging.error(f"Object sharing error {ex}.")
            return None
