import datetime
import json
import logging
from pathlib import Path
from typing import cast

import requests
from pydantic import JsonValue

from .exceptions import DataServicesApiError
from .exceptions import EventDoesNotExistError
from .exceptions import InvalidEventQueryParametersError
from .models import DataServicesEvent
from .reports import EventUploadReport
from .sdk_base import SdkBase
from .types import EventId

logger = logging.getLogger(__name__)


class EventsSdk(SdkBase):
    def publish_event(self, event: DataServicesEvent, *, explicitly_set_id: bool = False) -> EventId:
        # Although the Swagger documentation says that the `data` field is nullable, we seem to get errors trying to publish an event with no data...unclear if we should refactor to assume it's non-nullable in all cases or just leave as-is

        payload = event.to_api_request()
        # Although the Swagger documentation says that the `createdDateUtc` field can be supplied, it doesn't seem to be respected when supplied
        _ = payload.pop("createdDateUtc", None)
        if not explicitly_set_id:
            _ = payload.pop("eventId", None)

        response = self._post_request(query="EventService", payload=payload)
        assert isinstance(response, str), f"Expected a string, got {type(response)} with value {response}"
        return response

    def get_events(
        self, *, start: datetime.datetime | None = None, end: datetime.datetime | None = None, topic: str | None = None
    ) -> list[DataServicesEvent]:
        payload: dict[str, JsonValue] = {}
        if start is not None:
            payload["start"] = start.isoformat()
        if end is not None:
            payload["end"] = end.isoformat()
        if topic is not None:
            payload["topic"] = topic
        if not payload:
            raise InvalidEventQueryParametersError
        response = self._post_request(query="QueryService/Events", payload=payload)
        assert isinstance(response, list), f"Expected a list, got {type(response)} with value {response}"
        event_list: list[DataServicesEvent] = []
        for item in response:
            assert isinstance(item, dict), f"Expected a dict, got {type(item)} with value {item}"
            event = DataServicesEvent.from_api_response(item)
            event_list.append(event)
        return event_list

    def get_event_by_id(self, event_id: str) -> DataServicesEvent:
        try:
            response = self._get_query(f"events/{event_id}", api_version=3)
        except DataServicesApiError as e:
            if e.status_code == requests.codes.not_found and "Event with EventId" in e.body:
                raise EventDoesNotExistError(event_id) from e
            raise  # pragma: nocover # not sure how to test this defensive statement
        assert isinstance(response, dict), f"Expected a dict, got {type(response)} with value {response}"
        return DataServicesEvent.from_api_response(response)

    def upload_events_from_file(self, savepoint_dir: Path, *, preview: bool = False) -> EventUploadReport:
        all_events_json_files = sorted(savepoint_dir.rglob("*events*.json"))
        report = EventUploadReport()
        for json_file in all_events_json_files:
            with json_file.open() as f:
                json_data = json.load(f)
            assert isinstance(json_data, list), f"Expected list but got type {type(json_data)} for file {json_file}"
            num_events_in_file = len(json_data)  # pyright: ignore[reportUnknownArgumentType] # we're loading in JSON and then asserting about it
            for idx, event_json in enumerate(json_data):  # pyright: ignore[reportUnknownArgumentType,reportUnknownVariableType] # we're loading in JSON and then asserting about it
                event_json = cast(dict[str, JsonValue], event_json)
                assert isinstance(event_json, dict), f"Expected dict but got type {type(event_json)} for {event_json}"
                event_in_file = DataServicesEvent.from_api_response(event_json)
                logger.info(
                    f"Processing event {event_in_file.id} from file {json_file} for upload. {idx + 1}/{num_events_in_file} in file"
                )
                matching_existing_event: DataServicesEvent | None = None
                try:
                    matching_existing_event = self.get_event_by_id(event_in_file.id)
                except EventDoesNotExistError:
                    matching_existing_event = None

                if matching_existing_event is None:
                    if not preview:
                        _ = self.publish_event(event_in_file, explicitly_set_id=True)
                    report.created.append(event_in_file.id)
                    continue
                fields_to_exclude = {"created_at", "original_full_json_string"}
                existing_event_fields = matching_existing_event.model_dump(exclude=fields_to_exclude)
                event_in_file_fields = event_in_file.model_dump(exclude=fields_to_exclude)
                if existing_event_fields == event_in_file_fields:
                    report.untouched.append(event_in_file.id)
                    continue
                report.conflicts.append(event_in_file.id)

        return report
