import numpy as np
from ivimfit.bayesian import fit_bayesian

def test_bayesian_fit_runs():
    b = np.array([0, 50, 100, 200, 400, 600, 800])
    f_true, D_true, D_star_true = 0.1, 0.0011, 0.016
    s = f_true * np.exp(-b * D_star_true) + (1 - f_true) * np.exp(-b * D_true)
    f, D, D_star = fit_bayesian(b, s, omit_b0=True, draws=100, chains=1)
    assert 0 <= f <= 0.3
    assert 0.0005 <= D <= 0.003
    assert 0.005 <= D_star <= 0.05
