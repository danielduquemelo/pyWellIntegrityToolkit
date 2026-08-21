# src/collapse/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from ..entities.tubular import TubularData
from ..entities.steel_grade import SteelGrade
from ..entities.tubular_load_case import TubularLoadCase


@dataclass
class CollapseResult:
    """Result from collapse calculation."""
    pressure: float
    regime: str
    method: str
    metadata: dict


class CollapseMethod(ABC):
    """Base class for all collapse calculation methods."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this method."""
        pass

    @abstractmethod
    def calculate(
        self,
        tubular: TubularData,
        material: SteelGrade,
        loading: Optional[TubularLoadCase] = None
    ) -> CollapseResult:
        """Calculate collapse pressure."""
        pass

    @abstractmethod
    def get_regime(self, tubular: TubularData, material: SteelGrade) -> str:
        """Determine which regime (elastic/plastic/transition) applies."""
        pass