from typing import Mapping, Any

from openapi_spec_validator import validate
from openapi_spec_validator.readers import read_from_filename

from apier.utils.data_access import get_nested, _default


class Definition:
    """
    An OpenAPI definition.
    """

    def __init__(self, definition: dict):
        self.definition = definition

    @staticmethod
    def load(filename):
        """
        Loads an OpenAPI definition file.
        :param filename: OpenAPI definition file.
        :return: Definition loaded from file.
        """
        spec_dict, _ = read_from_filename(filename)
        validate(spec_dict)
        return Definition(dict(spec_dict))

    @property
    def paths(self) -> dict:
        """
        Returns all the endpoint paths of this definition.

        :return: The paths content of this definition.
        """
        return self.definition["paths"]

    def get_value(self, key: str, separator: str = ".", default=_default):
        """
        Returns the value of the definition given by a key, which can define
        multiple levels (e.g. "info.version").

        :param key: The key of the value that will be returned. It can define
                    multiple levels by using a separator (which is '.' by default).
        :param separator: The separator of a multi-level key.
        :param default: The default value that will be returned if the key is not
                        found.
        :return: The definition value of the given key. It raises a KeyError if
                 the value is not found and default is not set.
        """
        try:
            return get_nested(self.definition, key, separator, default)
        except KeyError:
            raise KeyError(f"Key '{key}' not found")

    def solve_ref(self, ref: str) -> Mapping[str, Any]:
        """
        Returns the definition of the given reference ($ref).
        :param ref: A definition reference (e.g. "#/components/schemas/Store").
        :return: The reference defintion. It raises a KeyError if the value
                 is not found.
        """
        ref_clean = ref.replace("#/", "")
        try:
            return self.get_value(ref_clean, "/")
        except KeyError:
            raise KeyError(f"Reference '{ref}' not found")
