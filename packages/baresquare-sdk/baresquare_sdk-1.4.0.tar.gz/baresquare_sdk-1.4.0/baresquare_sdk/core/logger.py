import json
import logging
import sys

from baresquare_sdk.settings import get_settings


def get_request_context():
    """Get the entire request context dictionary."""
    try:
        main_module = sys.modules.get("app.main")
        if main_module and hasattr(main_module, "request_context"):
            try:
                context = main_module.request_context.get()
                return context if context is not None else {}
            except LookupError:
                return {}
            except Exception:
                return {}
        return {}
    except Exception:
        return {}


class JSONFormatter(logging.Formatter):
    def __init__(self, extra_fields=None):
        super().__init__()
        self.extra_fields = extra_fields or {}

    def format(self, record):
        log_record = {"level": record.levelname}
        settings = get_settings()
        if settings.pl_env != "dev":
            log_record["env"] = settings.pl_env
            log_record["service"] = settings.pl_service
        if record.exc_info:
            log_record["exception"] = sanitise_secrets(self.formatException(record.exc_info))

        # file (instead of the default filename) is used in datadog alerts
        log_record["file"] = record.filename

        # Add custom fields provided in extra_fields
        log_record.update(self.extra_fields)

        # Add request_context params to log_record
        context = get_request_context()
        if context:
            log_record.update(context)

        # Update with log-specific fields
        if record.__dict__:
            log_record.update(record.__dict__)

        # A few third party libraries (e.g. requests) have non-serializable objects in their logs
        # Results is that we are getting  --- Logging error --- in the logs which is super spam
        for key, value in record.__dict__.items():
            try:
                json.dumps(value)  # Check if value is JSON serializable
                log_record[key] = value
            except TypeError:
                log_record[key] = str(value)

        log_record = sanitise_secrets(log_record)
        return json.dumps(log_record)


class JSONLogger(logging.Logger):
    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stack_level=1):
        if extra is None:
            extra = {}
        if isinstance(extra, dict):
            extra = {**extra}
        super()._log(level, msg, args, exc_info, extra, stack_info, stack_level)


def setup_logger(extra_fields=None):
    logging.setLoggerClass(JSONLogger)

    # Remove all handlers associated with the root logger object
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Configure the root logger with a single JSON formatter
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter(extra_fields))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # Configure all other loggers to use the same JSON formatter and set level to WARNING
    for logger_name in logging.root.manager.loggerDict:
        log = logging.getLogger(logger_name)
        log.setLevel(logging.WARNING)
        for h in log.handlers:
            h.setFormatter(JSONFormatter(extra_fields))

    return logger


logger = setup_logger()


def sanitise_secret(input_key, input_value):
    key_str = str(input_key).lower()
    if key_str == "authentication":
        return "*REDACTED*"
    if key_str in ["authorization", "authorisation"]:
        return "*REDACTED*" + str(input_value)[-3:]
    if key_str == "client_secret":
        return "*REDACTED*"
    if key_str == "password":
        return "*REDACTED*"
    return input_value


def sanitise_secrets(input_obj):
    """Walk a possibly complex JSON object and return a *copy* of the original JSON object with secrets redacted.

    Example:
        - input: {"password": "value-password"}
        - output: {"password": "*REDACTED*"}

    Note that, since the method returns a copy of the input, passing a big JSON object may consume a lot of memory
    """
    if isinstance(input_obj, dict):
        modified_obj = {}
        for key, value in input_obj.items():
            modified_value = sanitise_secret(key, value)
            if isinstance(value, (dict, list)):
                modified_value = sanitise_secrets(value)
            modified_obj[key] = modified_value
        return modified_obj
    if isinstance(input_obj, list):
        modified_value = []
        for item in input_obj:
            if isinstance(item, dict):
                modified_value.append(sanitise_secrets(item))
            else:
                modified_value.append(item)
        return modified_value

    return input_obj


if __name__ == "__main__":
    # Example of adding extra fields during setup
    xf = {"app_version": "1.2.3", "team": "platform"}
    my_logger = setup_logger(xf)
    my_logger.info("Application started")
