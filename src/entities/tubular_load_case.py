"""Loading conditions for OCTG tubular collapse analysis."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TubularLoadCase:
    """Loading conditions applied to a tubular.

    Attributes:
        external_pressure: External hydrostatic pressure in psi
        internal_pressure: Internal fluid pressure in psi
        axial_stress: Axial stress in psi (positive = tension, negative = compression)
        temperature: Operating temperature in celsius
        bending_moment: Applied bending moment in lbf*in
        torque: Applied torque in lbf*in
    """
    external_pressure: float = 0.0
    internal_pressure: float = 0.0
    axial_stress: float = 0.0
    temperature: float = 15.6  # 60°F in Celsius
    bending_moment: float = 0.0
    torque: float = 0.0

    def __post_init__(self):
        """Validate loading conditions."""
        if self.external_pressure < 0:
            raise ValueError("External pressure must be non-negative")
        if self.internal_pressure < 0:
            raise ValueError("Internal pressure must be non-negative")

    @property
    def net_pressure(self) -> float:
        """Net collapse pressure (external - internal)."""
        return self.external_pressure - self.internal_pressure

    @property
    def is_biaxial(self) -> bool:
        """Check if loading includes axial stress."""
        return abs(self.axial_stress) > 1e-6

    @property
    def is_triaxial(self) -> bool:
        """Check if loading includes bending or torque."""
        return abs(self.bending_moment) > 1e-6 or abs(self.torque) > 1e-6

    def copy(self, **changes) -> TubularLoadCase:
        """Create a copy with modified attributes."""
        data = {
            "external_pressure": self.external_pressure,
            "internal_pressure": self.internal_pressure,
            "axial_stress": self.axial_stress,
            "temperature": self.temperature,
            "bending_moment": self.bending_moment,
            "torque": self.torque,
        }
        data.update(changes)
        return TubularLoadCase(**data)



