from dataclasses import dataclass
from typing import Optional

@dataclass
class KleverTamanoParameters:

    """Calibrated Klever tamano parameters for OCTG tubular.
    kels: Elastic modulus reduction factor (default 1.089)
    kyls: Yield strength reduction factor (default 0.991)
    Hn: Elastic reduction exponent (default 0.017 fo kneed shapes, 0.0 otherwise)
    He: Elastic reduction coefficient (default 0.0)
    Hy: Yield reduction exponent (default 0.0)
    c: Wall thickness Clinedinst factor (default None -> ISO/TR 10400, c = -1 + t/D)
    residual_stress: Residual stress in psi (default 0.0), compressive stress is negative, tensile stress is positive
    ."""

    kels: float = 1.089
    kyls: float = 0.991
    Hn: float = 0.017
    He: float = 0.0
    Hy: float = 0.0
    c: Optional[float] = None   # None -> ISO/TR 10400 form, c = -1 + t/D
    residual_stress: float = 0.0

DEFAULT_KT_PARAMS = KleverTamanoParameters()