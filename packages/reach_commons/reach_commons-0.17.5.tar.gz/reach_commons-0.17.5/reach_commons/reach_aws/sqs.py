import json
import os
from decimal import Decimal
from functools import cached_property

import boto3
from botocore.exceptions import ClientError

from reach_commons.app_logging.logger import get_reach_logger
from reach_commons.reach_aws.exceptions import (
    SQSClientPublishError,
    SQSClientTopicNotFound,
)

MESSAGE_ATTRIBUTES_TYPE = {
    str: "String",
    int: "Number",
    Decimal: "Number",
    float: "Number",
    bytes: "Binary",
    list: "String.Array",
    tuple: "String.Array",
}

FALLBACK_MESSAGE_ATTRIBUTES_TYPE = "String"


# noinspection PyMethodMayBeStatic
class BaseSQSClient:
    def __init__(
        self,
        topic_name=None,
        logger=get_reach_logger(),
        region_name="us-east-1",
        profile_name=None,
    ):
        self.topic_name = topic_name
        self.logger = logger
        self.region_name = region_name
        self.profile_name = profile_name

    @staticmethod
    def _prepare_message_attributes(attributes):
        message_attributes = {}
        for key, value in attributes.items():
            attr_type = MESSAGE_ATTRIBUTES_TYPE.get(
                type(value), FALLBACK_MESSAGE_ATTRIBUTES_TYPE
            )
            value_key = "BinaryValue" if attr_type == "Binary" else "StringValue"
            if attr_type in ("String.Array", "Number"):
                value = json.dumps(value)
            elif attr_type == "String":
                value = str(value)
            message_attributes[key] = {
                "DataType": attr_type,
                value_key: value,
            }
        return message_attributes

    def handle_exception(self, exc, message_data, message_attributes):
        error_msg = (
            "error_publishing_message, "
            "topic_name={}, "
            "message_data={}, "
            "message_attributes={}, "
            "error={}".format(self.topic_name, message_data, message_attributes, exc)
        )
        self.logger.error(error_msg)
        if exc.response["Error"]["Code"] == "NotFound":
            raise SQSClientTopicNotFound(error_msg)
        raise SQSClientPublishError(error_msg)


class SQSClient(BaseSQSClient):
    def __init__(
        self,
        topic_name=None,
        logger=get_reach_logger(),
        region_name="us-east-1",
        profile_name=None,
    ):
        super(SQSClient, self).__init__(
            topic_name=topic_name,
            logger=logger,
            region_name=region_name,
            profile_name=profile_name,
        )

    @cached_property
    def client(self):
        session = boto3.Session(
            region_name=self.region_name, profile_name=self.profile_name
        )

        return session.client("sqs")

    def publish(self, message_data, delay_seconds=60, message_attributes=None):
        if delay_seconds is None or delay_seconds < 1:
            self.logger.warning("Invalid delay_seconds value. It must be at least 1.")
            return False

        if delay_seconds > 900:
            self.logger.warning(
                "Message delay exceeds 15 minutes. Message not published."
            )
            return False
        message_attributes = message_attributes or {}
        message_attributes = self._prepare_message_attributes(message_attributes)

        self.logger.debug(
            "topic_name={}, "
            "message_data={}, "
            "message_attributes={}".format(
                self.topic_name, message_data, message_attributes
            )
        )

        message_data["delay_seconds"] = delay_seconds
        message = json.dumps(message_data)

        try:
            self.client.send_message(
                QueueUrl=self.topic_name,
                MessageBody=message,
                DelaySeconds=delay_seconds,
                MessageAttributes=message_attributes,
            )
        except ClientError as exc:
            self.logger.error(
                "publish_message_error, "
                "topic_name={}, "
                "message={}, "
                "message_attributes={},"
                "error={}".format(
                    self.topic_name, message, message_attributes, str(exc)
                )
            )
            self.handle_exception(exc, message_data, message_attributes)

        self.logger.debug(
            "published_message, "
            "topic_name={}, "
            "message={}, "
            "message_attributes={}".format(self.topic_name, message, message_attributes)
        )

        return True


