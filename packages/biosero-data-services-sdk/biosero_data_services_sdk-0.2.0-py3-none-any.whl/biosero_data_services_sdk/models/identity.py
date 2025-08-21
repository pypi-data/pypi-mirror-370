from enum import StrEnum
from typing import Literal
from typing import Self
from typing import overload
from typing import override
from uuid import uuid4

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import JsonValue

from .base import DataServicesModel


class IdentityPropertyValueType(StrEnum):
    STRING = "String"
    BOOLEAN = "Boolean"
    DOUBLE = "Double"
    INTEGER = "Integer"
    OTHER = "Other"
    UNKNOWN = "Unknown"


class IdentityPropertyNotFoundError(KeyError):
    def __init__(self, property_name: str, full_response_dict: dict[str, JsonValue]):
        super().__init__(f"Property {property_name} not found in identity {full_response_dict}")


class NullIdentityPropertyValueError(ValueError):
    def __init__(self, property_name: str, full_response_dict: dict[str, JsonValue]):
        super().__init__(f"Property {property_name} has a null value in identity {full_response_dict}")


class DataServicesIdentityProperty(DataServicesModel):
    name: str
    value: str | None
    value_type: IdentityPropertyValueType = Field(default=IdentityPropertyValueType.STRING, alias="valueType")
    unit: str | None = None
    default_value: str | None = Field(default=None, alias="defaultValue")
    value_options: list[str] | None = Field(default=None, alias="valueOptions")
    validation_rules: list[str] | None = Field(
        default=None, alias="validationRules"
    )  # this is present in API responses and works when included in API calls, but is absent from the Data Services Swagger Documentation. We have to give the list some type, so arbitrarily choosing string for now
    tags: list[str] | None = None
    identity: str | None = None
    description: str | None = None

    model_config = ConfigDict(validate_by_alias=True, validate_by_name=True)


def _extract_properties_from_api_response(properties_json: list[JsonValue]) -> list[DataServicesIdentityProperty]:
    properties_pydantic: list[DataServicesIdentityProperty] = []
    for property_json in properties_json:
        assert isinstance(property_json, dict), f"Expected a dict, got {type(property_json)} with value {property_json}"
        assert "name" in property_json, f'Expected a "name" key in the property, got {property_json}'
        assert "value" in property_json, f'Expected a "value" key in the property, got {property_json}'
        property_name = property_json["name"]
        assert isinstance(property_name, str), (
            f"Expected a string, got {type(property_name)} with value {property_name}"
        )
        value = property_json["value"]
        assert isinstance(value, (str | type(None))), f"Expected a string or None, got {type(value)} with value {value}"

        assert "valueType" in property_json, f'Expected a "valueType" key in the property, got {property_json}'
        value_type = property_json["valueType"]
        assert isinstance(value_type, str), f"Expected a string, got {type(value_type)} with value {value_type}"

        assert "unit" in property_json, f'Expected a "unit" key in the property, got {property_json}'
        unit = property_json["unit"]
        assert isinstance(unit, (str, type(None))), f"Expected a string or None, got {type(unit)} with value {unit}"

        assert "defaultValue" in property_json, f'Expected a "defaultValue" key in the property, got {property_json}'
        default_value = property_json["defaultValue"]
        assert isinstance(default_value, (str, type(None))), (
            f"Expected a string or None, got {type(default_value)} with value {default_value}"
        )

        assert "valueOptions" in property_json, f'Expected a "valueOptions" key in the property, got {property_json}'
        value_options = property_json["valueOptions"]
        assert isinstance(value_options, (list, type(None))), (
            f"Expected a list or None, got {type(value_options)} with value {value_options}"
        )
        if value_options is not None:
            for option in value_options:
                assert isinstance(option, str), (
                    f"Expected a string in valueOptions, got {type(option)} with value {option}"
                )

        assert "tags" in property_json, f'Expected a "tags" key in the property, got {property_json}'
        tags = property_json["tags"]
        assert isinstance(tags, (list, type(None))), f"Expected a list or None, got {type(tags)} with value {tags}"
        if tags is not None:
            for tag in tags:
                assert isinstance(tag, str), f"Expected a string in tags, got {type(tag)} with value {tag}"

        assert "identity" in property_json, f'Expected a "identity" key in the property, got {property_json}'
        property_identity = property_json["identity"]
        assert isinstance(property_identity, (str, type(None))), (
            f"Expected a string or None, got {type(property_identity)} with value {property_identity}"
        )

        assert "description" in property_json, f'Expected a "description" key in the property, got {property_json}'
        property_description = property_json["description"]
        assert isinstance(property_description, (str, type(None))), (
            f"Expected a string or None, got {type(property_description)} with value {property_description}"
        )

        validation_rules = None
        if "validationRules" in property_json:
            validation_rules = property_json["validationRules"]
            assert isinstance(validation_rules, (list, type(None))), (
                f"Expected a list or None, got {type(validation_rules)} with value {validation_rules}"
            )
            if validation_rules is not None:
                for rule in validation_rules:
                    assert isinstance(  # pragma: no cover # we don't actually know if validation rules are actually represented as strings, but this will help alert us if they aren't
                        rule, str
                    ), f"Expected a string in validationRules, got {type(rule)} with value {rule}"

        pydantic_property = DataServicesIdentityProperty(
            name=property_name,
            value=value,
            value_type=IdentityPropertyValueType(value_type),  # pyright: ignore[reportCallIssue] # ongoing problem with pydantic, IDEs, and aliases https://github.com/pydantic/pydantic/issues/5893
            unit=unit,
            default_value=default_value,  # pyright: ignore[reportCallIssue] # ongoing problem with pydantic, IDEs, and aliases https://github.com/pydantic/pydantic/issues/5893
            value_options=value_options,  # pyright: ignore[reportCallIssue] # ongoing problem with pydantic, IDEs, and aliases https://github.com/pydantic/pydantic/issues/5893
            tags=tags,
            identity=property_identity,
            description=property_description,
            validation_rules=validation_rules,  # pyright: ignore[reportCallIssue] # ongoing problem with pydantic, IDEs, and aliases https://github.com/pydantic/pydantic/issues/5893
        )
        pydantic_property.set_full_response_dict(property_json)
        properties_pydantic.append(pydantic_property)
    return properties_pydantic


