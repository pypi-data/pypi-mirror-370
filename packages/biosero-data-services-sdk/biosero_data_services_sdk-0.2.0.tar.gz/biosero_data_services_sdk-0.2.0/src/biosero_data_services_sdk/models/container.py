import json
from typing import Any
from typing import Self
from typing import cast
from typing import override

from pydantic import BaseModel
from pydantic import Field
from pydantic import JsonValue

from .base import DataServicesModel


class VolumeAmount(BaseModel):
    amount: float
    unit: str = "uL"


class NullContainerIdError(ValueError):
    def __init__(self, response_json: str):
        super().__init__(f"Container ID is null in the response JSON: {response_json}")


class DataServicesContainer(DataServicesModel):
    identity_id: str
    substance_id: str | None = (
        None  # this can be a Material or a Sample, so just calling it "substance". It's also basically worthless, since it seems to only evaluates to the _first_ substance that was ever transferred into the container, even if the container holds multiple substances
    )
    well_name: str | None = None
    net_volume: VolumeAmount | None = None
    location_path_as_ids: list[str] | None = Field(
        default=None, exclude=False
    )  # this isn't normally returned by Data Services, but is sometimes added on when it is obtained during model generation since it's an expensive API call we don't want to duplicate

    @override
    @classmethod
    def from_api_response(
        cls, response: dict[str, JsonValue], *, alternate_id_field_names: list[str] | None = None
    ) -> Self:
        # due to the way BioSero originally structured the identities at one client site, sometimes regular identities get passed to this with not the `containerIdentifier` key name holding the container's identity ID
        well_name: str | None = None
        if alternate_id_field_names is None:
            alternate_id_field_names = []
        id_field_names_to_check = ["containerIdentifier", *alternate_id_field_names]
        for id_field_name in id_field_names_to_check:
            if id_field_name in response:
                identity_identifier = response[id_field_name]
                break
        else:
            raise KeyError(  # noqa: TRY003 # this is a key error, and this is what key errors should actually provide so there's some helpful debugging context
                f"None of the expected ID field names ({id_field_names_to_check}) were found in the response: {response}"
            )
        if identity_identifier is None:
            # this seems like a bug in Data Services, but it can happen in results from /FindMaterial calls, and because there's no identifier, it's unclear how to track down how to fix it in the database...so we need to handle it gracefully
            raise NullContainerIdError(response_json=str(response))
        assert isinstance(identity_identifier, str), (
            f"Expected a string, got {type(identity_identifier)} with value {identity_identifier} within {response}"
        )

        if identity_identifier.endswith(">"):  # assume this is a well within a plate, e.g. "Plate 5<A1>"
            # Data Services does not typically register each well as its own Identity, just the parent Labware
            id_split = identity_identifier.split("<")
            well_name = id_split[-1].rstrip(">")
            identity_identifier = id_split[0]
        substance_identifier: JsonValue = None
        if "sampleIdentifier" in response:
            substance_identifier = response["sampleIdentifier"]
            assert isinstance(substance_identifier, str | type(None)), (
                f"Expected a string or None, got {type(substance_identifier)} with value {substance_identifier}"
            )
        elif "materialIdentifier" in response:
            substance_identifier = response["materialIdentifier"]
            assert isinstance(substance_identifier, str | type(None)), (
                f"Expected a string or None, got {type(substance_identifier)} with value {substance_identifier}"
            )
        net_volume: VolumeAmount | None = None
        if "netVolume" in response:
            net_volume_json = response["netVolume"]
            assert isinstance(net_volume_json, dict), (
                f"Expected a dict, got {type(net_volume_json)} with value {net_volume_json}"
            )

            assert "amount" in net_volume_json, f'Expected an "amount" key in the netVolume, got {net_volume_json}'
            assert isinstance(net_volume_json["amount"], (int, float)), (
                f"Expected an int or float for amount, got {type(net_volume_json['amount'])} with value {net_volume_json['amount']}"
            )
            assert "unit" in net_volume_json, f'Expected a "unit" key in the netVolume, got {net_volume_json}'
            assert isinstance(net_volume_json["unit"], str), (
                f"Expected a string for unit, got {type(net_volume_json['unit'])} with value {net_volume_json['unit']}"
            )
            net_volume = VolumeAmount(amount=net_volume_json["amount"], unit=net_volume_json["unit"])

        obj = cls(
            identity_id=identity_identifier,
            substance_id=substance_identifier,
            well_name=well_name,
            net_volume=net_volume,
        )
        obj.set_full_response_dict(response)
        return obj


