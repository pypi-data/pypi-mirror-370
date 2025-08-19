# reach_commons

## Description

`reach_commons` is a Python library that provides various classes and utilities to assist developers in their projects. This library aims to simplify and streamline processes by offering reusable components that can be easily integrated into various Python applications.

## Installation

Install `reach_commons` using pip:

```bash
pip install reach_commons

from reach_commons.api_client_v2 import ReachApiGatewayV2

api_gateway = ReachApiGatewayV2(
                        base_url=os.environ["api_gateway_v2_endpoint"],
                        access_token=os.environ["event_processor_token"],
                    )
response = api_gateway.stripe_create_booking_guarantee(
                        business_id=business_id, booking_price=booking_price
                    )
{
            "statusCode": stripe_customer.status_code,
            "body": json.dumps(response.json()),
        }