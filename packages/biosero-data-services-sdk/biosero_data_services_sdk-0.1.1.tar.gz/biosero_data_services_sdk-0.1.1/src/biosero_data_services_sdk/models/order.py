from enum import StrEnum
from typing import Self
from typing import override

from pydantic import Field
from pydantic import JsonValue

from .base import DataServicesModel
from .order_template import OrderParameter
from .order_template import parse_input_parameters_from_response


class OrderStatus(StrEnum):
    CREATED = "Created"
    INVALID = "Invalid"
    VALIDATED = "Validated"
    SCHEDULED = "Scheduled"
    RUNNING = "Running"
    PAUSED = "Paused"
    ERROR = "Error"
    COMPLETE = "Complete"
    CANCELED = "Canceled"
    CONSOLIDATED = "Consolidated"
    UNKNOWN = "Unknown"


BAD_ORDER_STATUSES = {OrderStatus.INVALID, OrderStatus.ERROR, OrderStatus.CANCELED}


class Order(DataServicesModel):
    id: str
    input_parameters: list[OrderParameter] = Field(default_factory=list[OrderParameter])
    status: OrderStatus

    @override
    @classmethod
    def from_api_response(cls, response: dict[str, JsonValue]) -> Self:
        assert "identifier" in response, "Order response must contain 'identifier' field"
        identifier = response["identifier"]
        assert isinstance(identifier, str), (
            f"'identifier' field must be a string, got {type(identifier)} for {identifier}"
        )

        assert "status" in response, f"Order response must contain 'status' field: {response}"
        status = response["status"]
        assert isinstance(status, str), f"'status' field must be a string, got {type(status)} for {status}"
        status_enum = OrderStatus(status)

        obj = cls(id=identifier, input_parameters=parse_input_parameters_from_response(response), status=status_enum)
        obj.set_full_response_dict(response)
        return obj
