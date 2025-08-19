# Azure OpenAI Limits

A Python package that provides static token limits for Azure OpenAI models, including context and output limits for various model versions.

## Installation

```bash
pip install azure-openai-limits
```

## Usage

### Python API

```python
from azure_openai_limits import get_limits, context_limit, output_limit

# Get limits for a model (uses default version)
limits = get_limits("gpt-4o")
print(f"Context: {limits.context}, Output: {limits.output}")

# Get limits for a specific version
limits = get_limits("gpt-4o", "2024-05-13")
print(f"Context: {limits.context}, Output: {limits.output}")

# Try the new O3 Pro model
limits = get_limits("o3-pro")
print(f"O3 Pro - Context: {limits.context}, Output: {limits.output}")

# Check Codex Mini limits
limits = get_limits("codex-mini")
print(f"Codex Mini - Context: {limits.context}, Output: {limits.output}")

# Get just context or output limits
context = context_limit("gpt-4o")
output = output_limit("gpt-4o")

# Check if a model/version exists
from azure_openai_limits import model_exists
if model_exists("gpt-4o", "2024-08-06"):
    print("Model version exists!")

# List all available models
from azure_openai_limits import list_models
models = list_models()
print("Available models:", models)

# List all versions for a model
from azure_openai_limits import list_versions
versions = list_versions("gpt-4o")
print("Available versions:", versions)
```

### Command Line Interface

```bash
# List all available models and their versions
azure-openai-limits list

# Show limits for a specific model (default version)
azure-openai-limits show gpt-4o

# Show limits for a specific model version
azure-openai-limits show gpt-4o --version 2024-05-13

# Check out the new O3 Pro model
azure-openai-limits show o3-pro
```

## Supported Models

The package includes limits for the following Azure OpenAI models:

- **Codex**: codex-mini
- **GPT-3.5**: gpt-35-turbo, gpt-35-turbo-instruct
- **GPT-4**: gpt-4, gpt-4-32k
- **GPT-4 Turbo**: gpt-4.1, gpt-4.1-mini, gpt-4.1-nano
- **GPT-4.5**: gpt-4.5-preview
- **GPT-4o**: gpt-4o, gpt-4o-mini
- **GPT-4o Audio**: gpt-4o-audio-preview, gpt-4o-mini-audio-preview
- **GPT-4o Realtime**: gpt-4o-realtime-preview, gpt-4o-mini-realtime-preview
- **GPT-5**: gpt-5, gpt-5-mini, gpt-5-nano, gpt-5-chat
- **GPT OSS**: gpt-oss-20b, gpt-oss-120b
- **O1 Models**: o1, o1-mini, o1-preview
- **O3 Models**: o3, o3-mini, o3-pro
- **O4 Models**: o4-mini
- **Model Router**: model-router

Each model may have multiple versions with different limits. Use `azure-openai-limits list` to see all available models and their versions.

## Data Source

The model limits data in this package is sourced from the official Microsoft documentation:
[Azure AI Foundry OpenAI Models](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/models)

**Last Updated:** August 19, 2025

## API Reference

### Classes

#### `Limits`

A dataclass representing token limits for a model.

**Attributes:**

- `context: int` - Maximum context tokens (input + conversation history)
- `output: int` - Maximum output tokens that can be generated
- `total_max: int` - Property returning context + output

### Functions

#### `get_limits(model: str, version: str | None = None) -> Limits`

Get context and output limits for a specific model.

#### `context_limit(model: str, version: str | None = None) -> int`

Get just the context limit for a model.

#### `output_limit(model: str, version: str | None = None) -> int`

Get just the output limit for a model.

#### `model_exists(model: str, version: str | None = None) -> bool`

Check if a model (and optionally version) exists.

#### `list_models() -> list[str]`

Get a sorted list of all available model names.

#### `list_versions(model: str) -> list[str]`

Get a sorted list of all versions for a specific model.

#### `all_models() -> dict[str, dict[str, Limits]]`

Get the complete model data structure.

## Error Handling

The package raises appropriate exceptions:

- `KeyError`: When a model or version is not found
- `ValueError`: When invalid input is provided (e.g., empty model name)

All error messages include helpful information about available models/versions.

## Development

To set up for development:

```bash
git clone <repository-url>
cd azure-openai-limits
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Run linting:

```bash
ruff check src/
mypy src/
```

## License

MIT License
