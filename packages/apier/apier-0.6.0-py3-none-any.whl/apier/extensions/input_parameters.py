"""
This module defines an extension that allows overriding the function arguments
of an endpoint with others, allowing customization or simplification of the way
to interact with that endpoint.

This way, a function that takes the request payload as an argument (default
behavior) could only require specific values that will be used for constructing
the payload.

NOTE: This is a demo feature and needs more work, so it is subject to changes.
"""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class Schema(BaseModel):
    type: str


class Parameter(BaseModel):
    name: str
    description: str = ""
    schema_: Schema = Field(default=None, alias="schema")


class InputParametersDescription(BaseModel):
    class Config:
        allow_population_by_field_name = True

    parameters: List[Parameter]
    payload: str


InputParametersDescription.update_forward_refs()
