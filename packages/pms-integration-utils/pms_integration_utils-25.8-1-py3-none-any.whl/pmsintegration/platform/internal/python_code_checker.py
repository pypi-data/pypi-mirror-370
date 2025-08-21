import ast
import os
import typing


def find_imports(file_path) -> set[str]:
    with open(file_path, 'r', encoding="utf-8") as f:
        tree = ast.parse(f.read())
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)  # Get top-level package
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)  # Get top-level package
    return imports


def find_python_files(directory: str) -> typing.Generator[str, None, None]:
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                yield file_path
