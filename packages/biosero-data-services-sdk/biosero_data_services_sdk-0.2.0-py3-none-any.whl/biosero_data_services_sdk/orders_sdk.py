import logging
from functools import partial
from typing import TYPE_CHECKING

import requests

from .exceptions import DataServicesApiError
from .exceptions import OrderDoesNotExistError
from .exceptions import OrderParameterNotInTemplateError
from .exceptions import OrderTemplateAlreadyExistsError
from .exceptions import OrderTemplateDoesNotExistError
from .models import Order
from .models import OrderParameter
from .models import OrderTemplate
from .sdk_base import SdkBase
from .sdk_base import get_all_data
from .sdk_base import get_limit

if TYPE_CHECKING:
    from pydantic import JsonValue
logger = logging.getLogger(__name__)


class OrdersSdk(SdkBase):
    def get_order_template(self, name: str) -> OrderTemplate:
        try:
            response = self._get_query(f"order-templates/{name}", api_version=3)
        except DataServicesApiError as e:
            if e.status_code == requests.codes.not_found and "OrderTemplateNotFound" in e.body:
                raise OrderTemplateDoesNotExistError(name=name) from e
            raise  # pragma: nocover # not sure how to test this defensive statement
        assert isinstance(response, dict), f"Expected a dict, got {type(response)} with value {response}"
        return OrderTemplate.from_api_response(response)

    def create_order_template(self, order_template: OrderTemplate) -> None:
        order_exists = True
        try:
            _ = self.get_order_template(order_template.name)
        except OrderTemplateDoesNotExistError:
            order_exists = False
        if order_exists:
            raise OrderTemplateAlreadyExistsError(name=order_template.name)

        payload = order_template.model_to_pass_to_api_for_update()
        _ = self._post_request(query="OrderService/RegisterOrderTemplate", payload=payload)

    def update_order_template(self, order_template: OrderTemplate) -> None:
        _ = self.get_order_template(order_template.name)  # confirm that the order template exists
        payload = order_template.model_to_pass_to_api_for_update()
        _ = self._post_request(query="OrderService/RegisterOrderTemplate", payload=payload)

    def get_order(self, order_id: str) -> Order:
        try:
            response = self._get_query(f"orders/{order_id}", api_version=3)
        except DataServicesApiError as e:
            if e.status_code == requests.codes.not_found and "OrderNotFound" in e.body:
                raise OrderDoesNotExistError(id=order_id) from e
            raise  # pragma: nocover # not sure how to test this defensive statement
        assert isinstance(response, dict), f"Expected a dict, got {type(response)} with value {response}"
        return Order.from_api_response(response)

    def get_order_templates(self) -> list[OrderTemplate]:
        limit = get_limit(2000)
        request = partial(self._get_query, query=f"order-templates?limit={limit}", api_version=3)
        all_responses = get_all_data(request=request, limit=limit)
        all_templates: list[OrderTemplate] = []
        for response in all_responses:
            assert isinstance(response, dict), f"Expected a dict, got {type(response)} with value {response}"
            all_templates.append(OrderTemplate.from_api_response(response))
        return all_templates

    def create_order(self, *, template_name: str, parameters: list[OrderParameter] | None = None) -> str:
        order_template = self.get_order_template(template_name)  # confirm that the order template exists
        if parameters is None:
            parameters = []
        payload: dict[str, JsonValue] = {
            "templateName": template_name,
            "schedulingStrategy": "ImmediateExecution",
            "restrictToModuleIds": "Workflow Execution Engine",  # this can be set to a workcell ID if not intended to be executed by Conductor itself
            "moduleRestrictionStrategy": "NoRestriction",  # this can be used to set fallback workcells if the desired module ID is busy
        }
        parameters_payload = [param.model_dump(include={"name", "value"}, mode="json") for param in parameters]
        for parameter_in_payload in parameters:
            found_param_in_template = False
            for parameter_in_template in order_template.input_parameters:
                if parameter_in_payload.name == parameter_in_template.name:
                    found_param_in_template = True
                    break
            if not found_param_in_template:
                raise OrderParameterNotInTemplateError(
                    parameter_name=parameter_in_payload.name,
                    template_name=template_name,
                    template_parameters=[param.name for param in order_template.input_parameters],
                )
        if parameters_payload:
            payload["inputParameters"] = parameters_payload  # pyright: ignore[reportArgumentType] # the parameters payload comes from a pydantic model_dump with mode=json, so not sure why it's not typed better to declare it being JSON-compatible
        response = self._post_request(
            query="orders",
            payload=payload,
            api_version=3,
        )
        assert isinstance(response, str), f"Expected a string, got {type(response)} with value {response}"
        return response
