import copy
import shutil
from pathlib import Path

import yaml
from datamodel_code_generator import InputFileType, generate

from apier.core.api.openapi import Definition


def generate_models(definition: Definition, schemas: dict[str, dict], output_path: str):
    """
    Generate the Pydantic models for all the given schemas.

    :param definition:  The OpenAPI definition object.
    :param schemas:     The dictionary of schemas that will be generated as
                        models.
    :param output_path: The output directory.
    """
    openapi_output = copy.deepcopy(definition.definition)
    openapi_output["components"] = {"schemas": schemas}
    filename = f"{output_path}/_temp/schemas.yaml"

    file = Path(filename)
    file.parent.mkdir(parents=True, exist_ok=True)
    with file.open("w") as f:
        yaml.dump(openapi_output, f)

    pkg_name = __name__.rsplit(".", 1)[0]
    custom_formatter = f"{pkg_name}.formatter"

    generate(
        input_=Path(filename),
        input_file_type=InputFileType.OpenAPI,
        output=Path(f"{output_path}/models/models.py"),
        base_class=".basemodel.APIBaseModel",
        custom_formatters=[custom_formatter],
    )

    shutil.rmtree(f"{output_path}/_temp")
