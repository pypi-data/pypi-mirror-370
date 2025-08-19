"""
This module provides a custom code formatter for datamodel-code-generator to
customize the generated Pydantic models.
"""

import ast
from dataclasses import dataclass

import astor
from datamodel_code_generator.format import CustomCodeFormatter


@dataclass
class ModelTypeReplacer:
    """
    A dataclass that defines how to replace specific types in Pydantic models.
    """

    target: str
    extra_imports: list[tuple[str, list[str]]] = None
    arbitrary_types_allowed: bool = (
        False  # Whether to allow arbitrary types in the model's Config class
    )


type_mapping = {
    "bytes": ModelTypeReplacer(
        target="Union[bytes, IO, IOBase, FilePayload]",
        extra_imports=[
            ("typing", ["Union", "IO"]),
            ("io", ["IOBase"]),
            (".primitives", ["FilePayload"]),
        ],
        arbitrary_types_allowed=True,
    ),
}


class CodeFormatter(CustomCodeFormatter):
    """
    A custom datamodel-code-generator formatter that applies type replacements.
    """

    def apply(self, code: str) -> str:
        code = convert_types(code)
        return code


class TypeTransformer(ast.NodeTransformer):
    """
    A custom AST transformer that replaces specific types in Pydantic models
    according to the given type mapping information.
    """

    def __init__(self, mapping: dict[str, ModelTypeReplacer]):
        self.types = mapping
        self.replaced_types = set()

    def visit_ClassDef(self, node):
        arbitrary_types_allowed = False

        for stmt in node.body:
            if isinstance(stmt, ast.AnnAssign):
                new_annotation, changed = self.replace_type(stmt.annotation)
                if changed:
                    stmt.annotation = new_annotation
                    arbitrary_types_allowed = True

        if arbitrary_types_allowed:
            self.ensure_config_with_arbitrary_types(node)

        return node

    def replace_type(self, annotation):
        """Recursively replace types inside the annotation AST."""
        arbitrary_types_allowed = False

        if isinstance(annotation, ast.Name):
            if annotation.id in self.types:
                self.replaced_types.add(annotation.id)
                new_node = ast.parse(self.types[annotation.id].target).body[0].value
                return new_node, self.types[annotation.id].arbitrary_types_allowed

        elif isinstance(annotation, ast.Subscript):
            annotation.slice, slice_changed = self.replace_type(annotation.slice)
            annotation.value, val_changed = self.replace_type(annotation.value)
            changed = slice_changed or val_changed
            return annotation, changed

        elif isinstance(annotation, ast.Tuple):
            # e.g. Union[bytes, None]
            new_elts = []
            for elt in annotation.elts:
                new_elt, elt_changed = self.replace_type(elt)
                new_elts.append(new_elt)
                arbitrary_types_allowed |= elt_changed
            annotation.elts = new_elts
            return annotation, arbitrary_types_allowed

        elif isinstance(annotation, ast.Attribute):
            # like typing.Optional, no replacement needed here
            return annotation, False

        return annotation, False

    def ensure_config_with_arbitrary_types(self, class_node):
        """Ensure that the Config class exists with arbitrary_types_allowed set to True."""
        # Check if Config class exists
        config_class = next(
            (
                n
                for n in class_node.body
                if isinstance(n, ast.ClassDef) and n.name == "Config"
            ),
            None,
        )

        if not config_class:
            config_class = ast.ClassDef(
                name="Config", bases=[], keywords=[], body=[], decorator_list=[]
            )
            class_node.body.append(config_class)

        for conf in ["arbitrary_types_allowed"]:
            if not any(
                isinstance(stmt, ast.Assign)
                and isinstance(stmt.targets[0], ast.Name)
                and stmt.targets[0].id == conf
                for stmt in config_class.body
            ):
                config_class.body.append(
                    ast.Assign(
                        targets=[ast.Name(id=conf, ctx=ast.Store())],
                        value=ast.Constant(value=True),
                    )
                )


def add_imports(tree: ast.Module, import_list: list[tuple[str, list[str]]]) -> None:
    """Add missing imports to the AST tree."""
    # Get existing imports to avoid duplicates
    existing_imports = {
        alias.name
        for node in tree.body
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }

    last_import_index = max(
        i
        for i, node in enumerate(tree.body)
        if isinstance(node, (ast.Import, ast.ImportFrom))
    )

    for module, names in import_list:
        missing = [
            ast.alias(name=name, asname=None)
            for name in names
            if name not in existing_imports
        ]
        if missing:
            # Add import statement after the last import
            import_node = ast.ImportFrom(module=module, names=missing, level=0)
            tree.body.insert(last_import_index + 1, import_node)
            last_import_index += 1


def convert_types(code: str) -> str:
    """
    Converts specific types in the given code to their replacements defined
    in type_mapping.
    """
    tree = ast.parse(code)

    transformer = TypeTransformer(type_mapping)
    transformed_tree = transformer.visit(tree)

    # Collect imports needed for replaced types
    extra_imports = []
    for type_replaced in transformer.replaced_types:
        if type_replaced in type_mapping:
            for item in type_mapping[type_replaced].extra_imports:
                if item not in extra_imports:
                    extra_imports.append(item)

    add_imports(transformed_tree, extra_imports)

    code = astor.to_source(transformed_tree)
    return code