class DataServicesLocation(DataServicesModel):
    parent_identity_id: str | None = None
    coordinates: str | None = None
    formatted_coordinates: str | None = None

    # TODO: figure out a way to return formatted_coordinates in the GraphQL response even if we don't have the coordinates being requested
    @override
    def model_post_init(self, context: Any) -> None:
        self.formatted_coordinates = self._parse_formatted_coordinates()

    def _parse_formatted_coordinates(self) -> str | None:
        if self.coordinates is None:
            return None
        try:
            json_dict = json.loads(self.coordinates)
        except json.JSONDecodeError:
            return self.coordinates
        if not isinstance(json_dict, dict):
            return self.coordinates
        row = json_dict.get("Row")  # pyright: ignore[reportUnknownMemberType,reportUnknownVariableType] # we're running isinstance afterwards to type guard
        if not isinstance(row, int):
            return self.coordinates
        column = json_dict.get("Column")  # pyright: ignore[reportUnknownMemberType,reportUnknownVariableType] # we're running isinstance afterwards to type guard
        if not isinstance(column, int):
            return self.coordinates
        return (
            f"{chr(64 + row)}{str(column).zfill(2)}"  # Convert 1-indexed row to A, B, C, etc. and column to 1-indexed
        )

    @override
    @classmethod
    def from_api_response(cls, response: dict[str, JsonValue]) -> Self:
        assert "parentIdentifier" in response, f'Expected an "parentIdentifier" key in the response, got {response}'
        parent_identifier = response["parentIdentifier"]
        assert isinstance(parent_identifier, str), (
            f"Expected a string, got {type(parent_identifier)} with value {parent_identifier}"
        )
        if (
            parent_identifier == "Unknown"
        ):  # for some reason, Data Services uses the string "Unknown" to indicate no parent identity instead of `null`
            parent_identifier = None
        assert "coordinates" in response, f'Expected a "coordinates" key in the response, got {response}'
        coordinates = response["coordinates"]
        assert isinstance(coordinates, str | type(None)), (
            f"Expected a string or None, got {type(coordinates)} with value {coordinates}"
        )

        obj = cls(parent_identity_id=parent_identifier, coordinates=coordinates)
        obj.set_full_response_dict(response)
        return obj


class DataServicesSubstanceInContainer(DataServicesModel):
    container_id: str
    volume_change: float | None = None
    volume_unit: str | None = None

    @property
    def substance_id(self) -> str:
        if hasattr(self, "sample_id"):
            sample_id = cast(str, self.sample_id)  # pyright: ignore[reportUnknownMemberType,reportAttributeAccessIssue] # we're casting and asserting the type...not sure why it thinks there's an attribute issue since we just did hasattr
            assert isinstance(sample_id, str), (
                f"Expected a string for sample ID, got {type(sample_id)} with value {sample_id}"
            )
            return sample_id
        if hasattr(self, "material_id"):
            material_id = cast(str, self.material_id)  # pyright: ignore[reportUnknownMemberType,reportAttributeAccessIssue] # we're casting and asserting the type...not sure why it thinks there's an attribute issue since we just did hasattr
            assert isinstance(material_id, str), (
                f"Expected a string for material ID, got {type(material_id)} with value {material_id}"
            )
            return material_id
        raise NotImplementedError(
            f"Could not find either a sample ID or a material ID. This should never happen. Details: {self.model_dump()}"
        )

    @override
    @classmethod
    def from_api_response(cls, response: dict[str, JsonValue]) -> "DataServicesSubstanceInContainer":
        assert "containerIdentifier" in response, (
            f'Expected a "containerIdentifier" key in the response, got {response}'
        )
        container_identifier = response["containerIdentifier"]
        assert isinstance(container_identifier, str), (
            f"Expected a string, got {type(container_identifier)} with value {container_identifier}"
        )

        assert "netVolume" in response, f'Expected a "netVolume" key in the response, got {response}'
        net_volume = response["netVolume"]
        assert isinstance(net_volume, (dict, type(None))), (
            f"Expected a dict or None, got {type(net_volume)} with value {net_volume}"
        )
        volume_change: float | None = None
        volume_unit: str | None = None
        if net_volume is not None:
            assert "amount" in net_volume, f'Expected an "amount" key in the netVolume, got {net_volume}'
            assert isinstance(net_volume["amount"], (int, float)), (
                f"Expected an int or float for amount, got {type(net_volume['amount'])} with value {net_volume['amount']}"
            )
            volume_change = net_volume["amount"]

            assert "unit" in net_volume, f'Expected a "unit" key in the netVolume, got {net_volume}'
            assert isinstance(net_volume["unit"], str), (
                f"Expected a string for unit, got {type(net_volume['unit'])} with value {net_volume['unit']}"
            )
            volume_unit = net_volume["unit"]

        obj = DataServicesSubstanceInContainer(
            container_id=container_identifier, volume_change=volume_change, volume_unit=volume_unit
        )
        obj.set_full_response_dict(response)
        return obj


class DataServicesSampleInContainer(DataServicesSubstanceInContainer):
    sample_id: str

    @override
    @classmethod
    def from_api_response(cls, response: dict[str, JsonValue]) -> Self:
        assert "sampleIdentifier" in response, f'Expected a "sampleIdentifier" key in the response, got {response}'
        sample_identifier = response["sampleIdentifier"]
        assert isinstance(sample_identifier, str), (
            f"Expected a string, got {type(sample_identifier)} with value {sample_identifier}"
        )
        obj = super().from_api_response(response)
        new_obj = cls(sample_id=sample_identifier, **obj.model_dump())
        new_obj.set_full_response_dict(response)
        return new_obj


class DataServicesMaterialInContainer(DataServicesSubstanceInContainer):
    material_id: str

    @override
    @classmethod
    def from_api_response(cls, response: dict[str, JsonValue]) -> Self:
        assert "materialIdentifier" in response, f'Expected a "materialIdentifier" key in the response, got {response}'
        material_identifier = response["materialIdentifier"]
        assert isinstance(material_identifier, str), (
            f"Expected a string, got {type(material_identifier)} with value {material_identifier} as part of {response}"
        )
        obj = super().from_api_response(response)
        new_obj = cls(material_id=material_identifier, **obj.model_dump())
        new_obj.set_full_response_dict(response)
        return new_obj
