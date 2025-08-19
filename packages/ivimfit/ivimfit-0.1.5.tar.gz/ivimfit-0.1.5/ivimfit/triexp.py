import numpy as np
from scipy.optimize import curve_fit

def triexp_model(b, f1, f2, D, D1_star, D2_star):
    f3 = 1 - f1 - f2
    return f1 * np.exp(-b * D1_star) + f2 * np.exp(-b * D2_star) + f3 * np.exp(-b * D)


def fit_triexp_free(b, s, omit_b0=False, p0=None, bounds=None):
    b = np.asarray(b)
    s = np.asarray(s)
    s_norm = s / s[0]

    if omit_b0:
        mask = b > 0
        b = b[mask]
        s_norm = s_norm[mask]

    if p0 is None:
        p0 = [0.05, 0.05, 0.001, 0.05, 0.02]  # f1, f2, D, D1*, D2*
    if bounds is None:
        bounds = (
            [0.0, 0.0, 0.0001, 0.001, 0.001],     # lower
            [0.9, 0.9, 0.003, 0.2, 0.2]           # upper
        )

    popt, _ = curve_fit(triexp_model, b, s_norm, p0=p0, bounds=bounds, maxfev=10000)
    return popt  # f1, f2, D, D1*, D2*