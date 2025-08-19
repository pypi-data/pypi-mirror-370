import json
import math
import os
from datetime import datetime
from functools import cached_property
from time import sleep

import boto3
from botocore.exceptions import ClientError

from reach_commons.app_logging.logger import get_reach_logger
from reach_commons.reach_aws.exceptions import KinesisClientException
from reach_commons.utils import ReachChunkObjectsUtils, remove_nulls


# noinspection PyMethodMayBeStatic
class BaseFirehoseClient:
    def __init__(
        self,
        logger=get_reach_logger(),
        region_name="us-east-1",
        profile_name=None,
    ):
        self.region_name = region_name
        self.profile_name = profile_name
        self.logger = logger

    def handle_exception(self, exc, secret, ciphertext):
        error_msg = (
            "error_kinesis_client, "
            "secret={}, "
            "ciphertext={!r}, "
            "error={!r}".format(secret, ciphertext, exc)
        )
        self.logger.error(error_msg)
        raise KinesisClientException(error_msg)


class FirehoseClient(BaseFirehoseClient):
    def __init__(self, delivery_stream_name=None, env=os.environ.get("ENV", "Staging")):
        super().__init__()
        self.delivery_stream_name = (
            delivery_stream_name or f"{env}-kinesis-firehose-extended-s3-stream"
        )

    @cached_property
    def client(self):
        session = boto3.Session(
            region_name=self.region_name, profile_name=self.profile_name
        )
        return session.client("firehose")

    def write_google_review_downloaded(
        self,
        business_id: int,
        partner_name: str,
        object_payload,
        method_name: str,
        split_array_path=None,
        retry: int = 0,
    ):
        return self.write(
            business_id=business_id,
            partner_name=partner_name,
            object_payload=object_payload,
            object_name="GoogleReviewDownloaded",
            method_name=method_name,
            split_array_path=split_array_path,
            retry=retry,
        )

    def write_sendgrid_email(
        self, business_id: int, partner_name: str, object_payload, message_id=0
    ):
        return self.write(
            business_id=business_id,
            partner_name=partner_name,
            object_payload=object_payload,
            object_name="sendgrid",
            method_name="email-reply",
            message_id=message_id,
        )

    def write_sendgrid_email_v2(
        self, business_id: int, partner_name: str, object_payload, message_id=0
    ):
        return self.write(
            business_id=business_id,
            partner_name=partner_name,
            object_payload=object_payload,
            object_name="sendgrid",
            method_name="email",
            message_id=message_id,
        )

    def write(
        self,
        business_id: int,
        partner_name: str,
        object_payload,
        object_name: str,
        method_name: str,
        split_array_path=None,
        retry: int = 0,
        message_id: str = None,
    ):
        object_payload = (
            remove_nulls(object_payload)
            if isinstance(object_payload, dict)
            else object_payload
        )

        def attempt_send(payload, current_retry):
            firehose_message = {
                "DateTime": str(datetime.now()),
                "MinuteGroup": int(15 * (math.floor(datetime.now().minute / 15))),
                "BusinessID": business_id,
                "PartnerName": partner_name,
                "ObjectName": object_name,
                "MethodName": method_name,
                "ObjectPayload": payload,
            }
            if message_id:
                firehose_message["MessageID"] = message_id

            try:
                record = {"Data": json.dumps(firehose_message)}
                response = self.client.put_record(
                    DeliveryStreamName=self.delivery_stream_name, Record=record
                )
                self.logger.info(
                    f"Successfully sent data to Firehose for BusinessID: {business_id}, Retry attempt: {current_retry}"
                )

                return response
            except Exception as ex:
                self.logger.exception(
                    "An error occurred while trying to send data to Firehose",
                    exc_info=ex,
                )
                if current_retry < 20:
                    sleep(1)
                    self.logger.info(
                        f"Retrying to send data to Firehose for BusinessID: {business_id}, "
                        f"Next retry attempt: {current_retry + 1}"
                    )
                    return attempt_send(payload, current_retry + 1)

        if split_array_path:
            self.logger.info(
                f"Splitting payload for BusinessID: {business_id} using path: {split_array_path}"
            )

            chunked_payloads = ReachChunkObjectsUtils.chunk_list_items(
                obj_to_split=object_payload, path_of_array=split_array_path
            )

            for chunk in chunked_payloads:
                self.logger.info(
                    f"Sending a chunked payload part for BusinessID: {business_id}"
                )

                attempt_send(chunk, retry)
        else:
            self.logger.info(
                f"Sending payload for BusinessID: {business_id} without splitting"
            )

            return attempt_send(object_payload, retry)
