import logging
from functools import partial
from typing import NamedTuple

from pydantic import JsonValue

from .constants import BIOSERO_CONTAINER_IDENTITY_TYPE_ID
from .constants import BIOSERO_MATERIAL_IDENTITY_TYPE_ID
from .constants import BIOSERO_SAMPLE_IDENTITY_TYPE_ID
from .constants import WASTE_LOCATION_ID
from .events_sdk import EventsSdk
from .exceptions import DataRecordOverflowError
from .exceptions import IdentityIsNotContainerError
from .exceptions import IdentityIsNotSubstanceError
from .identities_sdk import IdentitiesSdk
from .locations_sdk import LocationsSdk
from .models import DataServicesContainer
from .models import DataServicesIdentity
from .models import DataServicesLocation
from .models import DataServicesMaterialInContainer
from .models import DataServicesSampleInContainer
from .models import NullContainerIdError
from .models import VolumeAmount
from .orders_sdk import OrdersSdk
from .reports import ReportsSdk
from .transportation_sdk import TransportationSdk
from .types import IdentityId
from .types import IdentityName
from .types import LocationPath
from .types import RequestWithOffset

logger = logging.getLogger(__name__)

IS_IN_WASTE_PROPERTY_NAME = "is_in_waste"
IS_IN_WASTE_PROPERTY_VALUE = "True"


class InWasteResponse(NamedTuple):
    is_in_waste: bool
    location_path: LocationPath | None


class ItemsInWasteCache:
    # This cache can persist, because the assumption is that once something is in Waste, it will never leave Waste.
    def __init__(self):
        super().__init__()
        self._items_in_waste: set[IdentityId] = set()

    @property
    def items_in_waste(self) -> frozenset[IdentityId]:
        return frozenset(self._items_in_waste)

    def is_item_in_waste(
        self,
        identifier: str,
        *,
        locations_cache: dict[IdentityId, DataServicesLocation] | None = None,
        identities_cache: dict[IdentityId, DataServicesIdentity] | None = None,
    ) -> InWasteResponse:
        """Check if the item is in Waste.

        If it's already in the Waste cache, then it will return True and None for the location path.
        If it is not yet in the Waste Cache, then it will look up the location path to see. If the Location doesn't specify that it's in Waste, then it will check the Identity of the container for the is_in_waste property to determine if it's in waste.
        If it is in Waste, it will return True and None for the loctaion path (since it's not actually the full location path...and also would only be available on initial calls and not cached hits).
        If it is not in Waste, it will return False and the full location path.
        """
        if identifier in self._items_in_waste:
            return InWasteResponse(is_in_waste=True, location_path=None)
        sdk = DataServicesSdk()
        is_in_waste, location_path = sdk.does_identity_location_path_contain(
            identity_id=identifier,
            ancestor_location_ids={
                WASTE_LOCATION_ID,
                # TODO: remove these hardcoded locations as part of https://lab-sync.atlassian.net/browse/LSP011-249
                "Sharps Bin 1",
                "Sharps Bin 2",
                "Sharps Bin 3",
                "Sharps Bin 4",
                "Recyclable Bin 1",
                "Recyclable Bin 2",
                "Recyclable Bin 3",
                "Chemical Waste Drum",
            },
            include_location_path_in_return=True,
            locations_cache=locations_cache,
        )

        if not is_in_waste:
            identity = sdk.get_identity_by_id(identifier, identities_cache=identities_cache)
            if identity.has_property(IS_IN_WASTE_PROPERTY_NAME):
                is_in_waste_property_value = identity.get_property_value(IS_IN_WASTE_PROPERTY_NAME)
                if is_in_waste_property_value == IS_IN_WASTE_PROPERTY_VALUE:
                    is_in_waste = True
        if is_in_waste:
            self._items_in_waste.add(identifier)
            location_path = None

        return InWasteResponse(is_in_waste, location_path)


_items_in_waste_cache = ItemsInWasteCache()


def get_items_in_waste_cache() -> ItemsInWasteCache:
    return _items_in_waste_cache


def clear_items_in_waste_cache() -> None:
    global _items_in_waste_cache  # noqa: PLW0603 # yes, it's a global, but we need a singleton cache
    _items_in_waste_cache = ItemsInWasteCache()


