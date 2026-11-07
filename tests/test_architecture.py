import ast
from pathlib import Path

import pytest

PACKAGE = "redragon_monitor"
SOURCE = Path(__file__).resolve().parent.parent / "src" / PACKAGE

ALLOWED_FEATURES = {
    "shared": {"shared"},
    "device": {"device", "shared"},
    "battery": {"battery", "device", "shared"},
    "alert": {"alert", "battery", "device", "shared"},
    "autostart": {"autostart", "shared"},
    "update": {"update", "shared"},
}
ALLOWED_LAYERS = {
    "domain": {"domain"},
    "application": {"domain", "application"},
    "infrastructure": {"domain", "application", "infrastructure"},
}
OUTER_PACKAGES = {"presentation", "bootstrap"}


def feature_modules():
    for path in sorted(SOURCE.rglob("*.py")):
        parts = path.relative_to(SOURCE).with_suffix("").parts
        if parts[0] in ALLOWED_FEATURES:
            yield path, parts


def imported_parts(path: Path):
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith(f"{PACKAGE}."):
            yield node.module.split(".")[1:]


def violations():
    found = []
    for path, parts in feature_modules():
        feature, layer = parts[0], parts[1] if len(parts) > 1 else None
        for target in imported_parts(path):
            found.extend(check(path, feature, layer, target))
    return found


def check(path: Path, feature: str, layer, target: list[str]):
    name = f"{path.relative_to(SOURCE)} -> {'.'.join(target)}"
    if target[0] in OUTER_PACKAGES:
        return [f"camada externa: {name}"]
    if target[0] not in ALLOWED_FEATURES[feature]:
        return [f"funcionalidade não permitida: {name}"]
    if layer in ALLOWED_LAYERS and target[1] not in ALLOWED_LAYERS[layer]:
        return [f"camada não permitida: {name}"]
    return []


def test_dependency_rule():
    assert violations() == []


def test_domain_has_no_framework_imports():
    for path, parts in feature_modules():
        if len(parts) < 2 or parts[1] != "domain":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        modules = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
        assert not any(m.startswith("PySide6") for m in modules), path


@pytest.mark.parametrize("path", [p for p in sorted(SOURCE.rglob("*.py")) if p.name != "__init__.py"])
def test_one_class_per_file(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    assert len([n for n in tree.body if isinstance(n, ast.ClassDef)]) <= 1


def test_rule_detects_forbidden_dependency():
    assert check(Path(SOURCE / "device/domain/x.py"), "device", "domain", ["battery", "domain", "x"])
    assert check(Path(SOURCE / "battery/domain/x.py"), "battery", "domain", ["battery", "infrastructure", "x"])
    assert check(Path(SOURCE / "battery/application/x.py"), "battery", "application", ["presentation", "x"])
