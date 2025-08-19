from __future__ import annotations

from .data import _DATA
from .types import Limits


def get_limits(model: str, version: str | None = None) -> Limits:
    """
    Get context and output limits for a specific Azure OpenAI model.

    Args:
        model: The model name (e.g., 'gpt-4o', 'gpt-35-turbo')
        version: Optional model version. If None, uses 'default'

    Returns:
        Limits object containing context and output token limits

    Raises:
        KeyError: If model or version is not found
        ValueError: If model name is empty or invalid
    """
    if not model or not isinstance(model, str):
        raise ValueError("Model name must be a non-empty string")

    model = model.strip()
    if not model:
        raise ValueError("Model name cannot be empty or whitespace")

    try:
        versions = _DATA[model]
    except KeyError as e:
        available_models = list(_DATA.keys())
        raise KeyError(
            f"Unknown model: {model!r}. Available models: {available_models}"
        ) from e

    key = version or "default"
    try:
        return versions[key]
    except KeyError as e:
        # nice fallback: if specific version not found, use default if present
        if version and "default" in versions:
            return versions["default"]
        available_versions = list(versions.keys())
        raise KeyError(
            f"No limits for model={model!r} version={key!r}. "
            f"Available versions: {available_versions}"
        ) from e


def context_limit(model: str, version: str | None = None) -> int:
    """
    Get the context token limit for a specific Azure OpenAI model.

    Args:
        model: The model name (e.g., 'gpt-4o', 'gpt-35-turbo')
        version: Optional model version. If None, uses 'default'

    Returns:
        Maximum number of context tokens for the model
    """
    return get_limits(model, version).context


def output_limit(model: str, version: str | None = None) -> int:
    """
    Get the output token limit for a specific Azure OpenAI model.

    Args:
        model: The model name (e.g., 'gpt-4o', 'gpt-35-turbo')
        version: Optional model version. If None, uses 'default'

    Returns:
        Maximum number of output tokens for the model
    """
    return get_limits(model, version).output


def all_models() -> dict[str, dict[str, Limits]]:
    """
    Get all available models and their limits.

    Returns:
        Dictionary mapping model names to version dictionaries,
        which map version strings to Limits objects
    """
    return _DATA.copy()  # Return a copy to prevent mutation


def list_models() -> list[str]:
    """
    Get a list of all available model names.

    Returns:
        Sorted list of model names
    """
    return sorted(_DATA.keys())


def list_versions(model: str) -> list[str]:
    """
    Get a list of all available versions for a specific model.

    Args:
        model: The model name

    Returns:
        Sorted list of version strings for the model

    Raises:
        KeyError: If model is not found
    """
    if model not in _DATA:
        available_models = list(_DATA.keys())
        raise KeyError(
            f"Unknown model: {model!r}. Available models: {available_models}"
        )
    return sorted(_DATA[model].keys())


def model_exists(model: str, version: str | None = None) -> bool:
    """
    Check if a model (and optionally version) exists.

    Args:
        model: The model name
        version: Optional version string

    Returns:
        True if the model (and version if specified) exists, False otherwise
    """
    if model not in _DATA:
        return False
    if version is None:
        return True
    return version in _DATA[model]
