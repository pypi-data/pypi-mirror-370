import os

import requests


class EventProcessorClient:
    def __init__(self):
        self.environment = os.environ.get("ENV", "Staging")

    @property
    def base_url(self):
        return {
            "Staging": "https://90tin0ndr1.execute-api.us-east-1.amazonaws.com",
            "Prod": "https://101iu6hpaj.execute-api.us-east-1.amazonaws.com",
        }.get(self.environment)

    @property
    def gateway_headers(self):
        common_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        auth_token = {
            "Staging": "Bearer 6c6adc18-22a9-929f-648d-786eb20ebcf4",
            "Prod": "Bearer a57a82c0-0493-563b-ba1d-6c63c201ce20",
        }.get(self.environment)

        headers = {**common_headers, "Authorization": auth_token}

        return headers

    def review_profile_patch_business(self, business_id):
        headers = {**self.gateway_headers, "X-Api-Version": "v2"}
        resp = requests.patch(
            f"{self.base_url}/v1/review-profile/business/{business_id}", headers=headers
        )
        return resp

    def review_profile_post_business(self, business_id):
        headers = {**self.gateway_headers, "X-Api-Version": "v2"}
        resp = requests.post(
            f"{self.base_url}/v1/review-profile/business/{business_id}",
            headers=headers,
        )
        return resp

    def review_profile_delete_business(self, business_id):
        headers = {**self.gateway_headers, "X-Api-Version": "v2"}
        resp = requests.delete(
            f"{self.base_url}/v1/review-profile/business/{business_id}",
            headers=headers,
        )
        return resp

    def create_twilio_phone_number_by_business(self, business_id):
        headers = {**self.gateway_headers}
        resp = requests.post(
            f"{self.base_url}/v1/business/{business_id}/twillio",
            headers=headers,
        )
        return resp
