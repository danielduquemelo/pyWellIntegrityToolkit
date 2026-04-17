
from typing import Optional
from src.entities.tubular_load_case import TubularLoadCase
from src.entities.steel_grade import SteelGrade
import numpy as np

def effective_yield_strength(
    material: SteelGrade,
    loading: Optional[TubularLoadCase]
    ) -> float:

    """Calculate effective yield ratio with respect to an axial stress load."""
    if not loading or loading.axial_stress == 0:
        return material.yield_strength

    ratio = loading.axial_stress / material.yield_strength
    factor = np.sqrt(1 - 0.75 * ratio**2) - 0.5 * ratio
    return factor * material.yield_strength