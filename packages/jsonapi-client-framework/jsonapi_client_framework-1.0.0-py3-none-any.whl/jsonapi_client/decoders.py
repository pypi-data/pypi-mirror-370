from typing import Callable

from dataclasses_json import cfg

def register(type: type, func: Callable) -> None:
    cfg.global_config.decoders[type] = func
