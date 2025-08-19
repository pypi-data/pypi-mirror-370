import re
from typing import Union

from apier.core.api.endpoints import ContentSchema, EndpointOperation, EndpointLayer
from apier.core.api.tree import APITree
from apier.core.consts import NO_RESPONSE_ID
from apier.utils.strings import to_snake_case


def get_type_hint(
    *args: Union[str, ContentSchema], include_primitive_type: bool = False
) -> str:
    """
    Returns the type string associated to the given array of schemas so that
    it can be used for type hints.

    >>> get_type_hint(ContentSchema(name='MyType'))
    'models.MyType'
    >>> get_type_hint('string')
    'str'
    >>> get_type_hint('string', 'integer')
    'Union[str, int]'
    >>> get_type_hint(ContentSchema(name='MyType'), 'array')
    'Union[models.MyType, list]'
    >>> get_type_hint(ContentSchema(name='MyType', schema={'type': 'object'}), include_primitive_type=True)
    'Union[models.MyType, dict]'

    :param args:    List of type strings and/or ContentSchema instances.
    :param include_primitive_type: If True, the primitive type of the
                    ContentSchema instances will be added to the output.
                    The 'type' must be defined in the ContentSchema definition.
    :return:        Type hint.
    """
    if len(args) == 0:
        return ""

    types_map = {
        "string": "str",
        "number": "float",
        "integer": "int",
        "object": "dict",
        "array": "list",
        "boolean": "bool",
        "null": "None",
    }

    types = []
    for i, t in enumerate(args):
        if isinstance(t, str):
            if t in types_map:
                types.append(types_map.get(t.lower(), t))
            else:
                types.append(t)
        elif isinstance(t, ContentSchema):
            if t.name in [NO_RESPONSE_ID, ""]:
                types.append("primitives.NoResponse")
                break
            types.append("models." + t.name)
            if include_primitive_type and "type" in t.schema:
                types.append(types_map[t.schema["type"]])
        else:
            raise ValueError("Invalid type")

    types = list(dict.fromkeys(types))
    if len(types) == 1:
        return types[0]
    else:
        return f"Union[{', '.join(types)}]"


def payload_from_input_parameters(endpoint_method: EndpointOperation) -> str:
    """
    Returns the code to dynamically generate the payload of an endpoint that
    uses the input-parameters extension.
    """
    try:
        params = {}
        for method_param in endpoint_method.parameters:
            if method_param.in_location == "path":
                params[method_param.name] = (
                    f"self._path_value('{to_snake_case(method_param.name)}')"
                )
            elif method_param.in_location in ["query", "header"]:
                params[method_param.name] = f"params[{method_param.name}]"

        for input_param in endpoint_method.extensions.input_parameters.parameters:
            params[input_param.name] = to_snake_case(input_param.name)

        supported_filters = {
            "str": lambda x: f"str({x})",
            "json": lambda x: f"json.dumps({x})",
        }

        payload_str = endpoint_method.extensions.input_parameters.payload

        escaped_expression = payload_str.replace('"', '\\"')

        # Find and replace the variables in the expression
        variables = re.findall(r"{{([^{].*?[^}])}}", escaped_expression)
        for var in variables:
            var_name, *filters = var.split("|")
            param_name = params[var_name.strip()]

            partial_escaped_expression = param_name

            # Apply filters
            if not filters:
                filters.append("str")

            for f in filters:
                f = f.strip()
                if f not in supported_filters:
                    raise ValueError(f"Unknown function {filters}")

                partial_escaped_expression = supported_filters[f](
                    partial_escaped_expression
                )

            escaped_expression = escaped_expression.replace(
                "{{" + var + "}}", '" + ' + partial_escaped_expression + ' + "'
            )

        escaped_expression = f'"{escaped_expression}"'

        if escaped_expression.startswith('"" +'):
            escaped_expression = escaped_expression[len('"" +') :]
        if escaped_expression.endswith('+ ""'):
            escaped_expression = escaped_expression[: -len('+ ""') :]

        return escaped_expression

    except ValueError as e:
        raise ValueError(f"Error building payload from input-parameters extension: {e}")


def get_method_name(endpoint_operation: EndpointOperation) -> str:
    """
    Returns the name of the function used in the client for the given endpoint
    method. By default, the name will be the HTTP method name, but this may
    change if the method-name extension is defined.
    """
    if endpoint_operation.extensions and endpoint_operation.extensions.method_name:
        extension_info = endpoint_operation.extensions.method_name

        from apier.templates.python_tree.renderer import TEMPLATE_NAME

        if TEMPLATE_NAME in extension_info.templates:
            return to_snake_case(extension_info.templates[TEMPLATE_NAME])

        if extension_info.default:
            return to_snake_case(extension_info.default)

    return to_snake_case(endpoint_operation.name)


def chain_layers(api_tree: APITree, path: str) -> list[EndpointLayer]:
    _, _, layers = api_tree.search_path(path)
    if not layers:
        raise Exception(f"path '{path}' not found")

    # layers.reverse()
    return layers
    # api_names = [l.api_levels[0]+'()' for l in layers]
    # return '.'.join(api_names)
