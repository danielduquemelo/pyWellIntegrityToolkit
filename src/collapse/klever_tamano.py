from typing import Optional
import numpy as np
from ..entities.klever_tamano_parameters import KleverTamanoParameters, DEFAULT_KT_PARAMS
from .base import CollapseMethod, CollapseResult
from ..entities.tubular import TubularData
from ..entities.steel_grade import SteelGrade
from ..entities.tubular_load_case import TubularLoadCase
from .effective_yield import effective_yield_strength


def original_parameter_c(slenderness_ratio: float) -> float:
    """Original Clinedinst factor c."""
    return -1.0 + 1.0 / slenderness_ratio  # Clinedinst factor

def calc_kt_imperfection_factor(
    tubular: TubularData,
    kt_params: KleverTamanoParameters = DEFAULT_KT_PARAMS
) -> float:
    """Calculate total imperfection factor Ht."""
    Ht = (
        0.127 * tubular.ovality / 100.0
        + 0.0039 * tubular.eccentricity / 100.0
        - 0.44 * kt_params.residual_stress
        + kt_params.Hn
    )
    return max(0.0, Ht)

def calc_kt_elastic_collapse(
    tubular: TubularData,
    material: SteelGrade,
    kt_params: KleverTamanoParameters = DEFAULT_KT_PARAMS) -> float:

    """Calculate elastic collapse pressure for klever tamano method."""
    slen = tubular.slenderness_ratio
    eta = 1.0 / (slen - 1)
    # c = -1.0 + 1.0 / slen  # Clinedinst factor

    E1 = kt_params.kels * (1 - kt_params.He) * material.young_modulus
    Pe = 2 * (E1 / (1 - material.poisson_ratio**2)) * (eta**3) * (1 + kt_params.c * eta)
    return Pe

def calc_kt_plastic_collapse(
    tubular: TubularData,
    material: SteelGrade,
    kt_params: KleverTamanoParameters = DEFAULT_KT_PARAMS,
    loading: Optional[TubularLoadCase] = None
) -> float:
    """Calculate plastic collapse pressure for klever tamano method."""
    slen = tubular.slenderness_ratio
    eta = 1.0 / (slen - 1)

    smys_eff = effective_yield_strength(material, loading)
    Sy1 = kt_params.kyls * (1 - kt_params.Hy) * smys_eff

    # Stress interaction factor (ISO 10400 Annex C)
    axial_stress = loading.axial_stress if loading else 0.0
    inner_pressure = loading.internal_pressure if loading else 0.0
    Si = (axial_stress + inner_pressure) / Sy1

    # Calculate plastic pressure
    part1 = eta * Sy1 * (4 * (1 + 2 * eta)) / (3 + (1 + 2 * eta)**2)
    Part2_1 = -Si + (1 + 3 * (1 - Si**2) / ((1 + 2 * eta)**2))**0.5
    Part2_2 = -Si - (1 + 3 * (1 - Si**2) / ((1 + 2 * eta)**2))**0.5

    deltaPy1 = part1 * Part2_1
    deltaPy2 = part1 * Part2_2
    deltaPy = max(deltaPy1, deltaPy2)
    average = 0.5 * (deltaPy + 2 * eta * Sy1)

    Py = min(deltaPy, average)
    return Py

def get_kt_regime_from_pressures(elastic_collapse: float, plastic_collapse: float) -> str:
    lambda_collapse = plastic_collapse / elastic_collapse
    if np.log(lambda_collapse) < -0.3:
        return "yield"
    elif np.log(lambda_collapse) > 0.3:
        return "elastic"
    else:
        return "transition"

def get_kt_regime(tubular: TubularData, material: SteelGrade,
                  kt_params: KleverTamanoParameters = DEFAULT_KT_PARAMS,
                  loading: Optional[TubularLoadCase] = None) -> str:
    """Determine which regime applies."""
    Pe = calc_kt_elastic_collapse(tubular, material, kt_params)
    Py = calc_kt_plastic_collapse(tubular, material, kt_params, loading)
    return get_kt_regime_from_pressures(Pe, Py)

class KleverTamanoMethod(CollapseMethod):
    """Klever-Tamano collapse calculation method."""

    @property
    def name(self) -> str:
        return "KLEVER_TAMANO"

    def get_regime(self, tubular: TubularData,
        material: SteelGrade,
        kt_params: KleverTamanoParameters = DEFAULT_KT_PARAMS,
        loading: Optional[TubularLoadCase] = None) -> str:
        return get_kt_regime(
            tubular,
            material,
            kt_params,
            loading)

    def calculate(
        self,
        tubular: TubularData,
        material: SteelGrade,
        kt_params: KleverTamanoParameters = DEFAULT_KT_PARAMS,
        loading: Optional[TubularLoadCase] = None
    ) -> CollapseResult:
        """Calculate Klever-Tamano collapse pressure."""
        Pe = calc_kt_elastic_collapse(tubular, material, kt_params)
        Py = calc_kt_plastic_collapse(tubular, material, kt_params, loading)
        Ht = calc_kt_imperfection_factor(tubular, kt_params)
        regime = get_kt_regime_from_pressures(Pe, Py)
        # Combined collapse pressure with imperfections
        Pc = 2 * (Py * Pe) / (Py + Pe + ((Py - Pe)**2 + 4 * Ht * Py * Pe)**0.5)

        return CollapseResult(
            pressure=max(Pc, 0.0),
            regime=regime,
            method=self.name,
            metadata={
                "slenderness": tubular.slenderness_ratio,
                "effective_yield": effective_yield_strength(material, loading),
                "parameters": {
                    "Pe": Pe,
                    "Py": Py,
                    "Ht": Ht,
                    "kels": kt_params.kels,
                    "kyls": kt_params.kyls,
                },
            }
        )

