import requests
from requests.auth import HTTPBasicAuth

from reach_commons.app_logging.logger import get_reach_logger


class CommonsPhoneNumberValidation:
    def __init__(self, logger=get_reach_logger()):
        self.base_url = "https://lookups.twilio.com/v1/PhoneNumbers/"
        self.account_sid = "AC1f9d2cb1c49cf9522f0de29861c9652d"
        self.auth_token = "2a5557dd0c80ea45bc23b3de68455480"
        self.logger = logger

    def is_valid_phone_number(self, phone_number):
        url = f"{self.base_url}{phone_number}"
        auth = HTTPBasicAuth(self.account_sid, self.auth_token)

        response = requests.get(url, auth=auth)

        if response.status_code == 200:
            return True
        else:
            self.logger.warning(
                f"Phone number {phone_number} is invalid. Status code: {response.status_code}, "
                f"Response: {response.text}"
            )
            return False
