import contextlib
import json
import logging
from pathlib import Path
from typing import Any
from typing import override

from nested_diff import diff  # pyright: ignore[reportUnknownVariableType] # the library is not fully typed
from nested_diff import handlers
from nested_diff.formatters import HtmlFormatter
from pydantic import BaseModel
from pydantic import Field

from .exceptions import IdentityDoesNotExistError
from .exceptions import NothingToScanProvidedError
from .locations_sdk import LocationsSdk
from .models import DataServicesIdentity
from .types import IdentityId

logger = logging.getLogger(__name__)


class IdentityDiff(BaseModel):
    id: str
    diff: str


class IdentitiesMergeReport(BaseModel):
    # the created and untouched lists are the identifiers of the identities, but GraphQL wouldn't let me easily use the custom `IdentityId` type
    created: list[str] = Field(default_factory=list[str])
    untouched: list[str] = Field(default_factory=list[str])
    updated: list[IdentityDiff] = Field(default_factory=list[IdentityDiff])

    @override
    def model_post_init(self, context: Any) -> None:
        self._updated: dict[IdentityId, str] = {diff.id: diff.diff for diff in self.updated}

    @property
    def num_created(self) -> int:
        return len(self.created)

    @property
    def num_untouched(self) -> int:
        return len(self.untouched)

    @property
    def num_updated(self) -> int:
        return len(self.updated)

    def get_update_diff_for_id(self, id: IdentityId) -> str:
        return self._updated[id]

    def add_update_diff(self, id: IdentityId, diff: str) -> None:
        self._updated[id] = diff
        self.updated.append(IdentityDiff(id=id, diff=diff))


class EventUploadReport(BaseModel):
    untouched: list[str] = Field(default_factory=list[str])
    created: list[str] = Field(default_factory=list[str])
    conflicts: list[str] = Field(default_factory=list[str])

    @property
    def num_untouched(self) -> int:
        return len(self.untouched)

    @property
    def num_created(self) -> int:
        return len(self.created)

    @property
    def num_conflicts(self) -> int:
        return len(self.conflicts)


class MissingIdentitiesAtLocationReport(BaseModel):
    id: str
    missing_ids: list[str] = Field(default_factory=list[str])


class MissingIdentitiesAtLocationWithChildrenReport(BaseModel):
    id: str
    missing_ids: list[str] = Field(default_factory=list[str])
    missing_contained_ids: list[MissingIdentitiesAtLocationReport] = Field(
        default_factory=list[MissingIdentitiesAtLocationReport]
    )


class DataServicesInconsistenciesReport(BaseModel):
    missing_identities_at_locations: list[MissingIdentitiesAtLocationWithChildrenReport] = (
        Field(  # using this type rather than a dict to make it GraphQL-friendly
            default_factory=list[MissingIdentitiesAtLocationWithChildrenReport]
        )
    )


