import json
import mimetypes
from dataclasses import dataclass, field
from io import IOBase
from typing import Any, Optional, Union
from urllib.parse import parse_qsl

import xmltodict
from requests.structures import CaseInsensitiveDict

from ..models.basemodel import APIBaseModel
from ..models.primitives import FilePayload


class ContentType:
    """
    Represents a Content-Type.
    """

    def __init__(self, content_type: str):
        self.content_type = content_type
        components = parse_content_type(content_type)
        self.media_type = components["media_type"]
        self.type = components["type"]
        self.subtype = components["subtype"]
        self.suffix = components["suffix"]
        self.parameters = components["parameters"]

    def __eq__(self, other):
        return content_types_match(self.content_type, other.content_type)

    def __str__(self):
        return self.content_type

    def __repr__(self):
        return f"ContentType({self.content_type})"


def parse_content_type(content_type):
    """
    Parses a Content-Type into its components.

    :param content_type: The Content-Type to parse.
    :return:  A dictionary with the components of the Content-Type.
    """
    # Split the main type from the parameters
    media_type, *params = content_type.split(";")
    media_type = media_type.strip()

    # Split the base type and the suffix
    base_type, _, suffix = media_type.partition("+")

    # Split the type and subtype
    main_type, _, subtype = base_type.partition("/")

    # Parse parameters into a dictionary
    parameters = {
        key.strip(): value.strip()
        for key, value in parse_qsl(";".join(params).replace(";", "&"))
    }

    return {
        "media_type": media_type,  # Full media type (e.g., application/json-patch+json)
        "type": main_type,  # Main type (e.g., application)
        "subtype": subtype,  # Subtype (e.g., json-patch)
        "suffix": (
            suffix if suffix else None
        ),  # Suffix (e.g., json), or None if not present
        "parameters": parameters,  # Parameters (e.g., {'charset': 'utf-8'})
    }


def content_types_compatible(type1: str, type2: str):
    """
    Checks if two Content-Types are compatible (i.e., if they use the same
    underlying format).
    """
    parsed_type1 = parse_content_type(type1)
    parsed_type2 = parse_content_type(type2)

    if parsed_type1["type"] != parsed_type2["type"]:
        return False

    if "*" in [parsed_type1["subtype"], parsed_type2["subtype"]]:
        return True

    suffix1 = parsed_type1["suffix"] or parsed_type1["subtype"]
    suffix2 = parsed_type2["suffix"] or parsed_type2["subtype"]
    return suffix1 == suffix2


def content_types_match(type1: str, type2: str) -> bool:
    """
    Returns whether the given Content-Types match.
    """
    t1, t2 = type1.lower().split(";")[0], type2.lower().split(";")[0]
    if "*/*" in [t1, t2]:
        return True
    return t1 == t2


@dataclass
class ContentTypeValidationResult:
    """
    Represents the result of preparing a request payload for a specific
    Content-Type.
    """

    type: str = ""  # The request's Content-Type, indicating the data format
    data: Any = None
    files: Optional[dict] = None
    json: Optional[Union[dict, list]] = None
    headers: CaseInsensitiveDict = field(default_factory=dict)


def to_plain_text(obj) -> ContentTypeValidationResult:
    """
    Returns the plain text representation of the given object.
    """
    return ContentTypeValidationResult(
        type="text/plain",
        data=str(obj),
        headers=CaseInsensitiveDict({"Content-Type": "text/plain"}),
    )


def to_form_urlencoded(obj) -> ContentTypeValidationResult:
    """
    Returns the form-urlencoded representation of the given object.
    Raises an exception if the object cannot be serialized to a valid
    application/x-www-form-urlencoded format.
    """
    result = ContentTypeValidationResult(
        type="application/x-www-form-urlencoded",
        headers=CaseInsensitiveDict(
            {"Content-Type": "application/x-www-form-urlencoded"}
        ),
    )

    if isinstance(obj, (str, bytes)):
        result.data = str(obj)
    elif isinstance(obj, dict):
        result.data = obj
    elif isinstance(obj, APIBaseModel):
        result.data = json.loads(obj.json(by_alias=True))
    else:
        raise ValueError(
            f'Value type "{type(obj).__name__}" cannot be converted to form-urlencoded'
        )

    return result


def to_json(obj) -> ContentTypeValidationResult:
    """
    Returns the JSON representation of the given object.
    Raises an exception if the object cannot be serialized to a valid JSON.
    """
    result = ContentTypeValidationResult(
        type="application/json",
        headers=CaseInsensitiveDict({"Content-Type": "application/json"}),
    )

    if isinstance(obj, (str, bytes)):
        result.json = json.loads(obj)
    elif isinstance(obj, (dict, list)):
        result.json = obj
    elif isinstance(obj, APIBaseModel):
        # obj.dict() performs a shallow conversion, so a second conversion is
        # used for a deeper JSON transformation
        result.json = json.loads(obj.json(by_alias=True))
    else:
        raise ValueError(
            f'Value type "{type(obj).__name__}" cannot be converted to JSON'
        )

    return result


def to_xml(obj) -> ContentTypeValidationResult:
    """
    Returns the XML representation of the given object.
    Raises an exception if the object cannot be serialized to a valid XML.
    """
    result = ContentTypeValidationResult(
        type="application/xml",
        headers=CaseInsensitiveDict({"Content-Type": "application/xml"}),
    )

    if isinstance(obj, (str, bytes)):
        xmltodict.parse(obj)
        result.data = str(obj)
        return result
    elif isinstance(obj, dict):
        obj_dict = obj
    elif isinstance(obj, APIBaseModel):
        obj_dict = json.loads(obj.json(by_alias=True))
    else:
        raise ValueError(
            f'Value type "{type(obj).__name__}" cannot be converted to XML'
        )

    obj_dict = {"root": obj_dict}
    result.data = xmltodict.unparse(obj_dict)
    return result


def to_multipart(obj) -> ContentTypeValidationResult:
    """
    Converts the given object to a multipart representation.
    Returns the data and files to be sent in a multipart/form-data request.
    """
    if isinstance(obj, dict):
        obj_dict = obj
    elif isinstance(obj, APIBaseModel):
        obj_dict = obj.dict(by_alias=True)
    else:
        raise ValueError(
            f'Value type "{type(obj).__name__}" cannot be converted to multipart/form-data'
        )

    data = {}
    files = {}

    for key, value in obj_dict.items():
        if isinstance(value, (bytes, IOBase)):
            name = key
            content_type = "application/octet-stream"
            if hasattr(value, "name"):
                if filename := value.name.split("/")[-1]:
                    name = filename

                content_type_guess, _ = mimetypes.guess_type(value.name)
                if content_type_guess:
                    content_type = content_type_guess

            files[key] = (name, value, content_type)

        elif isinstance(obj[key], FilePayload):
            value: FilePayload = obj[key]
            files[key] = (value.filename, value.content, value.content_type)

        else:
            data[key] = value

    return ContentTypeValidationResult(
        type="multipart/form-data",
        data=data,
        files=files,
        headers=CaseInsensitiveDict({"Content-Type": "multipart/form-data"}),
    )


SUPPORTED_REQUEST_CONTENT_TYPES = {
    "application/x-www-form-urlencoded": to_form_urlencoded,
    "application/json": to_json,
    "application/xml": to_xml,
    "text/plain": to_plain_text,
    "multipart/form-data": to_multipart,
}
