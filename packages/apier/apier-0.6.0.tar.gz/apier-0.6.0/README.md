<h2 align="center"><b>apier</b></h3>

<p align="center">A Python tool to turn OpenAPI specifications into API client libraries</p>

<p align="center">
  <a href="https://pypi.org/project/apier"><img src="https://img.shields.io/badge/pip_install-apier-orange" alt="pip command"></a>
  <a href="https://pypi.org/project/apier"><img src="https://img.shields.io/pypi/pyversions/apier.svg?logo=python" alt="Supported Versions"></a>
</p>

## 🧐 What is _apier_?

**apier** is a Python tool that automatically generates API client libraries from OpenAPI specifications. It uses a templates to allow developers to customize the structure, interface, or target programming language of the generated clients using templates, making it easier to integrate and interact with external APIs in their projects. This approach can help automate the process of creating and maintaining client libraries for external APIs, supporting consistency across projects and making it easier to keep libraries up to date as the API specification evolves.

apier provides a command-line interface (CLI) for building client libraries and merging OpenAPI documents.

> 🐣 This project is in pre-1.0.0. Expect breaking changes in minor and patch versions.

## 🐍 Installation

apier is available on PyPI:

```bash
pip install apier
```

Requires Python 3.9+.

## 🧠 Main Concepts

The following concepts are central to understanding how this project works and how it can be used to generate and maintain API client libraries from OpenAPI specifications:

- **OpenAPI Specification**: OpenAPI documents serve as the source of truth for describing the structure, endpoints, and data models of an API. The specification provides a standardized way to define available operations, request and response formats, authentication methods, and other aspects of the API contract.

- **Client Generation**: Client libraries are produced to enable applications to interact with APIs described by OpenAPI specifications. This process involves parsing the specification and generating code that implements the described endpoints, data models, and authentication flows. Clients can be rebuilt as the API specification changes, helping to keep integrations aligned with the latest API version.

- **Templating System**: A flexible templating system defines the structure, interface, and target language of the generated clients. Templates control the organization and style of the output code, and can be customized or extended to fit different requirements or programming languages. This enables adaptation to various coding standards or project needs.

## ⚡ Usage

apier provides a command-line interface (CLI) for generating client libraries and performing related operations. Supported commands are:

- **build**: Generates a client library from an OpenAPI specification. Provide the path to the specification, the output directory, and the template to use. This command produces a client library based on the given inputs.

- **merge**: Merges multiple OpenAPI documents into a single specification. The resulting document can then be used for client generation or other purposes.

Typical usage:

```
apier build --input path/to/openapi.yaml --output path/to/output/dir --template python-tree
```

Refer to the [CLI documentation](docs/cli/README.md) for detailed command usage and options.

### Example

A generated client library can be used to make requests to the API, handle responses, and manage authentication.

```python
from my_api_client import API
from my_api_client.security import BasicAuthentication

api = API(security_strategy=BasicAuthentication(username='user', password='pass'))

employee = api.companies("my_company").departments("my_department").employees(123).get()
print(f"Employee Name: {employee.name}")
```

## 🏗️ Templating System

apier uses a templating system to control how client libraries are generated. Templates define the structure, interface, and target programming language of the output code, allowing customization to fit different requirements or coding standards.

A selection of built-in templates is available for common scenarios. These templates can be used as-is or extended to create custom client libraries tailored to specific needs. Alternatively, you can create your own templates from scratch to define a completely custom structure and style for the generated code or to support different programming languages.

Currently, the only built-in template available is [`python-tree`](docs/templates/python_tree.md), which generates a Python client library with a hierarchical structure that mirrors the organization of REST API endpoints. This design allows developers to interact with nested resources through chainable methods, making the client intuitive and closely aligned with the API's structure.

More built-in templates may be added in the future.

For more information on available templates, how to use them, and how to create your own, see the [templating documentation](docs/templates/README.md).

## 🧩 OpenAPI Extensions
apier supports OpenAPI extensions to enhance the generated client libraries with additional metadata or functionality. Extensions can be used to customize the method names, add pagination support, or include other features to define how the client interacts with the API.

See the [OpenAPI extensions documentation](docs/extensions/README.md) for a list of supported extensions and how to use them in your OpenAPI specifications.

## 🚧️ Limitations

apier is a work in progress and may not support all OpenAPI features or edge cases 🦄. Currently, it supports OpenAPI 3.0 and 3.1, but some features may not be fully implemented or tested.

If you encounter any issues or have feature requests, please let me know and I will do my best to address them in future releases. 🙏
