import contextlib
import datetime
import json
import logging
import os
from functools import cached_property
from functools import partial
from time import perf_counter_ns

import requests
from pydantic import BaseModel
from pydantic import Field
from pydantic import JsonValue

from .constants import BIOSERO_DATA_SERVICES_HOSTNAME_ENVVAR_NAME
from .constants import DATA_STORE_ARBITRARY_JSON_ID_BASE
from .constants import DATA_STORE_GENERIC_STATE_ID_BASE
from .constants import DATA_STORE_ROOT_ID_BASE
from .constants import DATA_STORE_TENANT_SUFFIX_ENVVAR_NAME
from .constants import DATA_STORE_TENANT_SUFFIX_LENGTH
from .constants import DEFAULT_DATA_STORE_TENANT_SUFFIX
from .constants import IDENTITY_ROOT_ID
from .exceptions import DataServicesApiError
from .exceptions import DataStoreArbitraryJsonIdentityMissingError
from .exceptions import DataStoreRootIdentityMissingError
from .exceptions import IdentityAlreadyExistsError
from .exceptions import IdentityDoesNotExistError
from .models import DataServicesIdentity
from .models import DataServicesIdentityProperty
from .models import IdentityPropertyValueType
from .types import IdentityId

logger = logging.getLogger(__name__)


class DataStoreStateBase(BaseModel):
    # catch-all for anything not stored in specific identity registers
    last_updated: str = Field(default_factory=lambda: datetime.datetime.now(tz=datetime.UTC).isoformat())


