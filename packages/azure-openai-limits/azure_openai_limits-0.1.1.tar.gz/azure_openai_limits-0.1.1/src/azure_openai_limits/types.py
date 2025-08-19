"""Type definitions for Azure OpenAI limits."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Limits:
    """
    Token limits for an Azure OpenAI model.

    Attributes:
        context: Maximum number of context tokens (input + conversation history)
        output: Maximum number of output tokens that can be generated
    """

    context: int
    output: int

    def __post_init__(self) -> None:
        """Validate that limits are positive integers."""
        if not isinstance(self.context, int) or self.context <= 0:
            raise ValueError("context must be a positive integer")
        if not isinstance(self.output, int) or self.output <= 0:
            raise ValueError("output must be a positive integer")

    @property
    def total_max(self) -> int:
        """Maximum total tokens (context + output)."""
        return self.context + self.output
