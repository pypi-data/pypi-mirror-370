import curlify
import requests
from requests.adapters import HTTPAdapter

from reach_commons.app_logging.logger import get_reach_logger


class HttpRequestLogger(HTTPAdapter):
    """
    A custom HTTPAdapter for logging details of HTTP requests and responses.
    This class logs each request and response including URL, method, headers,
    and body. It also includes a unique UUID for each request, along with
    business_id and pos_partner_name for easier query and identification.

    Attributes:
        business_id (str): Identifier for the business.
        pos_partner_name (str): Name of the POS partner.

    Example of use:
        # Create a logging session with business details
        session = create_logging_session(business_id="12345",
                                         pos_partner_name="ExamplePOS")

        # Use the session to make requests
        response = session.get("https://httpbin.org/get", params={"test": "value"})
        # Request and response details will be logged with UUID, business_id, and pos_partner_name
    """

    def __init__(
        self, logger=get_reach_logger(), business_id=None, pos_partner_name=None
    ):
        super().__init__()
        self.logger = logger
        self.business_id = business_id
        self.pos_partner_name = pos_partner_name

    def send(self, request, **kwargs):
        # Unique identifier for each request
        self.logger.info(f"URL: {request.url}")
        self.logger.info(f"Method: {request.method}")
        self.logger.info(f"Headers: {request.headers}")
        self.logger.info(f"Body: {request.body}")

        # Send the request
        response = super(HttpRequestLogger, self).send(request, **kwargs)

        # Log response details with business_id, pos_partner_name, and request_uuid
        self.logger.info(f"Response Status: {response.status_code}")
        self.logger.info(f"Response Headers: {response.headers}")
        self.logger.info(f"Response Content: {response.content}")
        self.logger.info(f"Complete Curl: {curlify.to_curl(response.request)}")

        return response


def create_logging_session(
    logger=get_reach_logger(), business_id=None, pos_partner_name=None
):
    session = requests.Session()
    logger_adapter = HttpRequestLogger(
        logger=logger, business_id=business_id, pos_partner_name=pos_partner_name
    )
    session.mount("http://", logger_adapter)
    session.mount("https://", logger_adapter)
    return session