class SdkBase:
    def __init__(
        self,
        *,
        hostname: str | None = None,
        port: int = 8105,
        data_store_tenant_suffix: str | None = None,
        create_data_store_identities_if_not_exist: bool = True,
    ) -> None:
        super().__init__()
        self._data_store_tenant_suffix = (
            data_store_tenant_suffix
            if data_store_tenant_suffix is not None
            else os.getenv(DATA_STORE_TENANT_SUFFIX_ENVVAR_NAME, DEFAULT_DATA_STORE_TENANT_SUFFIX)
        )
        self._data_store_tenant_suffix = self._data_store_tenant_suffix.rjust(DATA_STORE_TENANT_SUFFIX_LENGTH, "-")[
            :DATA_STORE_TENANT_SUFFIX_LENGTH
        ]

        self.hostname = hostname
        if self.hostname is None:
            self.hostname = os.getenv(BIOSERO_DATA_SERVICES_HOSTNAME_ENVVAR_NAME, "localhost")

        self.port = port
        self.create_data_store_identities_if_not_exist = create_data_store_identities_if_not_exist
        self._data_store_identities_created: bool = False
        self._session = requests.Session()
        self._session.request = partial(self._session.request, timeout=3)  # pyright: ignore[reportAttributeAccessIssue] # not sure why pyright is unhappy. This seems to be a generally accepted approach https://stackoverflow.com/questions/41295142/is-there-a-way-to-globally-override-requests-timeout-setting

    @property
    def data_store_identities_created(self) -> bool:
        return self._data_store_identities_created

    @property
    def data_store_tenant_suffix(self) -> str:
        return self._data_store_tenant_suffix

    def _add_tenant_suffix(self, identifier: str) -> str:
        return f"{identifier}--{self.data_store_tenant_suffix}"

    def build_data_store_identities(
        self, *, create_generic_state: bool = True, raise_error_if_organization_tree_missing: bool = False
    ) -> None:
        if not self.is_data_store_root_identity_created():
            if raise_error_if_organization_tree_missing:
                raise DataStoreRootIdentityMissingError(id=self.data_store_root_identity_id)
            self.create_data_store_root()
        if not self.is_data_store_arbitrary_json_identity_created():
            if raise_error_if_organization_tree_missing:
                raise DataStoreArbitraryJsonIdentityMissingError(id=self.data_store_arbitrary_json_identity_id)
            self.create_arbitrary_json_identity()
        if create_generic_state and not self.is_data_store_generic_state_created():
            self.create_generic_state(check_data_store_creation=False)
        self._data_store_identities_created = True

    @cached_property
    def _url_v2(self) -> str:
        return f"http://{self.hostname}:{self.port}/api/v2.0/"

    @cached_property
    def _url_v3(self) -> str:
        return f"http://{self.hostname}:{self.port}/api/v3.0/"

    def _url(self, api_version: float) -> str:
        if api_version == 3:  # noqa: PLR2004 # this isn't magic, it's the api version
            return self._url_v3
        if api_version == 2:  # noqa: PLR2004 # this isn't magic, it's the api version
            return self._url_v2
        raise NotImplementedError(f"No url defined for API version {api_version}")

    def _get_query(self, query: str, *, check_data_store_creation: bool = False, api_version: float = 2) -> JsonValue:
        if (
            check_data_store_creation
            and self.create_data_store_identities_if_not_exist
            and not self.data_store_identities_created
        ):
            self.build_data_store_identities()
        url = f"{self._url(api_version)}{query}"
        logger.info(f"Querying DataServices: {url}")
        start_time = perf_counter_ns()
        response = self._session.get(url)
        end_time = perf_counter_ns()
        logger.info(
            f"Completed GET to DataServices: {url}", extra={"data_services_api_call_duration_ns": end_time - start_time}
        )
        if not response.ok:
            raise DataServicesApiError(
                url=url, status_code=response.status_code, reason=response.reason, body=response.text
            )
        return response.json()

    def _post_request(
        self, *, query: str, payload: dict[str, JsonValue], offset: int = 0, api_version: float = 2
    ) -> JsonValue:
        if offset > 0:
            query += f"&offset={offset}"
        url = f"{self._url(api_version)}{query}"
        logger.info(f"Posting to DataServices at {url} with payload {payload}")
        start_time = perf_counter_ns()
        response = self._session.post(url, json=payload, timeout=10)
        end_time = perf_counter_ns()
        logger.info(
            f"Completed POST to DataServices at {url} with payload {payload}",
            extra={"data_services_api_call_duration_ns": end_time - start_time},
        )
        if not response.ok:
            raise DataServicesApiError(
                url=url, status_code=response.status_code, reason=response.reason, body=response.text
            )
        return response.json()

    def _put_request(self, *, query: str, payload: dict[str, JsonValue], api_version: float = 2) -> JsonValue:
        url = f"{self._url(api_version)}{query}"
        logger.info(f"Running a Put request to DataServices at {url} with payload {payload}")
        start_time = perf_counter_ns()
        response = self._session.put(url, json=payload, timeout=10)
        end_time = perf_counter_ns()
        logger.info(
            f"Completed PUT to DataServices at {url} with payload {payload}",
            extra={"data_services_api_call_duration_ns": end_time - start_time},
        )
        if not response.ok:
            raise DataServicesApiError(
                url=url, status_code=response.status_code, reason=response.reason, body=response.text
            )
        if response.text != "":
            raise NotImplementedError(
                "Presumably we should return `response.json()` here, but haven't actually encountered an API call to test this yet"
            )
        return response.text

    def is_data_store_root_identity_created(self) -> bool:
        query = f"QueryService/Identity?id={self.data_store_root_identity_id}"
        try:
            _ = self._get_query(query)
        except DataServicesApiError as e:
            if e.status_code == requests.codes.not_found:
                return False
            raise
        return True

    def is_data_store_arbitrary_json_identity_created(self) -> bool:
        query = f"QueryService/Identity?id={self.data_store_arbitrary_json_identity_id}"
        try:
            _ = self._get_query(query)
        except DataServicesApiError as e:
            if e.status_code == requests.codes.not_found:
                return False
            raise
        return True

    def get_data_store_generic_state(self) -> dict[str, JsonValue]:
        # return as dict so that custom code can use their own pydantic models
        query = f"QueryService/Identity?id={self.data_store_generic_state_identity_id}"
        response = self._get_query(query, check_data_store_creation=True)
        assert isinstance(response, dict), f"Expected a dict, got {type(response)} with value {response}"
        assert "properties" in response, f'Expected a "properties" key in the response, got {response}'
        properties = response["properties"]
        assert isinstance(properties, list), f"Expected a list, got {type(properties)} with value {properties}"
        target_property = properties[0]
        assert isinstance(target_property, dict), (
            f"Expected a dict, got {type(target_property)} with value {target_property}"
        )
        assert "value" in target_property, f'Expected a "value" key in the property, got {target_property}'
        value = target_property["value"]
        assert isinstance(value, str), f"Expected a string, got {type(value)} with value {value}"
        _ = DataStoreStateBase().model_validate_json(value)  # confirm that it's minimially correctly formatted
        self._data_store_identities_created = True  # if the generic state was retrieved successfully, therefore the data store identities must already have been created
        return json.loads(value)

    def is_data_store_generic_state_created(self) -> bool:
        query = f"QueryService/Identity?id={self.data_store_generic_state_identity_id}"
        try:
            _ = self._get_query(query)
        except DataServicesApiError as e:
            if e.status_code == requests.codes.not_found:
                return False
            raise
        return True

    def _update_identity(self, payload: dict[str, JsonValue], *, check_data_store_creation: bool = False) -> None:
        if check_data_store_creation and not self.data_store_identities_created:
            self.build_data_store_identities(
                create_generic_state=self.create_data_store_identities_if_not_exist,
                raise_error_if_organization_tree_missing=not self.create_data_store_identities_if_not_exist,
            )
        _ = self._post_request(
            query="AccessioningService/RegisterIdentity",
            payload=payload,
        )

    def create_identity(self, identity: DataServicesIdentity) -> None:
        # TODO: refactor the data store creation methods to use this
        if self.identity_exists(identity.id):
            raise IdentityAlreadyExistsError(id=identity.id)
        self._update_identity(identity.model_to_pass_to_api_for_update())

    def create_data_store_root(self) -> None:
        self._update_identity(
            DataServicesIdentity(
                id=self.data_store_root_identity_id,
                name="Arbitrary Data Store Root",
                parent_id=IDENTITY_ROOT_ID,
                description="Root of the arbitrary data store",
                is_instance=False,
                inherit_properties=False,
                properties=[
                    DataServicesIdentityProperty(
                        name="optimistic_locking_version",
                        value=None,
                        default_value="0",  # pyright: ignore[reportCallIssue] # ongoing problem with pydantic, IDEs, and aliases https://github.com/pydantic/pydantic/issues/5893
                        description="Version for optimistic locking",
                        value_type=IdentityPropertyValueType.INTEGER,  # pyright: ignore[reportCallIssue] # ongoing problem with pydantic, IDEs, and aliases https://github.com/pydantic/pydantic/issues/5893
                    )
                ],
            ).model_to_pass_to_api_for_update()
        )

    def create_arbitrary_json_identity(self) -> None:
        self._update_identity(
            {
                "identity": {
                    "identifier": self.data_store_arbitrary_json_identity_id,
                    "name": "Arbitrary JSON Data Store Container",
                    "typeIdentifier": self.data_store_root_identity_id,
                    "description": "An identifier type that within the data store that holds an arbitrary JSON object",
                    "isInstance": False,
                    "inheritProperties": True,
                    "properties": [
                        {
                            "name": "json_object",
                            "valueType": "String",
                            "defaultValue": "{}",
                            "description": "JSON Object",
                        }
                    ],
                }
            },
        )

    def create_generic_state(self, *, check_data_store_creation: bool = True):
        self.update_generic_state(DataStoreStateBase(), check_data_store_creation=check_data_store_creation)

    def update_generic_state(
        self, data_store_state: DataStoreStateBase, *, check_data_store_creation: bool = True
    ) -> None:
        self._update_identity(
            {
                "identity": {
                    "identifier": self.data_store_generic_state_identity_id,
                    "name": "Generic State",
                    "typeIdentifier": self.data_store_arbitrary_json_identity_id,
                    "description": "Misc items of the data store state not covered by other identities",
                    "isInstance": True,
                    "inheritProperties": True,
                    "properties": [
                        {
                            "name": "json_object",
                            "value": data_store_state.model_dump_json(),
                        }
                    ],
                }
            },
            check_data_store_creation=check_data_store_creation,
        )

    @property
    def data_store_root_identity_id(self) -> str:
        return self._add_tenant_suffix(DATA_STORE_ROOT_ID_BASE)

    @property
    def data_store_arbitrary_json_identity_id(self) -> str:
        return self._add_tenant_suffix(DATA_STORE_ARBITRARY_JSON_ID_BASE)

    @property
    def data_store_generic_state_identity_id(self) -> str:
        return self._add_tenant_suffix(DATA_STORE_GENERIC_STATE_ID_BASE)

    def get_identity_by_id(
        self, id: str, *, identities_cache: dict[IdentityId, DataServicesIdentity] | None = None
    ) -> DataServicesIdentity:
        if identities_cache is None:
            identities_cache = {}
        with contextlib.suppress(KeyError):
            return identities_cache[id]
        try:
            response = self._get_query(f"QueryService/Identity?id={id}")
        except DataServicesApiError as e:
            if e.status_code == requests.codes.not_found and "IdentityNotFound" in e.body:
                raise IdentityDoesNotExistError(id=id) from e
            raise  # pragma: nocover # not sure how to test this defensive statement
        assert isinstance(response, dict), f"Expected a dict, got {type(response)} with value {response}"
        identity = DataServicesIdentity.from_api_response(response)
        identities_cache[id] = identity
        return identity

    def identity_exists(self, id: str) -> bool:
        try:
            _ = self.get_identity_by_id(id)
        except IdentityDoesNotExistError:
            return False
        return True
