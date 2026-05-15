from pathlib import Path
from typing import Any

import yaml


BASE_DIR = Path(__file__).resolve().parents[1]


def load_yaml(relative_path: str) -> dict[str, Any]:
    path = BASE_DIR / relative_path
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_schema() -> dict[str, Any]:
    return load_yaml("catalogs/schema.yaml")


def load_udfs() -> dict[str, Any]:
    return load_yaml("catalogs/udfs.yaml")
