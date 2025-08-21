from functools import cached_property
from io import BytesIO
from urllib.parse import unquote, urlparse

import boto3

from reach_commons.app_logging.logger import get_reach_logger


class S3Client:
    def __init__(
        self,
        logger=get_reach_logger(),
        region_name="us-east-1",
        profile_name=None,
    ):
        self.logger = logger
        self.region_name = region_name
        self.profile_name = profile_name

    @cached_property
    def client(self):
        session = boto3.Session(
            region_name=self.region_name, profile_name=self.profile_name
        )

        return session.client("s3")

    def _parse_s3_url(self, url: str) -> tuple[str, str]:
        """
        Support various S3 URL formats:
        - s3://bucket/key
        - https://bucket.s3.amazonaws.com/key
        - https://bucket.s3.<region>.amazonaws.com/key
        - https://s3.<region>.amazonaws.com/bucket/key (path-style)
        - https://s3.amazonaws.com/bucket/key (path-style)
        """
        p = urlparse(url)

        if p.scheme == "s3":
            bucket = p.netloc
            key = p.path.lstrip("/")
            return bucket, unquote(key)

        host = p.netloc
        path = p.path.lstrip("/")

        # Path-style: s3.<region>.amazonaws.com/bucket/key  ou s3.amazonaws.com/bucket/key
        if host.startswith("s3.") or host == "s3.amazonaws.com":
            parts = path.split("/", 1)
            if not parts or not parts[0]:
                raise ValueError(f"Invalid S3 URL (missing bucket in path): {url}")
            bucket = parts[0]
            key = parts[1] if len(parts) > 1 else ""
            return bucket, unquote(key)

        # Virtual-hosted: bucket.s3[.<region>].amazonaws.com/key
        bucket = host.split(".")[0]
        key = path
        if not bucket:
            raise ValueError(f"Invalid S3 URL (missing bucket in host): {url}")
        return bucket, unquote(key)

    def get_object(self, s3_bucket_name, s3_key):
        try:
            s3_object = self.client.get_object(Bucket=s3_bucket_name, Key=s3_key)
            actual_message_body = s3_object["Body"].read().decode("utf-8")

            self.logger.info(
                f"Retrieved object from S3: {s3_key} in bucket: {s3_bucket_name}"
            )
            return actual_message_body
        except Exception as e:
            self.logger.error(
                f"Error retrieving object {s3_key} from bucket: {s3_bucket_name}: {str(e)}"
            )

        return None

    def add_object(self, s3_bucket_name, s3_key, str_content):
        try:
            file_object = BytesIO(str_content.encode("utf-8"))

            self.client.upload_fileobj(
                Fileobj=file_object, Bucket=s3_bucket_name, Key=s3_key
            )
            url = (
                f"https://{s3_bucket_name}.s3.{self.region_name}.amazonaws.com/{s3_key}"
            )

            self.logger.info(
                f"Uploaded object to S3: {s3_key} in bucket: {s3_bucket_name}"
            )
            return url
        except Exception as e:
            self.logger.error(
                f"Error uploading object {s3_key} to bucket: {s3_bucket_name}: {str(e)}"
            )
            return None

    def delete_object_by_url(self, url: str) -> bool:
        """
        Deleta um objeto no S3 recebendo apenas a URL direta.
        Retorna True se deletou (ou o objeto não existia) e False se falhou.
        """
        try:
            bucket, key = self._parse_s3_url(url)
            self.client.delete_object(Bucket=bucket, Key=key)
            self.logger.info(f"Deleted object from S3: {key} in bucket: {bucket}")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting S3 object from url '{url}': {e}")
            return False
