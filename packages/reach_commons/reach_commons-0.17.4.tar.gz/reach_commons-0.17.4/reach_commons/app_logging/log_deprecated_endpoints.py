import datetime

from fastapi import Request, Response

from reach_commons.app_logging.logger import get_reach_logger

logger = get_reach_logger()


def add_deprecation_headers(
    request: Request,
    response: Response,
    added_date: datetime.datetime,
    deprecation_period_days: int = 180,
    replacement_url: str = None,
):
    """
    Adds deprecation headers to the response and logs deprecation information.

    Args:
        request (Request): The HTTP request object.
        response (Response): The HTTP response object.
        added_date (datetime.datetime): The date when deprecation was announced.
        deprecation_period_days (int): Number of days before the endpoint is removed (default: 180).
        replacement_url (str, optional): URL of the replacement endpoint, if available.
    """
    removal_date = added_date + datetime.timedelta(days=deprecation_period_days)
    removal_date_str = removal_date.strftime("%a, %d %b %Y %H:%M:%S GMT")
    current_date = datetime.datetime.utcnow()

    path = request.url.path if request else "Unknown Path"
    method = request.method if request else "Unknown Method"

    deprecation_warning = f'299 "{method} {path}" is deprecated and will be removed on [{removal_date_str}]"'

    response.headers["Deprecation-Warning"] = deprecation_warning

    if replacement_url:
        response.headers["Replacement-Endpoint"] = replacement_url

    if current_date < removal_date:
        logger.warning(
            f"Deprecated endpoint accessed: {method} {path}. "
            f"Deprecation period ends on {removal_date_str}."
            + (f" Replacement endpoint: {replacement_url}" if replacement_url else "")
        )

    elif current_date >= removal_date:
        logger.warning(
            f"Access to removed endpoint: {method} {path}. "
            f"Removal date was {removal_date_str}."
            + (f" Replacement endpoint: {replacement_url}" if replacement_url else "")
        )
