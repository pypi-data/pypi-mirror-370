"""
This module provides functionality to render an API client using a specified template.
"""

import importlib
import os
import sys
from importlib import import_module
from pathlib import Path
from typing import Union

from apier.core.api.endpoints import Endpoint
from apier.core.api.openapi import Definition

builtin_template_map = {
    "python-tree": "python_tree",
}


def render_api(
    ctx,
    template: Union[str, Path],
    definition: Definition,
    schemas: dict,
    endpoints: list[Endpoint],
    output_path: str,
):
    """
    Render the API client using the specified template.

    The template can be a built-in template name (e.g. 'python-tree') or a
    path to a directory containing a custom template with the required structure.

    :param ctx: Context dictionary containing configuration options.
    :param template: The template to use for rendering. Can be a string for
                     built-in templates or a Path object for custom templates.
    :param definition: The OpenAPI definition to use for rendering.
    :param schemas: The schemas defined in the OpenAPI specification.
    :param endpoints: The list of endpoints parsed from the OpenAPI definition.
    :param output_path: The path where the generated client code will be saved.
    """

    if ctx is None:
        ctx = {"verbose": False, "output_logger": print}

    if not os.path.isabs(output_path):
        output_path = os.path.normpath(os.path.join(os.getcwd(), output_path))

    try:
        if isinstance(template, str):
            # Use a built-in template
            template = builtin_template_map.get(template)
            renderer = import_module(f"apier.templates.{template}.renderer").Renderer(
                ctx, definition, schemas, endpoints, output_path
            )

        elif isinstance(template, Path):
            # Use a custom template directory. The directory must be
            # registered as a package and imported dynamically.

            template_path = template.resolve()
            package_name = f"apier.templates.{template_path.stem}"

            # Register the external directory as a package
            sys.modules[package_name] = importlib.util.module_from_spec(
                importlib.machinery.ModuleSpec(package_name, None, is_package=True)
            )

            # Add the parent directory of the template to sys.path
            sys.path.insert(0, str(template_path.parent))

            # Load all Python files in the directory as package modules
            for file in template_path.glob("*.py"):
                if file.stem == "__init__":
                    continue  # Saltar __init__.py si existe
                module_name = f"{package_name}.{file.stem}"
                spec = importlib.util.spec_from_file_location(module_name, file)
                if spec is None or spec.loader is None:
                    raise ImportError(f"No se pudo cargar {file}")

                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)  # Ejecuta el módulo

            # Import and execute the renderer module
            render_module = importlib.import_module(f"{package_name}.renderer")
            renderer_class = getattr(render_module, "Renderer")
            renderer = renderer_class(ctx, definition, schemas, endpoints, output_path)
        else:
            raise ValueError("Template must be a string or a Path object")

    except ModuleNotFoundError:
        raise ValueError(f"Template '{template}' not found")

    except AttributeError:
        raise ValueError(f"Template '{template}' does not have a Renderer class")

    renderer.render()
