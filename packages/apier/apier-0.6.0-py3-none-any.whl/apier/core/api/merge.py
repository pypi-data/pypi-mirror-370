import json
import warnings

import yaml
from onedict.merger import merge
from onedict.solvers import unique_lists, Skip


class MergeWarning(Warning):
    """
    Custom exception used as a warning when merging dictionaries. A warning
    is raised when a conflict is detected but the conflict is resolved by
    a solver function.
    """

    def __init__(self, spec_filename, key, value1, value2, max_length=100):
        super().__init__(key, value1, value2)
        self.spec_filename = spec_filename
        self.key = key
        self.value1 = value1
        self.value2 = value2
        self.max_length = max_length

    def __str__(self):
        message = f"Key '{self.key}'"

        value1 = self.value1
        if isinstance(value1, str):
            value1 = value1.replace("\n", "\\n")
            if len(value1) > self.max_length:
                value1 = value1[: self.max_length] + "..."
            value1 = f"'{value1}'"

        value2 = self.value2
        if isinstance(value2, str):
            value2 = value2.replace("\n", "\\n")
            if len(value2) > self.max_length:
                value2 = value2[: self.max_length] + "..."
            value2 = f"'{value2}'"

        return f"{message}: {value1} != {value2}"


current_spec_filename = None


def solver_string(keys, value1, value2):
    """
    This solver resolves conflicts between two string values by keeping the
    first value and issuing a warning.
    """
    if not isinstance(value1, str) or not isinstance(value2, str):
        return Skip()
    warnings.warn(
        MergeWarning(current_spec_filename, keys, value1, value2, max_length=100)
    )
    return value1


def merge_specs(*specs: dict) -> dict:
    """
    Merge multiple OpenAPI specs into one.
    :param specs: List of OpenAPI specs to merge.
    :return: The merged OpenAPI spec.
    """
    merged_spec = {}
    for spec in specs:
        merged_spec = merge(
            merged_spec, spec, conflict_solvers=[unique_lists, solver_string]
        )
    return merged_spec


def merge_spec_files(*files: str) -> dict:
    """
    Merge multiple OpenAPI files into one.
    :param files: List of file paths to merge.
    :return: The merged OpenAPI spec and a dictionary of warnings.
    """
    global current_spec_filename

    merged_spec = {}

    for spec_filename in files:
        current_spec_filename = spec_filename
        with open(spec_filename, "r") as f:
            if spec_filename.endswith(".json"):
                spec_dict = json.load(f)
            else:
                spec_dict = yaml.safe_load(f)

        merged_spec = merge_specs(merged_spec, spec_dict)

    return merged_spec
