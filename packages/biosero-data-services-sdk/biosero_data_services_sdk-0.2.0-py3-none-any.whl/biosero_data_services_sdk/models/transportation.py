import datetime
from enum import StrEnum
from typing import Self
from typing import override

from pydantic import JsonValue

from .base import DataServicesModel


class TransportationRequestStatus(StrEnum):
    CREATED = "Created"
    STARTED = "Started"
    ITEM_NOT_AVAILABLE_AT_SOURCE = "ItemNotAvailableAtSource"
    SPACE_NOT_AVAILABLE_AT_DESTINATION = "SpaceNotAvailableAtDestination"
    NO_VEHICLE_AVAILABLE = "NoVehicleAvailable"
    VEHICLE_ASSIGNED = "VehicleAssigned"
    VEHICLE_MOVING_TO_PICKUP = "VehicleMovingToPickup"
    VEHICLE_AT_PICKUP = "VehicleAtPickup"
    BEFORE_PICKUP = "BeforePickup"
    PICKUP_ACTIVE = "PickupActive"
    AFTER_PICKUP = "AfterPickup"
    ITEM_LOADED_ON_VEHICLE = "ItemLoadedOnVehicle"
    VEHICLE_MOVING_TO_DROPOFF = "VehicleMovingToDropoff"
    VEHICLE_AT_DROPOFF = "VehicleAtDropoff"
    BEFORE_DROPOFF = "BeforeDropoff"
    DROPOFF_ACTIVE = "DropoffActive"
    AFTER_DROPOFF = "AfterDropoff"
    DROPOFF_COMPLETE = "DropoffComplete"
    RESET = "Reset"
    ABORTED = "Aborted"
    COMPLETE = "Complete"
    CANCELED = "Canceled"
    ERROR = "Error"
    UNKNOWN = "Unknown"


class DataServicesTransportationRequest(DataServicesModel):
    id: str
    status: TransportationRequestStatus
    source_station_id: str
    item_id: str
    destination_station_id: str
    item_metadata: str | None = None
    status_details: str | None = None
    run_after_date: datetime.datetime

    @override
    @classmethod
    def from_api_response(
        cls,
        response: dict[str, JsonValue],
    ) -> Self:
        assert "requestIdentifier" in response, f"Expected a 'requestIdentifier' key in the response, got {response}"
        request_id = response["requestIdentifier"]
        assert isinstance(request_id, str), (
            f"Expected requestIdentifier to be a string, got {type(request_id)} for {request_id}"
        )

        assert "status" in response, f"Expected a 'status' key in the response, got {response}"
        status = response["status"]
        assert isinstance(status, str), f"Expected status to be a string, got {type(status)} for {status}"
        status_enum = TransportationRequestStatus(status)

        assert "sourceStationIdentifier" in response, (
            f"Expected a 'sourceStationIdentifier' key in the response, got {response}"
        )
        source_station_id = response["sourceStationIdentifier"]
        assert isinstance(source_station_id, str), (
            f"Expected sourceStationIdentifier to be a string, got {type(source_station_id)} for {source_station_id}"
        )

        assert "itemIdentifier" in response, f"Expected a 'itemIdentifier' key in the response, got {response}"
        item_id = response["itemIdentifier"]
        assert isinstance(item_id, str), f"Expected itemIdentifier to be a string, got {type(item_id)} for {item_id}"

        assert "destinationStationIdentifier" in response, (
            f"Expected a 'destinationStationIdentifier' key in the response, got {response}"
        )
        destination_station_id = response["destinationStationIdentifier"]
        assert isinstance(destination_station_id, str), (
            f"Expected destinationStationIdentifier to be a string, got {type(destination_station_id)} for {destination_station_id}"
        )

        item_metadata = None
        if "itemMetadata" in response:
            item_metadata = response["itemMetadata"]
            assert isinstance(item_metadata, (str, type(None))), (
                f"Expected itemMetadata to be a string or None, got {type(item_metadata)} for {item_metadata}"
            )

        status_details = None
        if "statusDetails" in response:
            status_details = response["statusDetails"]
            assert isinstance(status_details, (str, type(None))), (
                f"Expected statusDetails to be a string or None, got {type(status_details)} for {status_details}"
            )

        assert "runAfterDateUtc" in response, f"Expected a 'runAfterDateUtc' key in the response, got {response}"
        run_after_date_str = response["runAfterDateUtc"]
        assert isinstance(run_after_date_str, str), (
            f"Expected runAfterDateUtc to be a string, got {type(run_after_date_str)} for {run_after_date_str}"
        )
        run_after_date = datetime.datetime.fromisoformat(run_after_date_str)

        obj = cls(
            id=request_id,
            status=status_enum,
            source_station_id=source_station_id,
            item_id=item_id,
            destination_station_id=destination_station_id,
            item_metadata=item_metadata,
            status_details=status_details,
            run_after_date=run_after_date,
        )
        obj.set_full_response_dict(response)
        return obj
