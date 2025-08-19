"""
This module defines model class for the supported OpenAPI extensions to
customize the API client generation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field, ValidationError

from .input_parameters import InputParametersDescription
from .method_name import MethodNameDescription
from .pagination import PaginationDescription

if TYPE_CHECKING:
    from apier.core.api.endpoints import Endpoint


class Extensions(BaseModel):
    """
    Model class for the OpenAPI extensions defined in the `x-apier` field of
    the OpenAPI definition.
    """

    class Config:
        allow_population_by_field_name = True

    ignore: bool = Field(default=False, alias="ignore")
    pagination: Pagination = Field(default=None, alias="pagination")
    input_parameters: InputParametersDescription = Field(
        default=None, alias="input-parameters"
    )
    method_name: MethodNameDescription = Field(default=None, alias="method-name")
    response_stream: bool = Field(default=False, alias="response-stream")


class Pagination(BaseModel):
    """
    Model class for the pagination extension, which allows customizing the
    pagination behavior of the API client.
    """

    next: PaginationDescription


Extensions.update_forward_refs()


def parse_extensions(endpoint: Endpoint):
    """
    Parses the OpenAPI extensions defined in the endpoint and populates the
    `extensions` attribute of the endpoint operations.

    :param endpoint: The endpoint to parse the extensions for.
    """
    for op in endpoint.operations:
        endpoint_def = endpoint.definition.paths[endpoint.path][op.name]
        extensions_def = endpoint_def.get("x-apier")
        if not extensions_def:
            continue

        for extension_name, extension_def in extensions_def.items():
            if isinstance(extension_def, dict) and "$ref" in extension_def:
                extensions_def[extension_name] = endpoint.definition.solve_ref(
                    extension_def["$ref"]
                )

        try:
            op.extensions = Extensions.parse_obj(extensions_def)
        except ValidationError as e:
            extension_name = e.errors()[0]["loc"][0]
            raise ValueError(
                f"Invalid extension '{extension_name}' in operation '{endpoint_def.get('operationId')}': {e}"
            ) from e