class MessageFilter:
    """
    A utility class responsible for filtering SQS messages based on the service name.

    Methods:
        filter_messages(service_name: str, event: dict) -> list:
            Filters messages from the provided event based on the service name.
    """

    @staticmethod
    def filter_messages(
        event,
        service_name=None,
        logger=get_reach_logger(),
    ):
        """
        Filter messages from the provided event based on the given service name.

        If the service_name is None or matches the service specified in the message attributes,
        the message is included in the returned list.

        Args:
        - service_name (str): The name of the service to filter messages for.
                             If None, all messages are returned.
        - event (dict): The event data containing SQS records.

        Returns:
        - list: A list of messages filtered based on the service name.
        """
        logger.info(event)
        messages = []
        s3_client = boto3.client("s3")

        for record in event.get("Records", []):
            message_body = (
                record["body"]
                if isinstance(record["body"], dict)
                else json.loads(record["body"])
            )

            if (
                not service_name
                or service_name
                == record["messageAttributes"]["service_name"]["stringValue"]
            ):
                if (
                    isinstance(message_body, list)
                    and message_body[0]
                    == "software.amazon.payloadoffloading.PayloadS3Pointer"
                ):
                    s3_pointer = message_body[1]
                    s3_bucket_name = s3_pointer["s3BucketName"]
                    s3_key = s3_pointer["s3Key"]

                    # Fetch the actual message from S3
                    s3_object = s3_client.get_object(Bucket=s3_bucket_name, Key=s3_key)
                    actual_message_body = s3_object["Body"].read().decode("utf-8")
                    messages.append(json.loads(actual_message_body))
                else:
                    messages.append(message_body)

        return messages


class HubspotSQSNotifier(SQSClient):
    """
    Example:
        hubspot_msg = HubspotSQSNotifier()
        hubspot_msg.notify_business_change(business_id=10293)
    """

    SERVICE_NAME = "HubspotSQSNotifier"
    TOPIC_NAME = "reach-data-bridge-messages-queue"
    DEFAULT_REGION = "us-east-1"

    def __init__(
        self,
        region_name=DEFAULT_REGION,
        logger=get_reach_logger(),
        env=os.environ.get("ENV", "Staging"),
    ):
        super().__init__(
            region_name=region_name,
            logger=logger,
            topic_name=f"{env}-{self.TOPIC_NAME}",
        )

    def send_message(
        self, object_name, object_id, secondary_object_id=None, delay_seconds=60
    ):
        message_data = {
            "object_name": object_name,
            "object_id": object_id,
            "delay_seconds": delay_seconds,
        }
        if secondary_object_id is not None:
            message_data["secondary_object_id"] = secondary_object_id

        message_attributes = {"service_name": self.SERVICE_NAME}

        return self.publish(
            message_data=message_data,
            message_attributes=message_attributes,
            delay_seconds=delay_seconds,
        )

    def republish(self, message):
        delay_seconds = message.get("delay_seconds", 60)

        if "delay_seconds" in message:
            delay_seconds *= 2

        object_name = message["object_name"]
        object_id = message["object_id"]
        secondary_object_id = message.get("secondary_object_id")

        self.send_message(
            object_name=object_name,
            object_id=object_id,
            secondary_object_id=secondary_object_id,
            delay_seconds=delay_seconds,
        )

        return delay_seconds

    def notify_business_change(self, business_id, delay_seconds=60):
        return self.send_message(
            object_name="business_change",
            object_id=business_id,
            delay_seconds=delay_seconds,
        )

    def notify_user_change(self, user_id, delay_seconds=60):
        return self.send_message(
            object_name="user_change", object_id=user_id, delay_seconds=delay_seconds
        )

    def notify_user_business_change(self, user_id, business_id, delay_seconds=60):
        return self.send_message(
            object_name="user_business_change",
            object_id=user_id,
            secondary_object_id=business_id,
            delay_seconds=delay_seconds,
        )


class OutscraperSQSNotifier(SQSClient):
    SERVICE_NAME = "OutscraperSQSNotifier"
    TOPIC_NAME = "reach-data-bridge-messages-queue"
    DEFAULT_REGION = "us-east-1"

    def __init__(
        self,
        region_name=DEFAULT_REGION,
        logger=get_reach_logger(),
        env=os.environ.get("ENV", "Staging"),
    ):
        super().__init__(
            region_name=region_name,
            logger=logger,
            topic_name=f"{env}-{self.TOPIC_NAME}",
        )

    def notify_for_google_reviews_sync(
        self, business_id, step="call_outscraper", delay_seconds=60
    ):
        message_data = {"business_id": business_id, "step": step}

        message_attributes = {"service_name": self.SERVICE_NAME}

        return self.publish(
            message_data=message_data,
            message_attributes=message_attributes,
            delay_seconds=delay_seconds,
        )

    def notify_step_from_redis(
        self,
        business_id,
        redis_key_id: str,
        step: str,
        business_info_operation: str = None,
        delay_seconds=60,
    ):
        message_data = {
            "business_id": business_id,
            "redis_key_id": redis_key_id,
            "step": step,
            "business_info_operation": business_info_operation,
        }

        message_attributes = {"service_name": self.SERVICE_NAME}

        return self.publish(
            message_data=message_data,
            message_attributes=message_attributes,
            delay_seconds=delay_seconds,
        )

    def republish(self, message):
        message_attributes = {"service_name": self.SERVICE_NAME}

        delay_seconds = message.get("delay_seconds", 5)

        if "delay_seconds" in message:
            delay_seconds *= 2

        self.publish(
            message_data=message,
            message_attributes=message_attributes,
            delay_seconds=delay_seconds,
        )
        return delay_seconds


