import numpy as np
from ivimfit.segmented import fit_biexp_segmented

def test_fit_segmented_returns_values():
    b = np.array([0, 50, 100, 200, 400, 600, 800])
    f_true, D_true, D_star_true = 0.12, 0.0013, 0.018
    s = f_true * np.exp(-b * D_star_true) + (1 - f_true) * np.exp(-b * D_true)
    f, D, D_star = fit_biexp_segmented(b, s, omit_b0=False)
    assert 0 <= f <= 0.3
    assert 0.0005 <= D <= 0.003
    assert 0.005 <= D_star <= 0.05
