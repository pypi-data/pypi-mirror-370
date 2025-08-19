import json
import logging
import os
import traceback


class CustomPrefixFilter(logging.Filter):
    def __init__(self, prefix="[ReachLogProcessor]"):
        super().__init__()
        self.prefix = prefix

    def filter(self, record):
        if self.prefix not in record.msg:
            record.msg = f"{self.prefix} {record.msg}"
        return True


def setup_logger(prefix="[ReachLogProcessor]"):
    logger = logging.getLogger(__name__)
    logger.setLevel(os.environ.get("logger_level") or logging.WARNING)

    prefix_filter = CustomPrefixFilter(prefix)
    logger.addFilter(prefix_filter)

    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


logger = setup_logger()


def format_log_message(*params):
    """
    Formats the given parameters into a JSON-like string for better readability in CloudWatch.
    - params: multiple parameters of various types (string, dict, exceptions, etc.).
    """
    log_message = []

    for param in params:
        if isinstance(param, dict):
            try:
                log_message.append(json.dumps(param))
            except Exception:
                log_message.append(str(param))
        elif isinstance(param, Exception):
            log_message.append(traceback.format_exc())
        else:
            log_message.append(str(param))

    return " | ".join(log_message)