class EmailProcessorSQSNotifier(SQSClient):
    SERVICE_NAME = "EmailProcessorSQSNotifier"
    TOPIC_NAME = "email-messages-queue"
    DEFAULT_REGION = "us-east-1"

    def __init__(
        self,
        region_name=DEFAULT_REGION,
        logger=get_reach_logger(),
        env=os.environ.get("ENV", "Staging"),
    ):
        super().__init__(
            region_name=region_name,
            logger=logger,
            topic_name=f"{env}-{self.TOPIC_NAME}",
        )

    def notify_for_send_email(
        self,
        subject: str,
        to: str,
        from_: str,
        plain_text_content: str,
        html_content: str,
        message_id: str,
        delay_seconds=60,
        send_at=None,
        from_name=None,
        asm=None,
    ):
        message_data = {
            "subject": subject,
            "message_id": message_id,
            "to": to,
            "from": from_,
            "from_name": from_name,
            "plain_text_content": plain_text_content,
            "html_content": html_content,
        }
        if asm:
            message_data["asm"] = asm
            # {"group_id": 18335, "groups_to_display": [18335]}
        if send_at:
            message_data["send_at"] = send_at

        message_attributes = {"service_name": self.SERVICE_NAME}

        return self.publish(
            message_data=message_data,
            message_attributes=message_attributes,
            delay_seconds=delay_seconds,
        )


class SmsProcessorSQSNotifier(SQSClient):
    SERVICE_NAME = "SmsProcessorSQSNotifier"
    TOPIC_NAME = "sms-messages-queue"
    DEFAULT_REGION = "us-east-1"

    def __init__(
        self,
        region_name=DEFAULT_REGION,
        logger=get_reach_logger(),
        env=os.environ.get("ENV", "Staging"),
    ):
        super().__init__(
            region_name=region_name,
            logger=logger,
            topic_name=f"{env}-{self.TOPIC_NAME}",
        )

    def notify_for_send_sms(
        self,
        from_: str,
        to: str,
        body: str,
        message_id: str,
        long_url: str = None,
        delay_seconds=2,
        send_at=None,
        message_type=None,
        campaign_id=None,
    ):
        message_data = {
            "body": body,
            "to": to,
            "from": from_,
            "message_id": message_id,
            "long_url": long_url,
        }

        message_data.update(
            {
                k: v
                for k, v in {
                    "send_at": send_at,
                    "message_type": message_type,
                    "campaign_id": campaign_id,
                }.items()
                if v is not None
            }
        )

        message_attributes = {"service_name": self.SERVICE_NAME}

        return self.publish(
            message_data=message_data,
            message_attributes=message_attributes,
            delay_seconds=delay_seconds,
        )

    def notify_for_republish_sms(self, message_data):
        delay_seconds = message_data.get("delay_seconds", 60)

        if "delay_seconds" in message_data:
            delay_seconds *= 2

        message_attributes = {"service_name": self.SERVICE_NAME}

        return self.publish(
            message_data=message_data,
            message_attributes=message_attributes,
            delay_seconds=delay_seconds,
        )


class POSApiPullerSQSNotifier(SQSClient):
    SERVICE_NAME = "POSApiPullerSQSNotifier"
    TOPIC_NAME = "pos-api-messages-queue"
    DEFAULT_REGION = "us-east-1"

    def __init__(
        self,
        region_name=DEFAULT_REGION,
        logger=get_reach_logger(),
        env=os.environ.get("ENV", "Staging"),
    ):
        super().__init__(
            region_name=region_name,
            logger=logger,
            topic_name=f"{env}-{self.TOPIC_NAME}",
        )

    def notify_for_send_message(
        self,
        message_data: dict,
        delay_seconds=2,
    ):
        message_attributes = {"service_name": self.SERVICE_NAME}

        return self.publish(
            message_data=message_data,
            message_attributes=message_attributes,
            delay_seconds=delay_seconds,
        )
