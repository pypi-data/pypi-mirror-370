"""
prompt-forge: A modern toolkit for creating, managing, and testing LLM prompts as code.

This __init__.py file exposes the core components of the library, making them
easily accessible for users. For example, instead of having to import from
`prompt_forge.core`, users can simply import directly from `prompt_forge`.
"""

# Import the main function from the core module
from .core import load

# Import the data models.
from .models import Prompt, PromptRepository

# Import the exceptions.
from .exceptions import AydieException, InvalidPromptFileError, PromptNotFoundError

# Define the public API of the package.
__all__ = [
    "load",
    "Prompt",
    "PromptRepository",
    "AydieException",
    "InvalidPromptFileError",
    "PromptNotFouncError",
]

__version__ = "1.0.0"