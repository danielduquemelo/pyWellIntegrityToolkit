
def _lame_common(pipe, normalizedRadius, innerPressure, externalPressure):
    """Compute shared Lamé coefficients for a thick-walled cylinder."""
    re = 0.5 * pipe["OD"]
    ri = re - pipe["thickness"]
    r = ri + normalizedRadius * pipe["thickness"]
    aux1 = (innerPressure * ri**2 - externalPressure * re**2) / (re**2 - ri**2)
    aux2 = (innerPressure - externalPressure) * (re * ri)**2 / ((re**2 - ri**2) * r**2)
    return aux1, aux2


def LameStressesPlaneStrain(pipe, grade, normalizedRadius, axialStress=0.0, innerPressure=0.0, externalPressure=0.0):
    """
    Lamé stresses for a thick-walled cylinder under plane strain (?z = 0).

    Pressure loading contributes to the axial stress via Poisson's ratio:
        sigma_z = sigma_z_applied + nu(sigma_r + sigma_?) = sigma_z_applied + 2*nu·aux1
    """
    aux1, aux2 = _lame_common(pipe, normalizedRadius, innerPressure, externalPressure)
    return {
        "radial": aux1 - aux2,
        "hoop":   aux1 + aux2,
        "axial":  axialStress + 2 * grade["poisson"] * aux1,
    }


def LameStressesPlaneStress(pipe, normalizedRadius, axialStress=0.0, innerPressure=0.0, externalPressure=0.0):
    """
    Lamé stresses for a thick-walled cylinder under plane stress (sigma_z = 0 from pressure).

    The cylinder is free to deform axially, so pressure loading does not generate
    axial stress. Only the externally applied axial stress contributes:
        sigma_z = sigma_z_applied
    """
    aux1, aux2 = _lame_common(pipe, normalizedRadius, innerPressure, externalPressure)
    return {
        "radial": aux1 - aux2,
        "hoop":   aux1 + aux2,
        "axial":  axialStress,
    }

