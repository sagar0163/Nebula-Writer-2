"""Regression test: no duplicate method definitions shadowing each other (issue #143).

Python resolves duplicate method names with last-definition-wins, so a stray
duplicate definition silently shadows the correct implementation at runtime.
This test scans every class in the package and fails if any method name is
defined more than once unless the duplicates are the legitimately paired
@property/@<name>.setter (or .deleter/.getter) descriptors.
"""

import ast
from pathlib import Path

import nebula_writer

_PROPERTY_DESCRIPTORS = {"property", "setter", "deleter", "getter"}


def _package_paths():
    return sorted(Path(nebula_writer.__file__).parent.glob("*.py"))


def _is_property_descriptor_pair(decorator_ids):
    return bool(decorator_ids) and all(d in _PROPERTY_DESCRIPTORS for d in decorator_ids)


def _find_duplicate_methods(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    problems = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        definitions = {}
        for item in node.body:
            if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            definitions.setdefault(item.name, []).append(item)
        for method, items in definitions.items():
            if len(items) <= 1:
                continue
            decorators = [
                getattr(d, "id", None) or getattr(d, "attr", None)
                for item in items
                for d in item.decorator_list
            ]
            if _is_property_descriptor_pair(decorators):
                continue
            problems.append(
                f"{path.name}:{node.name}.{method} defined {len(items)}x at lines "
                f"{[i.lineno for i in items]}"
            )
    return problems


def test_no_duplicate_method_definitions():
    problems = []
    for path in _package_paths():
        problems.extend(_find_duplicate_methods(path))
    assert not problems, "Duplicate method definitions found:\n" + "\n".join(problems)
