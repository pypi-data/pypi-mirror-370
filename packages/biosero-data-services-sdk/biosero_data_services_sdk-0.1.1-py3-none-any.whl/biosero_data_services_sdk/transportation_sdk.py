import datetime
import logging
from typing import TYPE_CHECKING
from typing import NamedTuple
from urllib.parse import urlparse

import requests

from .constants import BIOSERO_TRANSFER_STATION_IDENTITY_TYPE_ID
from .exceptions import DataServicesApiError
from .exceptions import IdentityIsNotTransferStationError
from .exceptions import TransportationRequestDoesNotExistError
from .identities_sdk import IdentitiesSdk
from .models import DataServicesTransportationRequest
from .models import TransportationRequestStatus

if TYPE_CHECKING:
    from pydantic import JsonValue
logger = logging.getLogger(__name__)


class GbgRemoteConnectionInfo(NamedTuple):
    hostname: str
    port: int
    route: str


class TransportationSdk(IdentitiesSdk):
    def get_gbg_remote_connection_info_for_transfer_station(self, transfer_station_id: str) -> GbgRemoteConnectionInfo:
        if not self.is_identity_a_descendent_of(
            identity_id=transfer_station_id, ancestor_id=BIOSERO_TRANSFER_STATION_IDENTITY_TYPE_ID
        ):
            raise IdentityIsNotTransferStationError(info=transfer_station_id)
        identity = self.get_identity_by_id(transfer_station_id)
        uri = identity.get_property_value("URI", require_value=True)
        parsed_uri = urlparse(uri)
        hostname = parsed_uri.hostname
        assert isinstance(hostname, str), f"Expected hostname to be a string, got type {type(hostname)} for {hostname}"
        port = parsed_uri.port
        assert isinstance(port, int), f"Expected port to be an integer, got type {type(port)} for {port}"
        route = parsed_uri.path
        assert isinstance(route, str), f"Expected route to be a string, got type {type(route)} for {route}"
        return GbgRemoteConnectionInfo(
            hostname=hostname,
            port=port,
            route=route,
        )

    def get_transportation_request(self, request_id: str) -> DataServicesTransportationRequest:
        try:
            response = self._get_query(f"transportation-requests/{request_id}", api_version=3)
        except DataServicesApiError as e:
            if e.status_code == requests.codes.not_found and "TransportationRequestNotFound" in e.body:
                raise TransportationRequestDoesNotExistError(request_id) from e
            raise  # pragma: nocover # not sure how to test this defensive statement
        assert isinstance(response, dict), f"Expected a dict, got {type(response)} with value {response}"
        return DataServicesTransportationRequest.from_api_response(response)

    def get_transportation_requests(self, *, is_active: bool | None = None) -> list[DataServicesTransportationRequest]:
        # TODO: fully paginate
        query_str = "transportation-requests?limit=100"
        if is_active is not None:
            query_str += f"&isActive={str(is_active).lower()}"
        response = self._get_query(query_str, api_version=3)
        assert isinstance(response, list), f"Expected a list, got {type(response)} with value {response}"
        request_list: list[DataServicesTransportationRequest] = []
        for item in response:
            assert isinstance(item, dict), f"Expected a dict, got {type(item)} with value {item}"
            request = DataServicesTransportationRequest.from_api_response(item)
            request_list.append(request)
        return request_list

    def update_transportation_request_status(
        self, *, request_id: str, status: TransportationRequestStatus, status_details: str | None = None
    ) -> None:
        payload: dict[str, JsonValue] = {"status": status.value, "statusDetails": status_details}

        try:
            _ = self._put_request(
                query=f"transportation-requests/{request_id}/status",
                payload=payload,
                api_version=3,
            )
        except DataServicesApiError as e:
            if e.status_code == requests.codes.not_found and "TransportationRequestNotFound" in e.body:
                raise TransportationRequestDoesNotExistError(request_id) from e
            raise  # pragma: nocover # not sure how to test this defensive statement

    def update_transportation_run_after_date(self, *, request_id: str, run_after_date: datetime.datetime) -> None:
        payload: dict[str, JsonValue] = {"runAfterDateUtc": run_after_date.isoformat()}

        try:
            _ = self._put_request(
                query=f"transportation-requests/{request_id}/release",
                payload=payload,
                api_version=3,
            )
        except DataServicesApiError as e:
            if e.status_code == requests.codes.not_found and "TransportationRequestNotFound" in e.body:
                raise TransportationRequestDoesNotExistError(request_id) from e
            raise  # pragma: nocover # not sure how to test this defensive statement
