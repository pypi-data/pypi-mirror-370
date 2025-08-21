import json
import re
from datetime import datetime
from decimal import Decimal
from functools import cached_property
from typing import Dict

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from reach_commons.app_logging.logger import get_reach_logger
from reach_commons.utils import DecimalEncoder, build_update_params_for_attributes


# noinspection PyMethodMayBeStatic
class BaseDynamoDBClient:
    def __init__(
        self,
        region_name="us-east-1",
        profile_name=None,
    ):
        self.region_name = region_name
        self.profile_name = profile_name


class DynamoDBClient(BaseDynamoDBClient):
    @cached_property
    def client(self):
        session = boto3.Session(
            region_name=self.region_name, profile_name=self.profile_name
        )
        return session.client("dynamodb")

    def put_item(self, table_name, item):
        return self.client.put_item(TableName=table_name, Item=item)


class SMSConversationsComonQueries:
    @staticmethod
    def clean_phone_number(phone_number):
        return re.sub(r"\D", "", phone_number)

    @staticmethod
    def add_message_to_conversation_v2(
        table,
        from_number,
        to_number,
        business_id,
        business_number,
        body,
    ):
        from_number = SMSConversationsComonQueries.clean_phone_number(from_number)
        to_number = SMSConversationsComonQueries.clean_phone_number(to_number)
        business_number = SMSConversationsComonQueries.clean_phone_number(
            business_number
        )
        other_number = from_number if from_number != business_number else to_number

        timestamp = datetime.utcnow().isoformat() + "Z"
        conversation_key = f"CHAT#{other_number}#TIMESTAMP#{timestamp}"

        status_message = "SENT" if from_number == business_number else "RECEIVED"

        item = {
            "PK": f"BUSINESS#{business_id}",
            "SK": conversation_key,
            "from_number": from_number,
            "to_number": to_number,
            "created_at": timestamp,
            "updated_at": timestamp,
            "status_message": status_message,
            "body": body,
        }

        table.put_item(Item=item)

        table.update_item(
            Key={"PK": f"BUSINESS#{business_id}", "SK": f"CONV#{other_number}"},
            UpdateExpression="SET last_message = :last_message, created_at = if_not_exists(created_at, :created_at)",
            ExpressionAttributeValues={
                ":last_message": item,
                ":created_at": timestamp,
            },
            ReturnValues="ALL_NEW",
        )

    @staticmethod
    def update_chat_status(table, pk, sk, status_message):
        timestamp = datetime.utcnow().isoformat() + "Z"
        table.update_item(
            Key={"PK": pk, "SK": sk},
            UpdateExpression="SET status_message = :status_message, updated_at = :updated_at",
            ConditionExpression="attribute_exists(PK) AND attribute_exists(SK)",
            ExpressionAttributeValues={
                ":status_message": status_message,
                ":updated_at": timestamp,
            },
            ReturnValues="ALL_NEW",
        )

    @staticmethod
    def add_phone_owner(table, phone_number, owner_name, additional_info):
        if not owner_name or not additional_info:
            get_reach_logger().warning(
                "Both 'owner_name' and 'additional_info' must be provided. Operation ignored."
            )
            return

        if not additional_info or not (
            "business_id" in additional_info or "customer_id" in additional_info
        ):
            raise ValueError(
                "additional_info must contain either 'business_id' or 'customer_id'."
            )

        phone_number = SMSConversationsComonQueries.clean_phone_number(phone_number)

        update_expression = "SET #name = :name"
        expression_attribute_names = {"#name": "name"}
        expression_attribute_values = {":name": owner_name}

        if additional_info:
            for key, value in additional_info.items():
                update_expression += f", #{key} = :{key}"
                expression_attribute_names[f"#{key}"] = key
                expression_attribute_values[f":{key}"] = value

        table.update_item(
            Key={"PK": f"OWNER#{phone_number}", "SK": "INFO"},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
        )

    @staticmethod
    def get_phone_owner(table, phone_number):
        phone_number = SMSConversationsComonQueries.clean_phone_number(phone_number)

        response = table.get_item(Key={"PK": f"OWNER#{phone_number}", "SK": "INFO"})
        return response.get("Item")


class BusinessReviewsCommonQueries:
    @staticmethod
    def get_review_business_info(table, business_id: str) -> Dict:
        query_params = {
            "KeyConditionExpression": Key("PK").eq(f"business#{business_id}")
            & Key("SK").eq("info")
        }

        response = table.query(**query_params)

        if response["Items"]:
            business_info = response["Items"][0]
            return business_info
        else:
            return {}

    @staticmethod
    def patch_business_info(
        table,
        business_id: str,
        business_info: Dict,
        created_at_isoformat: str = None,
    ) -> str:
        filtered_info = {k: v for k, v in business_info.items() if v is not None}
        filtered_info = json.loads(
            json.dumps(filtered_info, cls=DecimalEncoder), parse_float=Decimal
        )

        try:
            table.put_item(
                Item={
                    "PK": f"business#{business_id}",
                    "SK": "info",
                    "created_at": created_at_isoformat
                    if created_at_isoformat
                    else datetime.utcnow().isoformat(),
                    **filtered_info,
                },
                ConditionExpression="attribute_not_exists(PK) AND attribute_not_exists(SK)",
            )
            return "insert"
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                (
                    update_expr,
                    attr_values,
                    attr_names,
                ) = build_update_params_for_attributes(filtered_info)
                table.update_item(
                    Key={"PK": f"business#{business_id}", "SK": "info"},
                    UpdateExpression=update_expr,
                    ExpressionAttributeValues=attr_values,
                    ExpressionAttributeNames=attr_names,
                )
                return "update"
            else:
                raise
