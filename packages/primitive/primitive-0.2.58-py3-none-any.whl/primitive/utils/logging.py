import json
from datetime import timezone
from functools import wraps

from loguru import logger


def log_context(**context):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with logger.contextualize(**context):
                return func(*args, **kwargs)

        return wrapper

    return decorator


def fmt(record) -> str:
    extra = record["extra"]
    label = extra.get("label", None)
    tag = extra.get("tag", None)
    type = extra.get("type", "system")

    context_object = {
        "label": label,
        "type": type,
        "utc": record["time"]
        .astimezone(timezone.utc)
        .strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
        "level": record["level"].name,
        "name": record["name"],
        "function": record["function"],
        "line": record["line"],
        "message": record["message"],
    }

    if tag:
        context_object["tag"] = tag

    # Loguru will fail if you return a string that doesn't select
    # something within its record
    record["extra"]["serialized"] = json.dumps(context_object)
    return "{extra[serialized]}\n"
