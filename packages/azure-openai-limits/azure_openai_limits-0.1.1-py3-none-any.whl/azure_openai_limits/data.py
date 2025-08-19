from __future__ import annotations

import importlib.resources as pkgres
import json
from typing import Any

from .types import Limits


def _load() -> dict[str, dict[str, Limits]]:
    """
    Load model limits data from the models.json file.

    Returns:
        Dictionary mapping model names to version dictionaries,
        which map version strings to Limits objects

    Raises:
        FileNotFoundError: If models.json is not found
        json.JSONDecodeError: If models.json contains invalid JSON
        TypeError: If the JSON structure is invalid
    """
    try:
        with (
            pkgres.files(__package__)
            .joinpath("models.json")
            .open("r", encoding="utf-8") as f
        ):
            raw: dict[str, dict[str, dict[str, Any]]] = json.load(f)
    except FileNotFoundError as e:
        raise FileNotFoundError("models.json not found in package") from e
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in models.json: {e}", e.doc, e.pos
        ) from e

    try:
        return {
            model: {ver: Limits(**vals) for ver, vals in versions.items()}
            for model, versions in raw.items()
        }
    except (TypeError, ValueError) as e:
        raise TypeError(f"Invalid data structure in models.json: {e}") from e


# Load data once at module import time
_DATA = _load()
