from dataclasses import dataclass
from numpy import pi
from .steel_grade import SteelGrade

@dataclass
class TubularData:
    """OCTG tubular
    od: outer diameter in inches,
    wt: wall thickness in inches,
    ovality: ovality in percent,
    eccentricity: eccentricity in percent
    grade: steel grade object
    ."""

    od: float
    wt: float
    grade: SteelGrade
    ovality: float = 0.0
    eccentricity: float = 0.0


    @property
    def id(self) -> float:
        return max(self.od - 2 * self.wt, 0.0)

    @property
    def slenderness_ratio(self) -> float:
        """D/t slenderness ratio (alias for od_to_wt_ratio)."""
        return self.od / self.wt

    @property
    def od_to_wt_ratio(self) -> float:
        """D/t ratio."""
        return self.od / self.wt

    @property
    def wt_to_od_ratio(self) -> float:
        """t/D ratio."""
        return self.wt / self.od

    @property
    def area(self) -> float:
        """Cross-sectional area of the tubular."""
        return pi * self.od * self.wt