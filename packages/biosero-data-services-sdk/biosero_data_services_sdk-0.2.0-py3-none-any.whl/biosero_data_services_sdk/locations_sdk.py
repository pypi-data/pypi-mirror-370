import logging
from typing import Literal
from typing import overload

from .exceptions import SeeminglyInfiniteLocationPathError
from .models import DataServicesIdentity
from .models import DataServicesLocation
from .sdk_base import SdkBase
from .types import IdentityId
from .types import LocationPath

logger = logging.getLogger(__name__)


class LocationsSdk(SdkBase):
    def get_identities_at_location(
        self, location_id: str, *, confirm_location_exists: bool = True
    ) -> list[DataServicesIdentity]:
        if confirm_location_exists:
            _ = self.get_identity_by_id(location_id)
        limit = 999999  # arbitrarily large number
        response = self._get_query(f"QueryService/ItemsAtLocation?locationId={location_id}&limit={limit}")
        assert isinstance(response, list), f"Expected a list, got {type(response)} with value {response}"
        identity_list: list[DataServicesIdentity] = []
        for item in response:
            assert isinstance(item, dict), f"Expected a dict, got {type(item)} with value {item}"
            identity = DataServicesIdentity.from_api_response(item)
            identity_list.append(identity)
        return identity_list

    def get_identity_location_by_id(
        self, id: str, *, locations_cache: dict[IdentityId, DataServicesLocation] | None = None
    ) -> DataServicesLocation:
        if locations_cache is None:
            locations_cache = {}
        if id in locations_cache:
            return locations_cache[id]
        response = self._get_query(f"QueryService/Location?itemId={id}")
        assert isinstance(response, dict), f"Expected a dict, got {type(response)} with value {response}"
        location = DataServicesLocation.from_api_response(response)
        locations_cache[id] = location
        return location

    def _get_identity_location_path(
        self,
        id: str,
        *,
        locations_cache: dict[IdentityId, DataServicesLocation] | None = None,
        break_condition_location: set[str] | None = None,
    ) -> list[IdentityId]:
        # the Data Services API call for /LocationPath errors out consistently
        # This will return a list of identities starting with the immediate parent, up to the point where an identity has no known parent
        location_path: list[IdentityId] = [id]
        if break_condition_location is None:
            break_condition_location = set()
        max_depth = 99  # Arbitrary maximum depth to avoid infinite loops
        while True:
            if len(location_path) > max_depth:
                raise SeeminglyInfiniteLocationPathError(original_id=id, location_path=location_path)
            location = self.get_identity_location_by_id(location_path[-1], locations_cache=locations_cache)
            if location.parent_identity_id is None:
                break
            location_path.append(location.parent_identity_id)
            if location.parent_identity_id in break_condition_location:
                break

        return list(reversed(location_path))

    @overload
    def does_identity_location_path_contain(  # pragma: no cover # this is a type definition
        self,
        *,
        identity_id: str,
        ancestor_location_ids: set[str],
        include_location_path_in_return: Literal[False],
        locations_cache: dict[IdentityId, DataServicesLocation] | None = None,
    ) -> bool: ...
    @overload
    def does_identity_location_path_contain(  # pragma: no cover # this is a type definition
        self,
        *,
        identity_id: str,
        ancestor_location_ids: set[str],
        locations_cache: dict[IdentityId, DataServicesLocation] | None = None,
    ) -> bool: ...
    @overload
    def does_identity_location_path_contain(  # pragma: no cover # this is a type definition
        self,
        *,
        identity_id: str,
        ancestor_location_ids: set[str],
        include_location_path_in_return: Literal[True],
        locations_cache: dict[IdentityId, DataServicesLocation] | None = None,
    ) -> tuple[bool, LocationPath]: ...
    def does_identity_location_path_contain(
        self,
        *,
        identity_id: str,
        ancestor_location_ids: set[str],
        include_location_path_in_return: bool = False,
        locations_cache: dict[IdentityId, DataServicesLocation] | None = None,
    ):
        """Check if an identity is located within a child location of a given ancestor location.

        This can reduce the number of API calls required compared to getting the full location path.
        """
        path = self._get_identity_location_path(
            id=identity_id, break_condition_location=ancestor_location_ids, locations_cache=locations_cache
        )
        is_contained = path[0] in ancestor_location_ids
        if include_location_path_in_return:
            return is_contained, path
        return is_contained

    def get_identity_location_path(
        self, id: str, *, locations_cache: dict[IdentityId, DataServicesLocation] | None = None
    ) -> list[IdentityId]:
        return self._get_identity_location_path(id=id, locations_cache=locations_cache)
