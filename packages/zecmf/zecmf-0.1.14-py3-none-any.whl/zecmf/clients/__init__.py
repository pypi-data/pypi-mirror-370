"""Client subpackage for external service integrations (e.g., LLM, payment, etc).

This package provides client modules for interacting with external APIs and services.
"""

from . import answering_machine, codebot, llm

__all__ = [
    "answering_machine",
    "codebot",
    "llm",
]
