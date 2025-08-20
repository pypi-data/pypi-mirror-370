import logging

from .exceptions import IdentityDoesNotExistError
from .models import DataServicesIdentity
from .sdk_base import SdkBase
from .types import IdentityId

logger = logging.getLogger(__name__)


class IdentitiesSdk(SdkBase):
    def get_child_identities(
        self, parent_id: str, *, recursive: bool = False, confirm_parent_id_exists: bool = True
    ) -> list[DataServicesIdentity]:
        # The API for ChildIdentities does not actually check if the parent exists...it will just silently return an empty list. That's unexpected API behavior, so we check it ourselves, which will raise an error if it doesn't exist
        if confirm_parent_id_exists:
            _ = self.get_identity_by_id(parent_id)
        limit = 999999  # arbitrarily large number
        identity_list: list[DataServicesIdentity] = []
        response = self._get_query(f"QueryService/ChildIdentities?parentTypeId={parent_id}&limit={limit}")
        assert isinstance(response, list), f"Expected a list, got {type(response)} with value {response}"

        for item in response:
            assert isinstance(item, dict), f"Expected a dict, got {type(item)} with value {item}"
            identity = DataServicesIdentity.from_api_response(item)
            identity_list.append(identity)
            if recursive:
                child_identities = self.get_child_identities(
                    identity.id, recursive=True, confirm_parent_id_exists=False
                )
                identity_list.extend(child_identities)
        return identity_list

    def is_identity_name_a_child_of(self, *, name: str, parent_id: str) -> bool:
        identities = self._get_query(f"identities?name={name}&typeIdentifier={parent_id}&limit=1", api_version=3)
        assert isinstance(identities, list), f"Expected a list, got {type(identities)} with value {identities}"
        return len(identities) > 0

    def is_identity_a_descendent_of(
        self,
        *,
        identity_id: str,
        ancestor_id: str,
        is_being_called_recursively: bool = False,
        identities_cache: dict[IdentityId, DataServicesIdentity] | None = None,
    ) -> bool:
        if identities_cache is None:
            identities_cache = {}
        if identity_id in identities_cache:
            identity = identities_cache[identity_id]
        else:
            try:
                identity = self.get_identity_by_id(identity_id)
            except IdentityDoesNotExistError:
                if not is_being_called_recursively:
                    raise
                return False
            identities_cache[identity_id] = identity
        if identity.parent_id == ancestor_id:
            return True
        if identity.parent_id == "":
            return False
        if identity.parent_id is None:
            return False
        return self.is_identity_a_descendent_of(
            identity_id=identity.parent_id,
            ancestor_id=ancestor_id,
            is_being_called_recursively=True,
            identities_cache=identities_cache,
        )