def _parse_container_list_from_response(response: JsonValue) -> list[DataServicesContainer]:
    assert isinstance(response, list), f"Expected a list, got {type(response)} with value {response}"
    container_list: list[DataServicesContainer] = []
    for item in response:
        assert isinstance(item, dict), f"Expected a dict, got {type(item)} with value {item}"
        try:
            container = DataServicesContainer.from_api_response(item)
        except NullContainerIdError as e:
            logger.warning(f"Skipping container with null ID: {e}")
            continue

        container_list.append(container)
    return container_list


def get_all_data(*, request: RequestWithOffset, limit: int, max_limit: int = 999999) -> list[JsonValue]:
    all_data: list[JsonValue] = []
    offset = 0
    while len(all_data) < max_limit:
        response = request(offset=offset)
        assert isinstance(response, list), f"Expected a list, got {type(response)} with value {response}"
        all_data.extend(response)
        if len(response) < limit:
            break
        offset += len(response)
    else:
        raise DataRecordOverflowError(max_limit=max_limit, request=request)
    return all_data


# view all identities: curl "http://localhost:8105/api/v3.0/identities?limit=99999"
# view all events: curl -X POST "http://10.73.26.8:8105/api/v2.0/QueryService/Events?limit=99999" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"start\": \"2022-07-02T13:24:27.216Z\"}"
# view liquid transfer events: curl -X POST "http://10.73.26.8:8105/api/v2.0/QueryService/Events?limit=99999" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"topic\": \"Biosero.DataModels.Events.LiquidTransferEvent\"}"
# view location changed events: # view liquid transfer events: curl -X POST "http://10.73.26.8:8105/api/v2.0/QueryService/Events?limit=99999" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"topic\": \"Biosero.DataModels.Events.LocationChangedEvent\"}"
# Check config via UI: http://localhost:8106/configuration
# Swagger UI: http://localhost:8107/swagger/index.html


