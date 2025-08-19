import warnings

from apier.core.api.openapi import Definition


def parse_security_schemes(definition: Definition) -> list[str]:
    """
    Returns the list of security scheme names that are supported by this
    template. If a non-supported security scheme is found, a warning will be
    issued.
    """
    security_scheme_names = []

    security_schemas = definition.get_value("components.securitySchemes", default=None)
    if not security_schemas:
        return security_scheme_names

    for name, security_scheme in security_schemas.items():
        scheme_type = security_scheme["type"]

        if scheme_type == "http":
            if security_scheme["scheme"] in ["basic", "bearer"]:
                security_scheme_names.append(name)
                continue

        if scheme_type == "oauth2":
            for flow_name, flow in security_scheme["flows"].items():
                if flow_name == "clientCredentials":
                    security_scheme_names.append(name)
                    continue
                else:
                    warnings.warn(
                        f"Security scheme '{name}' has an unsupported OAuth2 "
                        f"flow type '{flow_name}' and will be ignored"
                    )
                    continue

            continue

        warnings.warn(
            f"Security scheme '{name}' has an unsupported security "
            f"schema type '{scheme_type}' and will be ignored"
        )

    return security_scheme_names
