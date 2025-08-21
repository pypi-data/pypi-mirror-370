# standard
import json
from typing import Any

# dj
from django.urls import reverse
from django.http.request import HttpRequest


def absolute_reverse(
    request: HttpRequest,
    view: str,
    args: list | None = None,
    kwargs: dict | None = None,
) -> str:
    return request.build_absolute_uri(reverse(view, args=args, kwargs=kwargs)).replace(
        "127.0.0.1", "localhost"
    )


def is_serializable(value: Any) -> Any:
    try:
        json.dumps(value)
        return True
    except (TypeError, ValueError):
        return False


def clean_json_data(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: clean_json_data(v) for k, v in data.items() if is_serializable(v)}
    elif isinstance(data, list):
        return [clean_json_data(item) for item in data if is_serializable(item)]
    else:
        return data if is_serializable(data) else None
