# src/collapse/api5c3.py
from os import pipe
from typing import Optional
import numpy as np
from .base import CollapseMethod, CollapseResult
from ..entities.tubular import TubularData
from ..entities.steel_grade import SteelGrade
from ..entities.tubular_load_case import TubularLoadCase
from .effective_yield import effective_yield_strength

class ClassicalMethod(CollapseMethod):
    """Classical mechanics collapse calculation from Timoshenko(standard formulation)."""

    @property
    def name(self) -> str:
        return "TIMOSHENKO"

    def _ellastic_collapse_pressure(self, tubular: TubularData, material: SteelGrade) -> float:
        """Calculate elastic collapse pressure."""
        slen = tubular.od_to_wt_ratio
        E_ = material.young_modulus / (1 - material.poisson_ratio**2)
        return 2*E_*slen**-3

    def _plastic_collapse_pressure(self, tubular: TubularData, material: SteelGrade, loading: Optional[TubularLoadCase] = None) -> float:
        """Calculate plastic collapse pressure."""
        slen = tubular.od_to_wt_ratio
        smys_eff = effective_yield_strength(material, loading)
        Py = 2 * smys_eff * slen**-1
        return Py

    def get_regime(self, tubular: TubularData, material: SteelGrade) -> str:
        """Determine which regime (elastic/plastic/transition) applies."""
        return "elastic-plastic"

    def calculate(
        self,
        tubular: TubularData,
        material: SteelGrade,
        loading: Optional[TubularLoadCase] = None
    ) -> CollapseResult:
        """Calculate Timoshenko collapse pressure."""
        slen = tubular.od_to_wt_ratio
        Pe = self._ellastic_collapse_pressure(tubular, material)
        Py = self._plastic_collapse_pressure(tubular, material, loading)
        smys_eff = effective_yield_strength(material, loading)

        delta_ov = tubular.ovality_percent / 100.0
        oval_factor = 1 + 3.0 * delta_ov * slen
        Pc = ((Py + Pe * oval_factor) - np.sqrt((Py + Pe * oval_factor)**2 - 4 * Py * Pe)) / 2.0
        inner_pressure = loading.internal_pressure if loading else 0.0
        Pc = Pc + inner_pressure

        return CollapseResult(
            pressure=max(Pc, 0.0),
            regime="Classical Mechanics",
            method=self.name,
            metadata={
                "slenderness": slen,
                "effective_yield_psi": smys_eff,
                "parameters": {
                    "Pe": Pe,
                    "Py": Py,
                    "oval_factor": oval_factor,
                    "inner_pressure": inner_pressure,
                },
            }
        )


class ClinedinstClassicalMethod(ClassicalMethod):
    """Modified Classical mechanics collapse calculation: Clinedinst (standard formulation)."""

    @property
    def name(self) -> str:
        return "CLINEDINST_CLASSICAL_ELASTIC"

    def _ellastic_collapse_pressure(self, tubular: TubularData, material: SteelGrade) -> float:
        """Calculate elastic collapse pressure."""
        slen = tubular.od_to_wt_ratio
        print(material)
        E_ = material.young_modulus_psi / (1 - material.poisson_ratio**2)
        return 2 * E_ * (slen**-1) * ((slen-1)**-2)
