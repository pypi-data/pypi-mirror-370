import json
import logging
import os


class Singleton(type):
    """
    Define an Instance operation that lets clients access its unique
    instance.
    """

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class ReachLogger(metaclass=Singleton):
    logger = logging.getLogger()
    logger.setLevel(os.environ.get("logger_level") or logging.WARNING)
    context = {"logger_identifier": "reach_logger"}

    def set_context(self, **kwargs):
        self.context = {"logger_identifier": "reach_logger", **kwargs}

    # noinspection PyBroadException
    def _log(self, level, msg, *args, **kwargs):
        log_message = {**self.context, "level": logging.getLevelName(level)}

        if isinstance(msg, dict):
            log_message.update(msg)
        else:
            log_message["message"] = str(msg)

        if args and isinstance(args[0], dict):
            log_message.update(args[0])
        try:
            log_message_json = json.dumps(log_message)
        except Exception:
            log_message_json = str(log_message)

        self.logger.log(level, log_message_json, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._log(logging.INFO, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._log(logging.ERROR, msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self._log(logging.DEBUG, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._log(logging.WARNING, msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self._log(logging.ERROR, msg, *args, **kwargs)

    # noinspection PyPep8Naming
    def setLevel(self, level: str):
        self.logger.setLevel(level=level or logging.WARNING)


logger = ReachLogger()


def set_business_id(business_id, pos_partner, level=logging.WARNING):
    logger.set_context(business=business_id, partner=pos_partner)
    logger.setLevel(level)


def get_reach_logger():
    return logger
