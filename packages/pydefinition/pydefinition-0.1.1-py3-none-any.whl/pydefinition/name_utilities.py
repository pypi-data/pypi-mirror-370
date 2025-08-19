import re
from typing import Iterable

_CAMEL_RE = re.compile(r"(?!^)([a-z])([A-Z]+)")

def camel_to_snake(name: str) -> str:
    """Convert CamelCase or mixedCase to SNAKE_CASE (upper)."""
    return _CAMEL_RE.sub(r"\1_\2", name).upper()

def dotted_to_env(dotted_class_path: str, var_name: str, nest: int = 2) -> str:
    """
    Turn something like 'Config.General' + 'LOGS_DIR'
    into an ENV key like 'GENERAL_LOGS_DIR' (nest=2).
    Mirrors your current name_nest behavior.
    """
    parts = [camel_to_snake(p) for p in dotted_class_path.split(".")]
    var = camel_to_snake(var_name)
    if len(parts) > nest:
        scope = parts[-nest:]
    else:
        # Drop the first top-level (mirrors your logic)
        scope = parts[1:]
    return "_".join([*scope, var])

def join_env(parts: Iterable[str]) -> str:
    """Join arbitrary name parts into a single SNAKE_CASE env key."""
    return "_".join(camel_to_snake(p) for p in parts)
