"""
Configuration management for Commit-Gen.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any

# Configuration paths
CONFIG_DIR = Path.home() / ".config" / "git-commit-ai"
CONFIG_FILE = CONFIG_DIR / "config"
MODEL_FILE = CONFIG_DIR / "model"
BASE_URL_FILE = CONFIG_DIR / "base_url"
PROVIDER_FILE = CONFIG_DIR / "provider"
PROMPT_FILE = CONFIG_DIR / "prompt"

# Provider definitions
PROVIDERS = {
    "openrouter": {
        "name": "OpenRouter",
        "default_model": "moonshotai/kimi-k2:free",
        "base_url": "https://openrouter.ai/api/v1",
        "endpoint": "chat/completions",
        "requires_api_key": True,
        "description": "Cloud-based provider with access to multiple AI models"
    },
    "ollama": {
        "name": "Ollama",
        "default_model": "qwen2.5-coder:7b",
        "base_url": "http://localhost:11434/api",
        "endpoint": "generate",
        "requires_api_key": False,
        "description": "Local AI provider, requires Ollama installation"
    },
    "gemini": {
        "name": "Google Gemini",
        "default_model": "gemini-2.5-flash",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "endpoint": "models/{model}:generateContent",
        "requires_api_key": True,
        "description": "Google's powerful AI model with advanced capabilities"
    },
    "mistral": {
        "name": "Mistral AI",
        "default_model": "mistral-large-2411",
        "base_url": "https://api.mistral.ai/v1",
        "endpoint": "chat/completions",
        "requires_api_key": True,
        "description": "High-performance AI model with excellent reasoning"
    },
    "custom": {
        "name": "Custom Provider",
        "default_model": "",
        "base_url": "",
        "endpoint": "chat/completions",
        "requires_api_key": True,
        "description": "Custom AI provider with your own configuration"
    }
}

# Default provider
DEFAULT_PROVIDER = "openrouter"

# Default prompt template
DEFAULT_PROMPT = """Generate a commit message for these changes:

File changes:
{changes}

Diff:
{diff_content}

Format:
[Action] :: Detail action

Actions:
- [Fix] :: For bug fixes and error corrections
- [Feature] :: For new features and major additions
- [Update] :: For updates and improvements to existing features
- [Refactor] :: For code restructuring without behavior changes
- [Docs] :: For documentation changes
- [Test] :: For adding or modifying tests
- [Style] :: For code style/formatting changes
- [Build] :: For build system or dependency changes
- [CI] :: For CI/CD changes
- [Remove] :: For code or file removal

Guidelines:
- Bắt buộc action phải ở trong [], nếu không thì phải tạo lại.
- Bắt buộc message sẽ có khoảng từ 30 -> 70 ký tự tạo bằng tiếng anh.
- Use imperative mood ('add' not 'adds'/'added')
- Keep descriptions clear and concise
- Reference issues as '#123' at the end if applicable
- For breaking changes, add '!BREAKING!' prefix

Examples:
[Fix] :: Resolve null pointer in user validation
[Feature] :: Add email template customization
[Update] :: Improve database query performance
[Refactor] :: Restructure authentication module
[Remove] :: Delete deprecated API endpoints

Response should be only the commit message, without any additional text or explanations."""

SIMPLE_OLLAMA_PROMPT = """Generate a conventional commit message for these changes: {changes}. 
Format should be: <type>(<scope>): <subject>

<body>

Rules:
- Type: feat, fix, docs, style, refactor, perf, test, chore
- Subject: 50-70 chars, imperative mood, no period
- Body: explain what and why
- Use fix for minor changes
- Response should be the commit message only, no explanations."""


def get_provider_info(provider_name: str) -> Optional[Dict[str, Any]]:
    """Get provider information by name."""
    return PROVIDERS.get(provider_name)


def list_providers() -> Dict[str, Dict[str, Any]]:
    """Get all available providers."""
    return PROVIDERS


def ensure_config_dir() -> None:
    """Create configuration directory if it doesn't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    os.chmod(CONFIG_DIR, 0o700)


def save_api_key(api_key: str) -> None:
    """Save API key to configuration file."""
    ensure_config_dir()
    # Remove any quotes or extra arguments from the API key
    api_key = api_key.split()[0] if api_key else ""
    CONFIG_FILE.write_text(api_key)
    os.chmod(CONFIG_FILE, 0o600)


def get_api_key() -> str:
    """Get API key from configuration file."""
    if CONFIG_FILE.exists():
        return CONFIG_FILE.read_text().strip()
    return ""


def save_model(model: str) -> None:
    """Save model to configuration file."""
    ensure_config_dir()
    MODEL_FILE.write_text(model)
    os.chmod(MODEL_FILE, 0o600)


def get_model() -> str:
    """Get model from configuration file."""
    if MODEL_FILE.exists():
        return MODEL_FILE.read_text().strip()
    return ""


def save_base_url(base_url: str) -> None:
    """Save base URL to configuration file."""
    ensure_config_dir()
    BASE_URL_FILE.write_text(base_url)
    os.chmod(BASE_URL_FILE, 0o600)


def get_base_url() -> str:
    """Get base URL from configuration file."""
    if BASE_URL_FILE.exists():
        return BASE_URL_FILE.read_text().strip()
    return ""


def save_provider(provider: str) -> None:
    """Save provider to configuration file."""
    ensure_config_dir()
    PROVIDER_FILE.write_text(provider)
    os.chmod(PROVIDER_FILE, 0o600)


def get_provider() -> str:
    """Get provider from configuration file."""
    if PROVIDER_FILE.exists():
        return PROVIDER_FILE.read_text().strip()
    return DEFAULT_PROVIDER


def save_prompt(prompt: str) -> None:
    """Save custom prompt to configuration file."""
    ensure_config_dir()
    PROMPT_FILE.write_text(prompt)
    os.chmod(PROMPT_FILE, 0o600)


def get_prompt() -> str:
    """Get custom prompt from configuration file."""
    if PROMPT_FILE.exists():
        return PROMPT_FILE.read_text().strip()
    return ""


def get_current_config() -> Dict[str, Any]:
    """Get current configuration as a dictionary."""
    provider = get_provider()
    provider_info = get_provider_info(provider)

    return {
        "provider": provider,
        "provider_name": provider_info["name"] if provider_info else "Unknown",
        "model": get_model() or (provider_info["default_model"] if provider_info else ""),
        "base_url": get_base_url() or (provider_info["base_url"] if provider_info else ""),
        "api_key_set": bool(get_api_key()),
        "custom_prompt_set": bool(get_prompt())
    }


def validate_provider(provider: str) -> bool:
    """Validate if provider exists."""
    return provider in PROVIDERS


def get_default_model_for_provider(provider: str) -> str:
    """Get default model for a provider."""
    provider_info = get_provider_info(provider)
    return provider_info["default_model"] if provider_info else ""


def get_default_base_url_for_provider(provider: str) -> str:
    """Get default base URL for a provider."""
    provider_info = get_provider_info(provider)
    return provider_info["base_url"] if provider_info else ""


def provider_requires_api_key(provider: str) -> bool:
    """Check if provider requires API key."""
    provider_info = get_provider_info(provider)
    return provider_info["requires_api_key"] if provider_info else True
