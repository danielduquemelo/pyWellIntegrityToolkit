# src/collapse/registry.py
from typing import Dict, Type
from .base import CollapseMethod


class CollapseMethodRegistry:
    """Registry for collapse calculation methods."""

    _methods: Dict[str, Type[CollapseMethod]] = {}

    @classmethod
    def register(cls, method_class: Type[CollapseMethod]) -> None:
        """Register a collapse method."""
        instance = method_class()
        cls._methods[instance.name] = method_class

    @classmethod
    def get(cls, name: str) -> CollapseMethod:
        """Get method instance by name."""
        if name not in cls._methods:
            raise ValueError(f"Unknown collapse method: {name}")
        return cls._methods[name]()

    @classmethod
    def available_methods(cls) -> list[str]:
        """List all registered methods."""
        return list(cls._methods.keys())


# Auto-register methods
from .api5c3_design import API5C3Method
from .klever_tamano import KleverTamanoMethod

CollapseMethodRegistry.register(API5C3Method)
CollapseMethodRegistry.register(KleverTamanoMethod)