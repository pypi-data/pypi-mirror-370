import os
import re
from functools import partial
from re import Pattern
from typing import Any, Final


def env(name: str, module: str, *, default: str | None) -> str | None:
    return os.getenv(f"YAPT__{module.upper()}__{name}", default)


spark_env: partial[str | None] = partial(env, module="SPARK")
tool_env: partial[str] = partial(os.getenv, "YAPT_ENV", default="test")

# NOTE: Compiled regex for environment variable substitution is more performant.
#   Syntax: ${{ ENV_VAR:default_value }} (default_value is optional)
ENV_VAR_MATCHER: Final[Pattern[str]] = re.compile(
    r"\$\{\{\s*(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)\s*(?::\s*(?P<default>.*?))?\s*}}"
)


def substitute_env_vars(value: Any) -> Any:
    """Recursively traverses the data structure and substitutes environment
    variables.

    Args:
        value: The current value from the YAML data (can be dict, list, str, etc.).

    Returns:
        The value with environment variables substituted.

    Raises:
        KeyError: If an environment variable is not set and has no default.
    """
    if isinstance(value, dict):
        return {k: substitute_env_vars(v) for k, v in value.items()}
    if isinstance(value, list):
        return [substitute_env_vars(item) for item in value]
    if isinstance(value, str):
        return replace_string_env_var(value)
    return value


def replace_string_env_var(value: str) -> str:
    """Performs the actual environment variable substitution in a string.

    Args:
        value: The string value to process.

    Returns:
        The string with the placeholder replaced by the environment variable's value.
    """
    match = ENV_VAR_MATCHER.match(value)
    if not match:
        return value

    var_name = match.group("name")
    default_value = match.group("default")

    # Use os.getenv for thread-safe access to environment variables
    env_value = os.getenv(var_name)
    if env_value is not None:
        return env_value
    if default_value is not None:
        return default_value

    raise KeyError(
        f"Configuration error: Environment variable '{var_name}' is not set "
        "and no default value was provided."
    )
