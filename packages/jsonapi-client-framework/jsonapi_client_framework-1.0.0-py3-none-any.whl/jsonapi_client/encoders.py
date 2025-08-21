from datetime import datetime
from collections.abc import Callable
from typing import Any

import jsonpickle  # type: ignore[import-untyped]

from .parser import Json

JsonValue = str | int | bool | float | Json | None

class JsonEncoder(jsonpickle.handlers.BaseHandler):
    def __init__(self, func: Callable[..., JsonValue]) -> None:
        self.func = func

    def flatten(self, obj: Any, data: dict[str, Any]) -> JsonValue:
        return self.func(obj)

def register(type: type, func: Callable[..., JsonValue]) -> None:
    jsonpickle.handlers.registry.register(type, JsonEncoder(func))

def to_timestamp(obj: datetime) -> float:
    return obj.timestamp()

register(datetime, to_timestamp)