class DataServicesIdentity(DataServicesModel):
    id: str = Field(serialization_alias="identifier")
    name: str | None = None
    parent_id: str | None = Field(default=None, serialization_alias="typeIdentifier")
    description: str | None = None
    properties: list[DataServicesIdentityProperty] = Field(default_factory=list[DataServicesIdentityProperty])
    inherit_properties: bool = Field(default=True, serialization_alias="inheritProperties")
    is_instance: bool = Field(default=True, serialization_alias="isInstance")

    def model_to_pass_to_api_for_update(self) -> dict[str, JsonValue]:
        return {"identity": self.model_dump(by_alias=True, exclude={"original_full_json_string"})}

    def get_property(self, property_name: str) -> DataServicesIdentityProperty:
        # TODO: consider if needing to handle malformed identities with duplicate property names
        error_info = self.full_response_dict if self.original_full_json_string is not None else self.model_dump()
        for prop in self.properties:
            if prop.name == property_name:
                return prop
        raise IdentityPropertyNotFoundError(property_name, error_info)

    @overload
    def get_property_value(  # pragma: no cover # this is a type definition
        self, property_name: str, *, require_value: Literal[False]
    ) -> str | None: ...
    @overload
    def get_property_value(  # pragma: no cover # this is a type definition
        self, property_name: str, *, require_value: Literal[True]
    ) -> str: ...
    @overload
    def get_property_value(  # pragma: no cover # this is a type definition
        self, property_name: str
    ) -> str | None: ...
    def get_property_value(self, property_name: str, *, require_value: bool = False):
        error_info = self.full_response_dict if self.original_full_json_string is not None else self.model_dump()
        value = self.get_property(property_name).value
        if value is None and require_value:
            raise NullIdentityPropertyValueError(property_name, error_info)
        return value

    def has_property(self, property_name: str) -> bool:
        return any(prop.name == property_name for prop in self.properties)

    @override
    @classmethod
    def from_api_response(cls, response: dict[str, JsonValue]) -> Self:
        assert "identifier" in response, f'Expected an "identifier" key in the response, got {response}'
        identifier = response["identifier"]
        assert isinstance(identifier, str), f"Expected a string, got {type(identifier)} with value {identifier}"

        assert "typeIdentifier" in response, f'Expected a "typeIdentifier" key in the response, got {response}'
        parent_id = response["typeIdentifier"]
        assert isinstance(parent_id, str | type(None)), (
            f"Expected a string or None, got {type(parent_id)} with value {parent_id}"
        )

        assert "description" in response, f'Expected a "description" key in the response, got {response}'
        identity_description = response["description"]
        assert isinstance(identity_description, str | type(None)), (
            f"Expected a string or None, got {type(identity_description)} with value {identity_description}"
        )

        assert "name" in response, f'Expected a "name" key in the response, got {response}'
        identity_name = response["name"]
        assert isinstance(identity_name, str | type(None)), (
            f"Expected a string or None, got {type(identity_name)} with value {identity_name}"
        )

        assert "properties" in response, f'Expected a "properties" key in the response, got {response}'
        properties_json = response["properties"]
        assert isinstance(properties_json, list), (
            f"Expected a list, got {type(properties_json)} with value {properties_json}"
        )
        properties_pydantic = _extract_properties_from_api_response(properties_json)

        assert "isInstance" in response, f'Expected an "isInstance" key in the response, got {response}'
        is_instance = response["isInstance"]
        assert isinstance(is_instance, bool), f"Expected a boolean, got {type(is_instance)} with value {is_instance}"

        assert "inheritProperties" in response, f'Expected an "inheritProperties" key in the response, got {response}'
        inherit_properties = response["inheritProperties"]
        assert isinstance(inherit_properties, bool), (
            f"Expected a boolean, got {type(inherit_properties)} with value {inherit_properties}"
        )

        obj = cls(
            id=identifier,
            name=identity_name,
            properties=properties_pydantic,
            parent_id=parent_id,
            description=identity_description,
            is_instance=is_instance,
            inherit_properties=inherit_properties,
        )
        obj.set_full_response_dict(response)
        return obj


class DataServicesIdentityPropertyQuery(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    parent_identity_ids: list[str]
    recursive_search: bool = True
    expect_exactly_one_match: bool = True  # TODO: implement this in find matches

    # TODO: implement search_type that is things like "contains", "starts with", etc.
    parse_values_as_csv: bool = False
    property_names_to_search: list[str]

    def find_matches(self, *, identities: list[DataServicesIdentity], search_value: str) -> list[DataServicesIdentity]:
        matching_identities: list[DataServicesIdentity] = []
        for identity in identities:
            for property_name in self.property_names_to_search:
                for identity_property in identity.properties:
                    if identity_property.name == property_name:
                        parsed_property_value = [identity_property.value]
                        if parsed_property_value[0] is not None and self.parse_values_as_csv:
                            parsed_property_value = [x.strip() for x in parsed_property_value[0].split(",")]
                        if search_value in parsed_property_value:
                            matching_identities.append(identity)
                            break

        return matching_identities
