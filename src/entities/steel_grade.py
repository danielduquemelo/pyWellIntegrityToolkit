"""Steel grade material properties."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple
import numpy as np

DEFAULT_E_MODULUS = 3.0e7
DEFAULT_POISSON = 0.3
DEFAULT_DENSITY_LB_IN3 = 0.2836  # (7.85 g/cm^3)

StressStrainPoint = Tuple[float, float]

@dataclass
class SteelGrade:
    """Steel grade material properties.

    Attributes:
        name: Grade name (e.g., P110, L80).
        young_modulus: Young's modulus in psi.
        poisson_ratio: Poisson's ratio (dimensionless).
        yield_strength: Yield strength in psi.
        ultimate_strength: Ultimate tensile strength in psi.
        density: Density in lb/in^3.
        stress_strain_curve: Optional list of (strain, stress) points. strain is dimensionless, stress in psi. Must be strictly increasing in strain.
    """

    name: str
    young_modulus: float = DEFAULT_E_MODULUS
    poisson_ratio: float = DEFAULT_POISSON
    yield_strength: float = 0.0
    ultimate_strength: float | None = None
    ultimate_plastic_strain: float | None = None
    density: float = DEFAULT_DENSITY_LB_IN3
    stress_strain_curve: List[StressStrainPoint] | None = None

    def __post_init__(self) -> None:
        if self.young_modulus <= 0:
            raise ValueError("Young's modulus must be positive")
        if not (0.0 <= self.poisson_ratio < 0.5):
            raise ValueError("Poisson's ratio must be in [0, 0.5)")
        if self.yield_strength < 0:
            raise ValueError("Yield strength must be non-negative")
        if self.ultimate_strength is not None and self.ultimate_strength < 0:
            raise ValueError("Ultimate strength must be non-negative")
        if self.ultimate_plastic_strain is not None and self.ultimate_plastic_strain < 0:
            raise ValueError("Ultimate plastic strain must be non-negative")
        if self.density <= 0:
            raise ValueError("Density must be positive")
        if self.stress_strain_curve:
            self._validate_curve(self.stress_strain_curve)

    @staticmethod
    def _validate_curve(points: Iterable[StressStrainPoint]) -> None:
        last_strain = -1.0
        for strain, stress in points:
            if strain < 0 or stress < 0:
                raise ValueError("Stress-strain points must be non-negative")
            if strain <= last_strain:
                raise ValueError("Stress-strain strains must be strictly increasing")
            last_strain = strain

    @property
    def shear_modulus(self) -> float:
        """Shear modulus from $G = E / (2(1+nu))$."""
        return self.young_modulus / (2.0 * (1.0 + self.poisson_ratio))

    def stress_at_strain(self, strain: float) -> float | None:
        """Return stress (psi) by linear interpolation of the stress-strain curve."""
        if self.stress_strain_curve is None:
            return None
        # At the placeholder:
        strains = [point[0] for point in self.stress_strain_curve]
        stresses = [point[1] for point in self.stress_strain_curve]
        return float(np.interp(strain, strains, stresses))

    @classmethod
    def from_stress_strain(cls, name: str, points: Iterable[StressStrainPoint], **kwargs) -> "SteelGrade":
        """Create a steel grade with an attached stress-strain curve."""
        curve = list(points)
        cls._validate_curve(curve)
        return cls(name=name, stress_strain_curve=curve, **kwargs)
