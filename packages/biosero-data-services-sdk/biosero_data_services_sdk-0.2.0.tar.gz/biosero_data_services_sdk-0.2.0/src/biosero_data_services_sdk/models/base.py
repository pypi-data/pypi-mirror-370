import json
from typing import Self

from pydantic import BaseModel
from pydantic import Field
from pydantic import JsonValue


class DataServicesModel(BaseModel):
    original_full_json_string: str | None = Field(default=None, exclude=True)

    @property
    def full_response_dict(self) -> dict[str, JsonValue]:
        # this needs to be a property so that Strawberry doesn't try and include it
        return self._full_response_dict

    def set_full_response_dict(self, response: dict[str, JsonValue]) -> None:
        self._full_response_dict = response
        self.original_full_json_string = json.dumps(response)

    @classmethod
    def from_api_response(cls, response: dict[str, JsonValue]) -> Self:
        raise NotImplementedError(
            "Subclasses must implement from_api_response method...it's hard to use Abstract Base Class with Pydantic models"
        )
