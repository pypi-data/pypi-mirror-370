import base64
import json
import os
from functools import cached_property

import boto3
from botocore.exceptions import ClientError

from reach_commons.app_logging.logger import get_reach_logger
from reach_commons.reach_aws.exceptions import KMSClientException


# noinspection PyMethodMayBeStatic
class BaseKMSClient:
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
            "error_kms_client, "
            "secret={}, "
            "ciphertext={!r}, "
            "error={!r}".format(secret, ciphertext, exc)
        )
        self.logger.error(error_msg)
        raise KMSClientException(error_msg)


class KMSClient(BaseKMSClient):
    @cached_property
    def client(self):
        session = boto3.Session(
            region_name=self.region_name, profile_name=self.profile_name
        )
        return session.client("kms")

    def encrypt_for_business(self, data_to_encrypt, business_id):
        custom_context = {"business_id": business_id}
        self.logger.info(
            "encript_for_business"
            "data_to_encrypt={}, "
            "business_id={} ,custom_context={!r}, ".format(
                json.dumps(data_to_encrypt)
                if isinstance(data_to_encrypt, dict)
                else data_to_encrypt,
                business_id,
                custom_context,
            )
        )

        key_alias = f"alias/{os.environ.get('ENV', 'staging')}-db-data".lower()

        return self.encrypt(custom_context, data_to_encrypt, key_alias)

    def decrypt_for_business(self, secret, business_id):
        custom_context = {"business_id": business_id}
        self.logger.info(
            "decrypt_for_business"
            "secret={}, "
            "business_id={} ,custom_context={!r}, ".format(
                json.dumps(secret) if isinstance(secret, dict) else secret,
                business_id,
                custom_context,
            )
        )
        return self.decrypt(custom_context, secret)

    def decrypt_for_user(self, secret, user_id):
        custom_context = {"user_id": user_id}
        self.logger.info(
            "decrypt_for_user"
            "secret={}, "
            "user_id={} ,custom_context={!r}, ".format(
                json.dumps(secret) if isinstance(secret, dict) else secret,
                user_id,
                custom_context,
            )
        )
        return self.decrypt(custom_context, secret)

    def encrypt(self, custom_context, data_to_encrypt: str, key_alias: str):
        ciphertext = None
        encrypted = None
        try:
            ciphertext = self.client.encrypt(
                KeyId=key_alias,
                Plaintext=bytes(data_to_encrypt, encoding="utf8"),
                EncryptionContext={"CustomContext": f"{custom_context}"}
                if custom_context
                else None,
            )
            encrypted = base64.b64encode(ciphertext["CiphertextBlob"])
        except ClientError as exc:
            self.handle_exception(exc, data_to_encrypt, ciphertext)

        self.logger.info(
            "encrypt, "
            "data_to_encrypt={}, "
            "ciphertext={!r}, "
            "encrypted={}".format(data_to_encrypt, ciphertext, encrypted)
        )

        return encrypted

    def decrypt(self, custom_context, secret):
        plaintext = None
        decrypted = None
        try:
            if custom_context:
                plaintext = self.client.decrypt(
                    CiphertextBlob=bytes(base64.b64decode(secret)),
                    EncryptionContext={"CustomContext": f"{custom_context}"},
                )
            else:
                plaintext = self.client.decrypt(
                    CiphertextBlob=bytes(base64.b64decode(secret))
                )
            decrypted = plaintext["Plaintext"].decode("utf-8")
        except ClientError as exc:
            self.handle_exception(exc, secret, plaintext)

        self.logger.info(
            "decript, "
            "secret={}, "
            "ciphertext={!r}, "
            "decrypted={!r}".format(secret, plaintext, decrypted)
        )

        return decrypted
