"""Azure OpenAI model limits package."""

from .api import (
    all_models,
    context_limit,
    get_limits,
    list_models,
    list_versions,
    model_exists,
    output_limit,
)
from .types import Limits

__version__ = "0.1.0"
__all__ = [
    "Limits",
    "get_limits",
    "context_limit",
    "output_limit",
    "all_models",
    "list_models",
    "list_versions",
    "model_exists",
]


def _main() -> None:
    """Command-line interface for azure-openai-limits."""
    import argparse
    import json
    import sys

    p = argparse.ArgumentParser(
        prog="azure-openai-limits",
        description="Get context and output limits for Azure OpenAI models",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    show = sub.add_parser("show", help="Show limits for a specific model")
    show.add_argument("model", help="Model name (e.g., 'gpt-4o')")
    show.add_argument("--version", help="Model version (e.g., '2024-08-06')")

    sub.add_parser("list", help="List all available models and versions")

    args = p.parse_args()

    try:
        if args.cmd == "show":
            limits = get_limits(args.model, args.version)
            print(json.dumps(limits.__dict__, indent=2))
        elif args.cmd == "list":
            # pretty but compact
            data = {m: sorted(v.keys()) for m, v in all_models().items()}
            print(json.dumps(data, indent=2))
    except (KeyError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    _main()
