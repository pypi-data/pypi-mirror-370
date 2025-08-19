import numpy as np
from scipy.optimize import curve_fit


def biexp_model(b, f, D, D_star):
    """
    Biexponential IVIM model:
    S(b)/S0 = f * exp(-b * D*) + (1 - f) * exp(-b * D)

    Parameters:
        b (float or array): b-values
        f (float): perfusion fraction [0–1]
        D (float): true diffusion coefficient (mm^2/s)
        D_star (float): pseudo-diffusion coefficient (mm^2/s)

    Returns:
        modeled signal (normalized)
    """
    return f * np.exp(-b * D_star) + (1 - f) * np.exp(-b * D)


def prepare_signal(b_values, signal, omit_b0=False, max_b=1000):
    """
    Filter signal and b-values by max_b and omit_b0 flags.
    """
    b = np.array(b_values)
    s = np.array(signal)

    if omit_b0:
        mask = (b > 0) & (b <= max_b)
    else:
        mask = b <= max_b

    return b[mask], s[mask]


def fit_biexp_free(b_values, signal, omit_b0=False, p0=None, bounds=None):
    """
    Fit biexponential IVIM model (free fit) to diffusion signal.

    Parameters:
        b_values (array-like): b-values (s/mm^2)
        signal (array-like): signal intensities
        omit_b0 (bool): exclude b=0 from fitting if True
        p0 (list or tuple): optional initial guess [f, D, D*]
        bounds (2-tuple): optional lower and upper bounds ([min], [max])

    Returns:
        tuple: (f, D, D*) fitted values
    """
    b, s = prepare_signal(b_values, signal, omit_b0=omit_b0)

    if len(b) < 3:
        raise ValueError("Not enough b-values after filtering to fit biexponential model.")

    s = s / s[0]  # Normalize to S0

    # Default initial guess and bounds
    if p0 is None:
        p0 = [0.1, 0.001, 0.01]

    if bounds is None:
        bounds = ([0, 0.0005, 0.005], [0.7, 0.03, 0.5])

    try:
        popt, _ = curve_fit(biexp_model, b, s, p0=p0, bounds=bounds)
        return popt  # [f, D, D*]
    except RuntimeError:
        return [np.nan, np.nan, np.nan]

