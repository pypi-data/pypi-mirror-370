import os

import requests


class ReachDataBridgeClient:
    def __init__(self):
        self.environment = os.environ.get("ENV", "Staging")

    @property
    def base_url(self):
        return {
            "Staging": "https://api-staging.getreach.ai",
            "Prod": "https://api.getreach.ai",
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

    def stripe_create_subscription(self, user_id, business_id):
        resp = requests.post(
            f"{self.base_url}/stripe/user/{user_id}/business/{business_id}/subscription",
            headers=self.gateway_headers,
        )
        return resp

    def stripe_create_customer(self, user_id):
        resp = requests.post(
            f"{self.base_url}/stripe/user/{user_id}/customer",
            headers=self.gateway_headers,
        )
        return resp

    def stripe_create_booking_guarantee(self, business_id, booking_price):
        resp = requests.post(
            f"{self.base_url}/stripe/business/{business_id}/booking-guarantee/",
            headers=self.gateway_headers,
            params={"booking_price": booking_price},
        )
        return resp

    def stripe_get_customer(self, user_id):
        resp = requests.get(
            f"{self.base_url}/stripe/user/{user_id}/customer",
            headers=self.gateway_headers,
        )
        return resp

    def stripe_get_cards(self, user_id):
        resp = requests.get(
            f"{self.base_url}/stripe/user/{user_id}/cards", headers=self.gateway_headers
        )
        return resp

    def stripe_set_default_payment_method(self, user_id: int, default_payment_method):
        resp = requests.patch(
            f"{self.base_url}/stripe/user/{user_id}/default_payment/{default_payment_method}",
            headers=self.gateway_headers,
        )
        return resp

    def stripe_create_setup_intent(self, user_id: int):
        resp = requests.post(
            f"{self.base_url}/stripe/user/{user_id}/setup_intent",
            headers=self.gateway_headers,
        )
        return resp

    def stripe_delete_payment_method(self, payment_method: str):
        resp = requests.delete(
            f"{self.base_url}/stripe/payment_method/{payment_method}",
            headers=self.gateway_headers,
        )
        return resp

    def stripe_cancel_subscription(self, business_id: int):
        resp = requests.delete(
            f"{self.base_url}/stripe/business/{business_id}",
            headers=self.gateway_headers,
        )
        return resp

    def twilio_create_business_phone_number(self, business_id=None):
        resp = requests.post(
            f"{self.base_url}/twilio/create-business-phone-number",
            headers=self.gateway_headers,
            params={
                "business_id": business_id,
            },
        )
        return resp

    def twilio_remove_phone_number(
        self, business_id=None, phone_number=None, remove_from_db=False
    ):
        resp = requests.delete(
            f"{self.base_url}/twilio/remove-phone-number",
            headers=self.gateway_headers,
            params={
                "business_id": business_id,
                "phone_number": phone_number,
                "remove_from_db": remove_from_db,
            },
        )
        return resp

    def twilio_manage_toll_free_verification_review(
        self, business_id=None, phone_number=None
    ):
        resp = requests.post(
            f"{self.base_url}/twilio/manage-toll-free-verification-review",
            headers=self.gateway_headers,
            params={
                "business_id": business_id,
                "phone_number": phone_number,
            },
        )
        return resp

    def twilio_business_phone_details(self, business_id=None, phone_number=None):
        resp = requests.get(
            f"{self.base_url}/twilio/business-phone-details",
            headers=self.gateway_headers,
            params={
                "business_id": business_id,
                "phone_number": phone_number,
            },
        )
        return resp

    def stripe_subscription_one_time_recharge(self, business_id=None, price_id=None):
        resp = requests.post(
            f"{self.base_url}/stripe/subscription/{business_id}/one-time-charge/{price_id}",
            headers=self.gateway_headers,
        )
        return resp


#
# api_gateway = ReachApiGatewayV2()
# stripe_customer = api_gateway.stripe_create_customer(
#     user_id=1,
#     description="wilson",
#     name="teste",
#     email="teste@gmail.com",
#     phone=None,
# )
