from functools import reduce
from typing import Union


class _Default:
    """Unique class to signal that no default value has been provided."""

    pass


_default = _Default()


def get_nested(
    d: Union[dict, object], key: str, separator: str = ".", default=_default
):
    """
    Returns the value of the object or dictionary given by a key, which can define
    multiple levels (e.g. "info.version").

    :param d: The object or dictionary.
    :param key: The key of the value that will be returned. It can define
                multiple levels by using a separator (which is '.' by default).
    :param separator: The separator of a multi-level key.
    :param default: The default value that will be returned if the key is not
                    found.
    :return: The value of the given key. It raises a KeyError if the value
             is not found and default is not set.
    """
    try:

        def get_item(a, b):
            if isinstance(a, list):
                return a[int(b)]
            elif isinstance(a, dict):
                return a[b]
            elif hasattr(a, b):
                return getattr(a, b)
            raise KeyError

        return reduce(get_item, key.split(separator), d)
    except KeyError:
        if default != _default:
            return default
        raise KeyError(f"Key '{key}' not found")
    except IndexError:
        if default != _default:
            return default
        raise IndexError(f"Index '{key}' out of range")
