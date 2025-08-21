import json
import os

import requests


class ReachOpsApiClient:
    def __init__(self):
        self.environment = os.environ.get("ENV", "Staging")

    @property
    def base_url(self):
        return {
            "Staging": "https://api-staging.getreach.ai/ops/v1",
            "Prod": "https://api.getreach.ai/ops/v1",
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

        return {**common_headers, "Authorization": auth_token}

    def business_google_review_aggregated_by_month_recalculate(
        self, business_id, business_joined_at=None
    ):
        resp = requests.post(
            f"{self.base_url}/businesses/{business_id}/google-reviews/aggregated-by-month/recalculate",
            headers=self.gateway_headers,
            params={"business_joined_at": business_joined_at},
        )
        return resp

    def business_google_review_active_sync(
        self, business_id, place_id=None, joined_at=None
    ):
        resp = requests.post(
            f"{self.base_url}/businesses/{business_id}/google-reviews/activate-sync",
            headers=self.gateway_headers,
            data=json.dumps({"place_id": place_id, "joined_at": joined_at}),
        )
        return resp

    def business_google_review_initiate_resync(self, business_id):
        resp = requests.post(
            f"{self.base_url}/businesses/{business_id}/google-reviews/initiate-resync",
            headers=self.gateway_headers,
        )
        return resp

    def conversations_balances_apply_credits_from_invoice(self, invoice: dict):
        resp = requests.post(
            f"{self.base_url}/conversations/balances/apply-credits-from-invoice",
            headers=self.gateway_headers,
            data=json.dumps(invoice),
        )
        return resp

    def enable_text_ai(self, business_id):
        resp = requests.post(
            f"{self.base_url}/conversations/{business_id}/text-ai/enable",
            headers=self.gateway_headers,
        )
        return resp
