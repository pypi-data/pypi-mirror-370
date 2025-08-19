"""
Commit-Gen - AI-Powered Git Commit Message Generator

A command-line tool that automatically generates conventional commit messages using AI.
Supports multiple AI providers including OpenRouter, Ollama, and custom providers.
"""

__version__ = "1.1.4"
__author__ = "Mobio Company"
__email__ = "contact@mobio.vn"

try:
    from pkg_resources import declare_namespace

    declare_namespace(__name__)
except ImportError:
    pass

from .cli import main
from .core import generate_commit_message, generate_changelog

__all__ = ["generate_commit_message", "generate_changelog", "main"]
