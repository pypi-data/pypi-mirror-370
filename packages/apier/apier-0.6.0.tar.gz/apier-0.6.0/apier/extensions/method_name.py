"""
This module defines an extension that allows overriding the name of the function
of an endpoint with the given alias name.

For example, a POST endpoint could generate a `create` method instead of `post`.

Usage:

```yaml
paths:
  /companies:
    post:
      tags:
        - Companies
      x-apier:
        method-name:
          default: create company
          templates:
            python-tree: create
            go: Create
      ...
```

This extension is defined using the `method-name` attribute inside the
extension attribute definition. The following attributes can be defined:
  - `default`: The generic name of the function. If the template for the client
    being generated is not included in `templates`, this value will be used.
    The function name will depend on the template used and the naming conventions
    employed by it.
    If neither the `default` value nor one in `templates` is defined for the
    used template, the method name will be used (`post`, `get`, ...).
    If the name consists of multiple words, they should be separated by a space.
  - `templates`: A map with the names of the templates and the name the function
    will have for each of them. If the template for the client being generated
    is not included, the `default` value will be used.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class MethodNameDescription(BaseModel):
    class Config:
        allow_population_by_field_name = True

    default: str = ""
    templates: dict[str, str] = Field(default_factory=dict)
