"""
This module provides functionality to build an API client from one or more
OpenAPI specification files.
"""

from pathlib import Path
from typing import Union, List

from apier.core.api.endpoints import EndpointsParser
from apier.core.api.merge import merge_spec_files
from apier.core.api.openapi import Definition
from apier.core.renderer import render_api


def build(
    ctx, template: Union[str, Path], filename: Union[str, List], output_path="_build/"
):
    """
    Build the API client from the given OpenAPI file(s).

    :param ctx: A context dictionary.
    :param template: The template to use. If it is a string, it must be a
                     built-in template. If it is a Path, it must be the
                     directory containing a custom template.
    :param filename: The OpenAPI file(s) to use.
    :param output_path: The output directory.
    """
    if isinstance(filename, str):
        definition = Definition.load(filename)
    elif len(filename) == 1:
        definition = Definition.load(filename[0])
    else:
        merged_spec = merge_spec_files(*filename)
        definition = Definition(merged_spec)

    parser = EndpointsParser(definition)

    endpoints = []
    for path in definition.paths:
        endpoints.append(parser.parse_endpoint(path))

    render_api(ctx, template, definition, parser.schemas, endpoints, output_path)
