"""Domain factory for deriving tubular load cases from engineering inputs."""

from __future__ import annotations

from dataclasses import dataclass

from .tubular_load_case import TubularLoadCase


@dataclass(frozen=True)
class DepthLoadInput:
    """Inputs required to derive loading from depth-based assumptions."""

    depth: float
    external_fluid: float = 0.0
    internal_fluid: float = 0.0
    axial_load: float = 0.0
    cross_section_area: float = 1.0
    temperature: float = 0.01
    surface_temp_f: float = 60.0


class TubularLoadCaseFactory:
    """Factory for creating ``TubularLoadCase`` instances from domain inputs."""

    @staticmethod
    def from_depth(inputs: DepthLoadInput) -> TubularLoadCase:
        """Create a load case using depth, fluid gradient and axial load assumptions."""
        external_pressure = 0.052 * inputs.external_fluid * inputs.depth
        internal_pressure = 0.052 * inputs.internal_fluid * inputs.depth

        if inputs.cross_section_area <= 0:
            axial_stress = 0.0
        else:
            axial_stress = inputs.axial_load / inputs.cross_section_area

        temperature = inputs.temperature

        return TubularLoadCase(
            external_pressure=external_pressure,
            internal_pressure=internal_pressure,
            axial_stress=axial_stress,
            temperature=temperature,
        )
