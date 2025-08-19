import os
import json
from pathlib import Path
from typing import Any, Callable, Optional, TypeVar, Generic, List

from .name_utilities import dotted_to_env

T = TypeVar("T")

class _RequiredType:
    def __repr__(self) -> str:
        return "Required"

Required = _RequiredType()

def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}

def _parse_list(value: str, sep: str = ",") -> List[str]:
    return [item.strip() for item in value.split(sep) if item.strip()]


class EnvVar(Generic[T]):
    """
    Descriptor that calculates its env key from the owner class's __qualname__
    and the attribute name (or an override), reads it from the environment, and
    falls back to a default. Supports casting and caching.

    Usage:
        class Example:
            PORT = EnvVar(default=8080, cast=int, nest=1)
            DEBUG = EnvVar(default=False, cast=_parse_bool)
    """
    def __init__(
        self,
        default: Any = Required,
        *,
        name: Optional[str] = None,
        nest: int = 2,
        cast: Optional[Callable[[str], T]] = None,
        cache: bool = True,
    ) -> None:
        self.default = default
        self.nest = nest
        self.cast = cast
        self.cache = cache
        self._attr_name: Optional[str] = None
        self._explicit_name = name

    def __set_name__(self, owner, name: str) -> None:
        self._attr_name = name

    def _resolve_default(self, owner) -> Any:
        if callable(self.default):
            # Allow default(owner) for dependent defaults
            try:
                return self.default(owner)
            except TypeError:
                # Fallback to calling without owner if signature doesn't accept it
                return self.default()
        if self.default is Required:
            dotted = getattr(owner, "__qualname__", owner.__name__)
            env_key = dotted_to_env(dotted, self._explicit_name or self._attr_name or "UNKNOWN", self.nest)
            raise KeyError(f"Missing required env var: {env_key}")
        return self.default

    def __get__(self, instance, owner) -> T:
        if owner is None:
            owner = type(instance)

        attr_name = self._attr_name or "<unnamed>"
        var_name = self._explicit_name or attr_name
        dotted = getattr(owner, "__qualname__", owner.__name__)
        env_key = dotted_to_env(dotted, var_name, self.nest)

        if env_key in os.environ:
            raw = os.environ[env_key]
            value = self.cast(raw) if self.cast else raw
        else:
            value = self._resolve_default(owner)

        if self.cache:
            # cache by replacing the descriptor on the class with concrete value
            setattr(owner, attr_name, value)
        return value

    def __set__(self, instance, value) -> None:
        # Allow manual overrides on instances
        instance.__dict__[self._attr_name] = value

# Handy built-in casters you can import
parse_bool = _parse_bool
parse_list = _parse_list
parse_json = json.loads
parse_int = int
parse_float = float
parse_path = Path