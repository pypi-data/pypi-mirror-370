import numpy as np
from ivimfit.adc import fit_adc

def test_fit_adc_runs_and_returns_value():
    b = np.array([0, 200, 400, 600, 800])
    s = np.exp(-b * 0.0015)
    adc = fit_adc(b, s, omit_b0=False)
    assert 0.0005 < adc < 0.0025
