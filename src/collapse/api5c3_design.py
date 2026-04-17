# src/collapse/api5c3.py
from typing import Optional
import numpy as np
from .base import CollapseMethod, CollapseResult
from ..entities.tubular import TubularData
from ..entities.steel_grade import SteelGrade
from ..entities.tubular_load_case import TubularLoadCase


class API5C3DesignMethod(CollapseMethod):
    """API 5C3 collapse calculation (standard formulation)."""

    @property
    def name(self) -> str:
        return "API_5C3"

    def calculate(
        self,
        tubular: TubularData,
        material: SteelGrade,
        loading: Optional[TubularLoadCase] = None
    ) -> CollapseResult:
        """Calculate API 5C3 collapse pressure."""
        # Calculate effective yield if axial stress present
        smys_eff = self._effective_yield(material, loading)

        # Get regime parameters
        params = self._calculate_parameters(smys_eff)
        regime_limits = self._regime_limits(params, smys_eff)

        # Determine regime
        slen = tubular.slenderness_ratio
        regime = self._determine_regime(slen, regime_limits)

        # Calculate collapse for regime
        pc = self._collapse_for_regime(regime, slen, smys_eff, params)

        # Apply internal pressure correction
        if loading and loading.internal_pressure > 0:
            pc -= (1 - 2/slen) * loading.internal_pressure

        return CollapseResult(
            pressure=max(pc, 0.0),
            regime=regime,
            method=self.name,
            metadata={
                "slenderness": slen,
                "effective_yield_psi": smys_eff,
                "parameters": params,
            }
        )

    def get_regime(
        self,
        tubular: TubularData,
        material: SteelGrade,
        loading: Optional[TubularLoadCase] = None,
    ) -> str:
        """Determine collapse regime with optional axial stress effects."""
        smys_eff = self._effective_yield(material, loading)
        params = self._calculate_parameters(smys_eff)
        limits = self._regime_limits(params, smys_eff)
        return self._determine_regime(tubular.slenderness_ratio, limits)

    def _effective_yield(
        self,
        material: SteelGrade,
        loading: Optional[TubularLoadCase]
    ) -> float:
        """Calculate effective yield with axial stress."""
        if not loading or loading.axial_stress == 0:
            return material.yield_strength

        ratio = loading.axial_stress / material.yield_strength
        factor = np.sqrt(1 - 0.75 * ratio**2) - 0.5 * ratio
        return factor * material.yield_strength

    def _calculate_parameters(self, smys: float) -> dict:
        """Calculate A, B, C, F, G parameters."""
        A = (2.8762 + 0.10679e-5*smys + 0.2131e-10*smys**2
             - 0.53132e-16*smys**3)
        B = 0.026233 + 0.50609e-6*smys
        C = (-465.93 + 0.030867*smys - 0.10483e-7*smys**2
             + 0.36989e-13*smys**3)

        ratio = (3*B/A) / (2 + B/A)
        F = (46.95e6 * ratio**3) / (smys * (ratio - B/A) * (1 - ratio)**2)
        G = F * B / A

        return {"A": A, "B": B, "C": C, "F": F, "G": G}

    def _regime_limits(self, params: dict, effective_yield: float) -> dict:
        """Calculate slenderness regime boundaries."""
        A, B, C, F, G = params["A"], params["B"], params["C"], params["F"], params["G"]

        yp_limit = ((np.sqrt((A-2)**2 + 8*(B + C/effective_yield)) + (A-2))
                    / (2*(B + C/effective_yield)))
        pt_limit = (effective_yield*(A - F)) / (C + effective_yield*(B - G))
        te_limit = (2 + B/A) / (3*B/A)

        return {
            "yield": (0.0, yp_limit),
            "plastic": (yp_limit, pt_limit),
            "transition": (pt_limit, te_limit),
            "elastic": (te_limit, 50.0),
        }

    def _determine_regime(self, slen: float, limits: dict) -> str:
        """Find which regime the slenderness falls into."""
        for regime, (lower, upper) in limits.items():
            if lower < slen <= upper:
                return regime
        return "elastic"

    def _collapse_for_regime(
        self,
        regime: str,
        slen: float,
        smys: float,
        params: dict
    ) -> float:
        """Calculate collapse pressure for specific regime."""
        if regime == "yield":
            return 2 * smys * ((slen - 1) / slen**2)
        elif regime == "plastic":
            return smys * (params["A"]/slen - params["B"]) - params["C"]
        elif regime == "transition":
            return smys * (params["F"]/slen - params["G"])
        else:  # elastic
            return 46.95e6 / (slen * (slen - 1)**2)