class DataServicesSdk(ReportsSdk, LocationsSdk, OrdersSdk, EventsSdk, TransportationSdk, IdentitiesSdk):
    def get_software_version(self) -> str:
        version = self._get_query("version")
        assert isinstance(version, str), f"Expected a string, got {type(version)} with value {version}"
        return version

    def _filter_out_containers_in_waste(
        self,
        *,
        container_list: list[DataServicesContainer],
        exclude_containers_in_waste: bool,
        locations_cache: dict[IdentityId, DataServicesLocation] | None = None,
        identities_cache: dict[IdentityId, DataServicesIdentity] | None = None,
    ) -> list[DataServicesContainer]:
        if not exclude_containers_in_waste:
            return container_list
        containers_not_in_waste: list[DataServicesContainer] = []
        for container in container_list:
            is_in_waste, location_path = get_items_in_waste_cache().is_item_in_waste(
                container.identity_id, locations_cache=locations_cache, identities_cache=identities_cache
            )
            if is_in_waste:
                continue
            container.location_path_as_ids = location_path
            containers_not_in_waste.append(container)
        return containers_not_in_waste

    def get_sample_containers_by_name(
        self,
        name: str,
        *,
        exclude_containers_in_waste: bool = False,
        locations_cache: dict[IdentityId, DataServicesLocation] | None = None,
        identities_cache: dict[IdentityId, DataServicesIdentity] | None = None,
    ) -> list[DataServicesContainer]:
        limit = 25000  # some samples come in big batches
        request = partial(self._post_request, query=f"QueryService/FindSample?limit={limit}", payload={"name": name})
        container_list = _parse_container_list_from_response(get_all_data(request=request, limit=limit))
        return self._filter_out_containers_in_waste(
            container_list=container_list,
            exclude_containers_in_waste=exclude_containers_in_waste,
            locations_cache=locations_cache,
            identities_cache=identities_cache,
        )

    def get_material_containers_by_name(
        self,
        name: str,
        *,
        exclude_containers_in_waste: bool = False,
        locations_cache: dict[IdentityId, DataServicesLocation] | None = None,
        identities_cache: dict[IdentityId, DataServicesIdentity] | None = None,
    ) -> list[DataServicesContainer]:
        limit = 25000  # some reagents are made in very big batches
        request = partial(self._post_request, query=f"QueryService/FindMaterial?limit={limit}", payload={"name": name})
        container_list = _parse_container_list_from_response(get_all_data(request=request, limit=limit))
        return self._filter_out_containers_in_waste(
            container_list=container_list,
            exclude_containers_in_waste=exclude_containers_in_waste,
            locations_cache=locations_cache,
            identities_cache=identities_cache,
        )

    def get_substance_containers_by_name(
        self,
        info: IdentityName | DataServicesIdentity,
        *,
        exclude_containers_in_waste: bool = False,
        locations_cache: dict[IdentityId, DataServicesLocation] | None = None,
        identities_cache: dict[IdentityId, DataServicesIdentity] | None = None,
    ) -> list[DataServicesContainer]:
        identity_type = "needs to be queried"
        if isinstance(info, DataServicesIdentity):
            assert info.name is not None, f"Identity name must not be None. Provided Identity: {info}"
            name = info.name
            identity_type = info.parent_id
        else:
            name = info
        if identity_type == "needs to be queried":
            if self.is_identity_name_a_child_of(name=name, parent_id=BIOSERO_MATERIAL_IDENTITY_TYPE_ID):
                identity_type = BIOSERO_MATERIAL_IDENTITY_TYPE_ID
            elif self.is_identity_name_a_child_of(name=name, parent_id=BIOSERO_SAMPLE_IDENTITY_TYPE_ID):
                identity_type = BIOSERO_SAMPLE_IDENTITY_TYPE_ID

        if identity_type == BIOSERO_MATERIAL_IDENTITY_TYPE_ID:
            return self.get_material_containers_by_name(
                name,
                exclude_containers_in_waste=exclude_containers_in_waste,
                locations_cache=locations_cache,
                identities_cache=identities_cache,
            )
        if identity_type == BIOSERO_SAMPLE_IDENTITY_TYPE_ID:
            return self.get_sample_containers_by_name(
                name,
                exclude_containers_in_waste=exclude_containers_in_waste,
                locations_cache=locations_cache,
                identities_cache=identities_cache,
            )
        raise IdentityIsNotSubstanceError(info)

    def get_materials_in_container(self, container_id: IdentityId) -> list[DataServicesMaterialInContainer]:
        # this appears to return both materials and samples...for unknown reasons
        response = self._get_query(f"QueryService/MaterialsInContainer?containerId={container_id}")
        assert isinstance(response, list), f"Expected a list, got {type(response)} with value {response}"
        material_list: list[DataServicesMaterialInContainer] = []
        for item in response:
            assert isinstance(item, dict), f"Expected a dict, got {type(item)} with value {item}"
            material = DataServicesMaterialInContainer.from_api_response(item)
            if material.substance_id == container_id:
                # There have been observed cases where things say they are filled with themself. This happened in the case of a tube rack
                continue
            material_list.append(material)
        return material_list

    def get_samples_in_container(self, container_id: IdentityId) -> list[DataServicesSampleInContainer]:
        # this appears to return both samples and materials...for unknown reasons
        response = self._get_query(f"QueryService/SamplesInContainer?containerId={container_id}")
        assert isinstance(response, list), f"Expected a list, got {type(response)} with value {response}"
        sample_list: list[DataServicesSampleInContainer] = []
        for item in response:
            assert isinstance(item, dict), f"Expected a dict, got {type(item)} with value {item}"
            sample = DataServicesSampleInContainer.from_api_response(item)
            if sample.substance_id == container_id:
                # There have been observed cases where things say they are filled with themself. This happened in the case of a tube rack
                continue
            sample_list.append(sample)
        return sample_list

    def get_liquid_volume_in_container(
        self, container_id: IdentityId, *, identities_cache: dict[IdentityId, DataServicesIdentity] | None = None
    ) -> VolumeAmount:
        if not self.is_identity_a_descendent_of(
            identity_id=container_id, ancestor_id=BIOSERO_CONTAINER_IDENTITY_TYPE_ID, identities_cache=identities_cache
        ):
            raise IdentityIsNotContainerError(info=container_id)
        response = self._get_query(f"QueryService/NetVolume?containerId={container_id}")
        assert isinstance(response, dict), f"Expected a dict, got {type(response)} with value {response}"
        return VolumeAmount(
            amount=response["amount"],  # pyright:ignore[reportArgumentType] # the response is an untyped JSON value, but pyright will typeguard for us
            unit=response["unit"],  # pyright:ignore[reportArgumentType] # the response is an untyped JSON value, but pyright will typeguard for us
        )
