import datetime
import json
from typing import Any
from typing import Self
from typing import override
from uuid import uuid4

from pydantic import Field
from pydantic import JsonValue
from pydantic import field_serializer
from pydantic import field_validator

from .base import DataServicesModel


class DataServicesEvent(DataServicesModel):
    id: str = Field(default_factory=lambda: str(uuid4()), serialization_alias="eventId")
    topic: str
    orchestrator_id: str | None = Field(default=None, serialization_alias="orchestratorId")
    operator_id: str | None = Field(default=None, serialization_alias="operatorId")
    data: dict[str, JsonValue] | None = None
    start: datetime.datetime
    end: datetime.datetime
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(tz=datetime.UTC), serialization_alias="createdDateUtc"
    )

    def to_api_request(self) -> dict[str, JsonValue]:
        data: dict[str, JsonValue] = (
            json.loads(self.original_full_json_string) if self.original_full_json_string is not None else {}
        )
        model_dump = json.loads(
            self.model_dump_json(by_alias=True)
        )  # unless fully dumping to json, the field serializers will be used even for regular attributes

        # merge in values in the model to the full API response
        data.update(model_dump.items())
        return data

    @field_serializer("data", when_used="json")
    def serialize_data(self, data: dict[str, JsonValue] | None) -> str | None:
        return json.dumps(data, separators=(",", ":")) if data is not None else None

    @field_serializer("start", "end", "created_at", when_used="json")
    def serialize_datetime(self, dt: datetime.datetime) -> str:
        return dt.isoformat()

    @property
    def api_formatted_start(self) -> str:
        return self.start.isoformat()

    @property
    def api_formatted_end(self) -> str:
        return self.end.isoformat()

    @override
    @classmethod
    def from_api_response(cls, response: dict[str, JsonValue]) -> Self:
        assert "eventId" in response, f'Expected an "eventId" key in the response, got {response}'
        identifier = response["eventId"]
        assert isinstance(identifier, str), f"Expected a string, got {type(identifier)} with value {identifier}"

        assert "topic" in response, f'Expected a "topic" key in the response, got {response}'
        topic = response["topic"]
        assert isinstance(topic, str), f"Expected a string, got {type(topic)} with value {topic}"

        assert "orchestratorId" in response, f'Expected an "orchestratorId" key in the response, got {response}'
        orchestrator_id = response["orchestratorId"]
        assert isinstance(orchestrator_id, str | type(None)), (
            f"Expected a string or None, got {type(orchestrator_id)} with value {orchestrator_id}"
        )

        assert "operatorId" in response, f'Expected an "operatorId" key in the response, got {response}'
        operator_id = response["operatorId"]
        assert isinstance(operator_id, str | type(None)), (
            f"Expected a string or None, got {type(operator_id)} with value {operator_id}"
        )

        assert "createdDateUtc" in response, f'Expected a "createdDateUtc" key in the response, got {response}'
        created_at_str = response["createdDateUtc"]
        assert isinstance(created_at_str, str), (
            f"Expected a string, got {type(created_at_str)} with value {created_at_str}"
        )
        created_at = datetime.datetime.fromisoformat(created_at_str)

        assert "start" in response, f'Expected a "start" key in the response, got {response}'
        start_str = response["start"]
        assert isinstance(start_str, str), f"Expected a string, got {type(start_str)} with value {start_str}"
        start = datetime.datetime.fromisoformat(start_str)

        assert "end" in response, f'Expected an "end" key in the response, got {response}'
        end_str = response["end"]
        assert isinstance(end_str, str), f"Expected a string, got {type(end_str)} with value {end_str}"
        end = datetime.datetime.fromisoformat(end_str)

        data: dict[str, JsonValue] | None = None
        assert "data" in response, f'Expected a "data" key in the response, got {response}'
        raw_data = response["data"]
        assert isinstance(raw_data, str | type(None)), (
            f"Expected a string or None, got {type(raw_data)} with value {raw_data}"
        )
        if raw_data is not None:
            data = json.loads(raw_data)

        obj = cls(
            id=identifier,
            data=data,
            topic=topic,
            created_at=created_at,
            start=start,
            end=end,
            orchestrator_id=orchestrator_id,
            operator_id=operator_id,
        )
        obj.set_full_response_dict(response)
        return obj


LOCATION_CHANGED_EVENT_TOPIC = "Biosero.DataModels.Events.LocationChangedEvent"
LIQUID_TRANSFER_EVENT_TOPIC = "Biosero.DataModels.Events.LiquidTransferEvent"


class LocationChangedEvent(DataServicesEvent):
    topic: str = LOCATION_CHANGED_EVENT_TOPIC
    # These fields are excluded from serialization because they are used internally to populate the `data` field
    parent_id: str = Field(exclude=True)
    item_id: str = Field(exclude=True)
    coordinates: str | None = Field(default=None, exclude=True)

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, v: str) -> str:
        expected_topic = LOCATION_CHANGED_EVENT_TOPIC
        if v != expected_topic:
            raise ValueError(  # noqa: TRY003 # pydantic requires using ValueError within validation
                f"Expected topic to be '{expected_topic}', got {v}"
            )
        return v

    @override
    def model_post_init(self, context: Any) -> None:
        if self.data is not None:
            raise ValueError(  # noqa: TRY003 # pydantic requires using ValueError within validation
                f"data must not be manually set, it will be auto populated based on other inputs. {self.data} was provided."
            )
        self.data = {
            "parentIdentifier": self.parent_id,
            "itemIdentifier": self.item_id,
            "coordinates": self.coordinates,
        }
        return super().model_post_init(context)


class LiquidTransferEvent(DataServicesEvent):
    topic: str = LIQUID_TRANSFER_EVENT_TOPIC
    source_id: str = Field(exclude=True)
    destination_id: str = Field(exclude=True)
    actual_transfer_volume: float = Field(exclude=True, ge=0)
    volume_unit: str = Field(default="uL", exclude=True)

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, v: str) -> str:
        expected_topic = LIQUID_TRANSFER_EVENT_TOPIC
        if v != expected_topic:
            raise ValueError(  # noqa: TRY003 # pydantic requires using ValueError within validation
                f"Expected topic to be '{expected_topic}', got {v}"
            )
        return v

    @override
    def model_post_init(self, context: Any) -> None:
        if self.data is not None:
            raise ValueError(  # noqa: TRY003 # pydantic requires using ValueError within validation
                f"data must not be manually set, it will be auto populated based on other inputs. {self.data} was provided."
            )
        self.data = {
            "sourceIdentifier": self.source_id,
            "destinationIdentifier": self.destination_id,
            "actualTransferVolume": {
                "amount": self.actual_transfer_volume,
                "unit": self.volume_unit,
            },
        }
        return super().model_post_init(context)
