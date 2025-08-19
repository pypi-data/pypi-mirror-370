import numpy as np
from scipy.optimize import curve_fit


def monoexp_model(b, ADC):
    """
    Monoexponential decay model for diffusion signal.

    Parameters:
        b (float or array): b-value(s)
        ADC (float): apparent diffusion coefficient

    Returns:
        normalized signal at b
    """
    return np.exp(-b * ADC)


def prepare_signal(b_values, signal, omit_b0=False, max_b=1000):
    """
    Prepare signal and b-values by applying filters.

    Parameters:
        b_values (array-like): input b-values
        signal (array-like): corresponding signal intensities
        omit_b0 (bool): if True, excludes b=0 values
        max_b (float): maximum b-value to include

    Returns:
        filtered_b (np.array), filtered_signal (np.array)
    """
    b = np.array(b_values)
    s = np.array(signal)

    # Build mask based on omit_b0 and max_b
    if omit_b0:
        mask = (b > 0) & (b <= max_b)
    else:
        mask = b <= max_b

    return b[mask], s[mask]


def fit_adc(b_values, signal, omit_b0=False):
    """
    Fit monoexponential ADC model to diffusion signal.

    Parameters:
        b_values (array-like): b-values (s/mm^2)
        signal (array-like): signal intensities
        omit_b0 (bool): whether to exclude b=0 from fitting

    Returns:
        adc (float): estimated apparent diffusion coefficient (mm^2/s)
    """
    b, s = prepare_signal(b_values, signal, omit_b0=omit_b0)

    if len(b) < 2:
        raise ValueError("Not enough b-values after filtering to fit ADC.")

    # Normalize to S0
    s = s / s[0]

    # Fit monoexponential model
    popt, _ = curve_fit(monoexp_model, b, s, bounds=(0, 0.03))

    return popt[0]
