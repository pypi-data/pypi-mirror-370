from dataclasses import dataclass
from typing import Any

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class JsonAPIResourceSchema:
    id: str

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self.id == other.id

@dataclass_json
@dataclass
class JsonAPIError:
    status: str
    detail: str
    code: str


@dataclass_json
@dataclass
class JsonAPIResourceIdentifier:
    id: str
    type: str

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self.id == other.id and self.type == other.type