class ReportsSdk(LocationsSdk):
    def download_all_identities(self, savepoint_dir: Path, *, pagination_size: int = 100) -> int:
        offset = 0
        while True:  # TODO: maybe provide some maximum number of iterations this will go through to avoid accidental infinite looping
            response = self._get_query(f"identities?limit={pagination_size}&offset={offset}", api_version=3)
            assert isinstance(response, list), f"Expected a list, got {type(response)} with value {response}"
            num_records = len(response)
            if num_records == 0:
                return offset
            file_path = savepoint_dir / f"identities_{(str(int(offset / pagination_size))).zfill(3)}.json"
            _ = file_path.write_text(json.dumps(response))
            if num_records < pagination_size:
                return offset + num_records
            offset += pagination_size

    def merge_identities_from_file(self, savepoint_dir: Path, *, preview: bool = False) -> IdentitiesMergeReport:
        all_identities_json_files = sorted(savepoint_dir.rglob("identities*.json"))
        merge_report = IdentitiesMergeReport()
        for json_file in all_identities_json_files:
            with json_file.open() as f:
                json_data = json.load(f)
            assert isinstance(json_data, list), f"Expected list but got type {type(json_data)} for file {json_file}"
            for identity_json in json_data:  # pyright: ignore[reportUnknownVariableType] # we're loading in JSON and then asserting about it
                assert isinstance(identity_json, dict), (
                    f"Expected dict but got type {type(identity_json)} for {identity_json}"  # pyright: ignore[reportUnknownArgumentType] # we're loading in JSON and then asserting about it
                )
                identity = DataServicesIdentity.from_api_response(identity_json)  # pyright: ignore[reportUnknownArgumentType] # we're loading in JSON and then asserting about it
                _ = self.update_identity(identity, preview=preview, merge_report=merge_report)
        return merge_report

    def update_identity(
        self,
        identity: DataServicesIdentity,
        *,
        preview: bool = False,
        merge_report: IdentitiesMergeReport | None = None,
    ) -> IdentitiesMergeReport:
        if merge_report is None:
            merge_report = IdentitiesMergeReport()
        existing_identity: DataServicesIdentity | None = None
        with contextlib.suppress(IdentityDoesNotExistError):
            existing_identity = self.get_identity_by_id(identity.id)
        if existing_identity is not None and existing_identity == identity:
            merge_report.untouched.append(identity.id)
            return merge_report
        if not preview:
            self._update_identity(identity.model_to_pass_to_api_for_update())
        if existing_identity is None:
            # TODO: consider renaming this method, since it will not just update identities...it will also create them if they don't exist
            merge_report.created.append(identity.id)
        else:
            formatter = HtmlFormatter()
            html_diff = formatter.format(  # pyright: ignore[reportUnknownMemberType] # the library is not fully typed
                diff(
                    json.dumps(existing_identity.full_response_dict, indent=2),
                    json.dumps(identity.full_response_dict, indent=2),
                    U=False,
                    extra_handlers=[handlers.TextHandler(context=5)],
                )
            )
            css = formatter.get_css()
            for old_color, new_color in (
                ("#dfd", "var(--ui-success)"),  # added text background
                ("#cfc", "var(--ui-success)"),  # some other sort of added text background
                ("#fcc", "var(--ui-error)"),  # removed text background
                ("#fdd", "var(--ui-error)"),  # some other sort of removed text background
                ("#777", "var(--ui-text)"),  # unchanged text
                ("#707", "var(--ui-info)"),  # the diff summary line
                ("#00b", "var(--ui-info)"),  # the data type line
                # still don't know what `.nDkD, .nDkN, .nDkO {color: #000}` is for
            ):
                css = css.replace(old_color, new_color)
            merge_report.add_update_diff(
                identity.id,
                f'<head><style>{css}</style></head><body><div class="nDvD" style="width:fit-content">{html_diff}</div><script>{formatter.get_script()}</script></body>',
            )
        return merge_report

    def scan_data_services_for_inconsistencies(
        self, *, confirm_identities_at_locations_exist: list[str] | None = None
    ) -> DataServicesInconsistenciesReport:
        """Scan for internal inconsistencies within the state of Data Services.

        Look for records in the Location Cache that do not actually exist as registered identities.
        """
        something_to_check_was_provided = False

        if confirm_identities_at_locations_exist is None:
            confirm_identities_at_locations_exist = []
        if len(confirm_identities_at_locations_exist) > 0:
            something_to_check_was_provided = True
        if not something_to_check_was_provided:
            raise NothingToScanProvidedError
        report = DataServicesInconsistenciesReport()
        for location_id in confirm_identities_at_locations_exist:
            missing_ids_report = MissingIdentitiesAtLocationWithChildrenReport(id=location_id)
            report.missing_identities_at_locations.append(missing_ids_report)
            contained_child_items = self.get_identities_at_location(location_id)
            for contained_child_item in contained_child_items:
                missing_ids_of_child_report = MissingIdentitiesAtLocationReport(id=contained_child_item.id)

                contained_grandchild_items = self.get_identities_at_location(
                    contained_child_item.id,
                    confirm_location_exists=False,  # we're going to do this separately
                )
                for contained_grandchild_item in contained_grandchild_items:
                    if not self.identity_exists(contained_grandchild_item.id):
                        missing_ids_of_child_report.missing_ids.append(contained_grandchild_item.id)
                if len(missing_ids_of_child_report.missing_ids) > 0:
                    missing_ids_report.missing_contained_ids.append(missing_ids_of_child_report)
                if not self.identity_exists(contained_child_item.id):
                    missing_ids_report.missing_ids.append(contained_child_item.id)

        return report
