import json

import boto3


def invoke_lambda(lambda_name, payload):
    lambda_client = boto3.client("lambda")
    lambda_client.invoke(
        FunctionName=lambda_name,
        InvocationType="Event",
        Payload=json.dumps(payload),
    )
