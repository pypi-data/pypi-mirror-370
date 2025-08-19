"""
This module defines the APIResource class, which is the base class for all API
resources. It provides methods to build URLs, handle requests and responses,
and manage the API call stack. It also includes methods for validating request
payloads and handling pagination.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pyexpat import ExpatError
from typing import Union, get_type_hints, get_args, Type

import requests
from requests import HTTPError, PreparedRequest, Response
from requests.structures import CaseInsensitiveDict

from .content_disposition import parse_content_disposition
from .content_type import (
    SUPPORTED_REQUEST_CONTENT_TYPES,
    content_types_match,
    content_types_compatible,
    ContentTypeValidationResult,
)
from .expressions.runtime import evaluate, prepare_request
from ..models.basemodel import APIBaseModel
from ..models.exceptions import ExceptionList, ResponseError
from ..models.extensions.pagination import PaginationDescription


def _is_api(obj):
    from ..api import API

    return isinstance(obj, API)


@dataclass
class APIResource(ABC):
    """
    Abstract class to represent a part of an API call.
    This must be inherited by any class implementing an API operation.
    """

    _stack: list = field(default_factory=list, init=False)
    """
    A list used to store the objects generated during a call chain.
    This allows to access all the information needed to make an API request,
    such as building the request URL.

    Items in the stack can be:
    - One (and only one) `API` instance. This must be the first item in the
      stack.
    - A number of `APIResource` building the request.
    """

    @abstractmethod
    def _build_partial_path(self):
        pass

    def _with_stack(self, stack: list):
        self._stack = stack
        return self

    def _child_of(self, obj):
        """
        Sets the stack of this instance to a copy of the given `APIResource`
        stack with the object itself added.
        This method is used when a new `APIResource` instance is created from
        another one.
        """
        if _is_api(obj):
            self._stack = [obj]
        else:
            self._stack = obj._stack.copy()
            self._stack.append(obj)
        return self

    def _build_url(self) -> str:
        """
        Builds and returns the URL using all the stack information.
        The first item in the stack must be an `API` instance, and the rest
        must be `APIResource` instances.
        """
        if len(self._stack) == 0 or not _is_api(self._stack[0]):
            raise RuntimeError("API instance is missing in the stack")

        return self._stack[0].host.rstrip("/") + self._build_path()

    def _build_path(self) -> str:
        """
        Builds the URL path using all the `APIResource` instances in the stack.
        """
        path = ""
        for obj in self._stack:
            if isinstance(obj, APIResource):
                path = path + obj._build_partial_path()

        return path + self._build_partial_path()

    def _path_value(self, path_param_name: str):
        """
        Returns the value of the given path parameter.
        """
        if hasattr(self, path_param_name):
            return getattr(self, path_param_name)

        for r in self._stack[1:]:
            if hasattr(r, path_param_name):
                return getattr(r, path_param_name)

        return None

    def _path_values(self) -> dict:
        """
        Returns a dictionary with the values of all the path parameters of the
        current stack.
        """
        values = {k: v for k, v in self.__dict__.items() if k != "_stack"}
        for r in self._stack[1:]:
            values.update({k: v for k, v in r.__dict__.items() if k != "_stack"})

        return values

    def _api(self):
        if len(self._stack) == 0 or not _is_api(self._stack[0]):
            raise RuntimeError("API instance is missing in the stack")
        return self._stack[0]

    def _make_request(
        self, method="GET", body=None, req_content_types: list = None, **kwargs
    ) -> Response:
        api = self._api()

        results = _validate_request_payload(
            body, req_content_types, kwargs.get("headers")
        )

        forced_content_type = kwargs.get("headers", {}).get("Content-Type")
        kwargs.pop("headers", None)  # Remove headers from kwargs to avoid duplication

        # If the Content-Type header is not explicitly provided, remove it from
        # the headers for cases where it should be set automatically
        if not forced_content_type:
            auto_content_types = ["application/json", "multipart/form-data"]
            if results.type in auto_content_types:
                results.headers.pop("Content-Type", None)

        return api.make_request(
            method,
            self._build_path(),
            data=results.data,
            json=results.json,
            files=results.files,
            headers=results.headers,
            **kwargs,
        )

    def _handle_response(
        self,
        response: requests.Response,
        expected_responses: list,
        param_types: dict = None,
        pagination_info: PaginationDescription = None,
    ):
        default_status_code = 0

        # Send default expected response to the end of the list
        expected_responses = sorted(expected_responses, key=lambda x: x[0] == 0)

        expected_status_codes = set([r[0] for r in expected_responses])
        if (
            response.status_code not in expected_status_codes
            and default_status_code not in expected_status_codes
        ):
            raise ResponseError(
                response, f"Unexpected response status code ({response.status_code})"
            )

        resp_content_type = response.headers.get("content-type", "")
        for r in expected_responses:
            code, content_type, resp_class = r

            if not content_type:
                ret = resp_class()

                ret._set_http_response(response)
                self._handle_pagination(
                    ret,
                    response,
                    pagination_info,
                    self._path_values(),
                    param_types,
                    expected_responses,
                )

                return self._handle_error(ret)

            if code not in [
                response.status_code,
                default_status_code,
            ] or not content_types_match(resp_content_type, content_type):
                continue

            resp_payload = _parse_response_content(response, resp_class)

            ret = resp_class.parse_obj(resp_payload)

            ret._set_http_response(response)
            self._handle_pagination(
                ret,
                response,
                pagination_info,
                self._path_values(),
                param_types,
                expected_responses,
            )

            return self._handle_error(ret)

        raise ResponseError(
            response, f"Unexpected response content type ({resp_content_type})"
        )

    def _handle_error(self, ret):
        api = self._stack[0]
        if api._raise_errors:
            try:
                ret.http_response().raise_for_status()
            except HTTPError as e:
                raise ResponseError(ret, str(e))

        return ret

    def _handle_pagination(
        self,
        ret: APIBaseModel,
        resp: Response,
        pagination_info: PaginationDescription,
        path_values: dict,
        params_info: dict,
        expected_responses: list,
    ):
        """
        Add metadata to the returned model object to allow handling pagination.
        """
        if pagination_info is None:
            return None

        if params_info is None:
            params_info = {}

        ret._enable_pagination(pagination_info.result)
        ret._pagination.iter_func = None

        query_params = params_info.get("query")
        headers = params_info.get("header")

        has_more = evaluate(
            resp, pagination_info.has_more, path_values, query_params, headers
        )
        if not has_more:
            return

        req = PreparedRequest()
        req.headers = CaseInsensitiveDict()
        req.prepare_url(resp.request.url, None)
        req.prepare_method(resp.request.method)
        if pagination_info.reuse_previous_request:
            req = resp.request

        for modifier in pagination_info.modifiers or []:
            value = evaluate(resp, modifier.value, path_values, query_params, headers)
            prepare_request(req, modifier.param, value)

        if pagination_info.operation_id:
            # If a next operation is defined, prepare the parameters for it
            # and set the iter_func to call the next operation using the
            # API class with flat operation methods.
            op_id = pagination_info.operation_id
            evaluated_params = {}

            for param in pagination_info.parameters or []:
                evaluated_params[param.name] = evaluate(
                    resp, param.value, path_values, query_params, headers
                )

            api = self._api()
            from .api_operations import APIOperations

            api_operations = APIOperations(api)
            if not hasattr(api_operations, op_id):
                raise ValueError(f"Next operation '{op_id}' not found in API")

            next_op = getattr(api_operations, op_id)

            ret._pagination.iter_func = lambda: next_op(**evaluated_params)
            return

        def make_request():
            api = self._api()
            new_resp = api.make_request(
                req.method, req.url, req.body, headers=req.headers
            )
            return self._handle_response(
                new_resp, expected_responses, params_info, pagination_info
            )

        ret._pagination.iter_func = make_request


def _parse_response_content(response: Response, resp_class: Type[APIBaseModel]):
    """
    Parses the response content according to its content type to ensure it
    matches the expected response class.
    """
    resp_content_type = response.headers.get("content-type", "")

    if content_types_match(resp_content_type, "application/json"):
        return response.json()

    if content_types_match(resp_content_type, "application/xml"):
        import xmltodict

        try:
            resp_payload = xmltodict.parse(response.content)
        except ExpatError as e:
            raise ResponseError(response, f"Invalid XML response: {str(e)}")

        root_name = list(resp_payload.keys())[0]
        return resp_payload[root_name]

    if content_types_match(resp_content_type, "text/plain"):
        return response.content.decode("utf-8")

    # To handle files or streams, verify that the response class has a root
    # type compatible with known file handling types
    type_hints = get_type_hints(resp_class)
    if "__root__" in type_hints:
        root_types = _extract_subtypes(type_hints["__root__"])
        root_type_names = {t.__name__ for t in root_types if hasattr(t, "__name__")}

        if "FilePayload" in root_type_names:
            from ..models.primitives import FilePayload

            filename = ""
            if content_disposition := response.headers.get("Content-Disposition"):
                if parsed_filename := parse_content_disposition(content_disposition):
                    filename = parsed_filename

            content = response.content if response._content_consumed else response.raw

            return FilePayload(
                filename=filename, content_type=resp_content_type, content=content
            )

        if "IOBase" in root_type_names:
            return response.raw

        if "bytes" in root_type_names:
            return response.content

    return None


def _extract_subtypes(tp):
    """Recursively extracts subtypes from a type hint."""
    args = get_args(tp)

    if not args:
        return {tp}

    subtypes = set()
    for arg in args:
        subtypes.update(_extract_subtypes(arg))

    return subtypes


def _validate_request_payload(
    body: Union[str, bytes, dict, APIBaseModel], req_content_types: list, headers: dict
) -> ContentTypeValidationResult:
    """
    Tries to parse the request body into one of the supported pairs of
    content-type / class type. An exception will be returned if the body
    doesn't match any of the given expected types.

    If req_content_types is None or an empty list, this is a no-op.

    :param body:              Payload of the request.
    :param req_content_types: List of tuples defining the supported types of the
                              request. The first element of each tuple is the
                              Content-Type, and the second one is the class of
                              the payload model.
    :param headers:           The headers of the request. If a Content-Type is
                              set, only the types in req_content_types that
                              matches that Content-Type will be validated.
    :return:                  A ContentTypeValidationResult object with request
                              information prepared for a specific content type.
    """
    exceptions_raised = []

    if req_content_types:
        # If Content-Type header is set, only that one is allowed
        headers = CaseInsensitiveDict(headers)
        expected_content_type = headers.get("content-type", None)
        if expected_content_type:
            req_content_types = [
                (content_type, req_class)
                for content_type, req_class in req_content_types
                if content_types_match(content_type, expected_content_type)
            ]

        for content_type, request_class in req_content_types:
            if isinstance(body, APIBaseModel) and type(body) is not request_class:
                continue

            for ct, conv_func in SUPPORTED_REQUEST_CONTENT_TYPES.items():
                if content_types_compatible(content_type, ct):
                    try:
                        result = conv_func(body)

                        # If the content types are not an exact match, update the info
                        # (e.g. application/json to application/json-patch+json)
                        if not content_types_match(content_type, ct):
                            result.type = content_type
                            result.headers["Content-Type"] = content_type

                        # Keep the headers from the request
                        if headers:
                            result.headers.update(headers)

                        return result
                    except (ValueError, ExpatError) as e:
                        exceptions_raised.append(e)

    if len(exceptions_raised) > 0:
        raise ExceptionList("Unexpected data format", exceptions_raised)

    return ContentTypeValidationResult(data=body, headers=headers)
