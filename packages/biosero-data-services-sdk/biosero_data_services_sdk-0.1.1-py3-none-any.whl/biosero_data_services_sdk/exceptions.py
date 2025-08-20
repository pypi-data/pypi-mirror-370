from .models import DataServicesIdentity
from .types import RequestWithOffset


class DataServicesApiError(Exception):
    def __init__(self, *, url: str, status_code: int, reason: str, body: str) -> None:
        self.url = url
        self.status_code = status_code
        self.reason = reason
        self.body = body
        super().__init__(f"Error querying {url}. Status code: {status_code}. Reason: {reason}. Body: {body}")


class SeeminglyInfiniteLocationPathError(Exception):
    def __init__(self, *, original_id: str, location_path: list[str]):
        super().__init__(
            f"The location path for {original_id} seems to be infinite. This is likely due to a circular reference in the location hierarchy. Please check the location data for circular references. {location_path}"
        )


class IdentityIsNotSubstanceError(Exception):
    def __init__(self, info: str | DataServicesIdentity) -> None:
        super().__init__(
            f"The provided identity {info} is not a Substance. It must be a direct child of Sample or Material identities for Data Services to be able to handle it."
        )


class IdentityIsNotContainerError(Exception):
    def __init__(self, info: str | DataServicesIdentity) -> None:
        super().__init__(
            f"The provided identity {info} is not a Container. It must be within the hierarchy of Container definitions."
        )


class IdentityIsNotTransferStationError(Exception):
    def __init__(self, info: str | DataServicesIdentity) -> None:
        super().__init__(
            f"The provided identity {info} is not a Transfer Station. It must be within the hierarchy of Transfer Station definitions."
        )


class OrderParameterNotInTemplateError(Exception):
    def __init__(self, *, parameter_name: str, template_name: str, template_parameters: list[str]):
        super().__init__(
            f"Order parameter '{parameter_name}' is not in the order template '{template_name}'. Available parameters: {', '.join(template_parameters)}"
        )


class IdentityDoesNotExistError(Exception):
    def __init__(self, *, id: str, extra_message: str = "") -> None:
        super().__init__(
            f"Identity with identifier '{id}' does not exist" + (f"\n{extra_message}" if extra_message else "")
        )


class OrderDoesNotExistError(Exception):
    def __init__(self, id: str):
        super().__init__(f"Order with ID {id} does not exist.")


class OrderTemplateDoesNotExistError(Exception):
    def __init__(self, name: str):
        super().__init__(f"Order template '{name}' does not exist.")


class OrderTemplateAlreadyExistsError(Exception):
    def __init__(self, name: str):
        super().__init__(f"Order template '{name}' already exists.")


class TransportationRequestDoesNotExistError(Exception):
    def __init__(self, request_id: str):
        super().__init__(f"Transportation request with id {request_id} does not exist.")


class IdentityAlreadyExistsError(Exception):
    def __init__(self, id: str):
        super().__init__(f"Identity with identifier '{id}' already exists.")


class EventDoesNotExistError(Exception):
    def __init__(self, event_id: str):
        super().__init__(f"Event with ID {event_id} does not exist.")


class InvalidEventQueryParametersError(Exception):
    def __init__(self):
        super().__init__("At least one of the query parameters must be provided.")


class DataStoreRootIdentityMissingError(IdentityDoesNotExistError):
    pass


class DataStoreArbitraryJsonIdentityMissingError(IdentityDoesNotExistError):
    pass


class NothingToScanProvidedError(Exception):
    def __init__(self):
        super().__init__("Nothing to check for inconsistencies was passed in as an argument.")


class DataRecordOverflowError(Exception):
    def __init__(self, *, max_limit: int, request: RequestWithOffset):
        request_info = self._get_request_info(request)
        super().__init__(
            f"Exceeded maximum limit of {max_limit} items while fetching data from DataServices API using {request_info}."
        )

    def _get_request_info(self, request: RequestWithOffset) -> str:
        """Extract meaningful information from the request, especially if it's a partial function."""
        if hasattr(request, "func") and hasattr(request, "keywords"):  # It's likely a partial
            func_name = request.func.__name__ if hasattr(request.func, "__name__") else str(request.func)  # pyright: ignore[reportUnknownArgumentType,reportUnknownMemberType,reportAttributeAccessIssue,reportUnknownVariableType] # this is tested and it works
            keywords = ", ".join(f"{k}={v!r}" for k, v in request.keywords.items())  # pyright: ignore[reportUnknownMemberType,reportAttributeAccessIssue,reportUnknownVariableType] # this is tested and it works
            return f"partial({func_name}, {keywords})"
        raise NotImplementedError(
            f"Not sure how we got here, but this should always be called with a partial. The request was {request!r}"
        )
