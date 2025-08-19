import numpy as np
from ivimfit.utils import calculate_r_squared

def test_r_squared_correctness():
    y_true = np.array([1, 0.8, 0.6, 0.5])
    y_pred = np.array([1, 0.75, 0.65, 0.45])
    r2 = calculate_r_squared(y_true, y_pred)
    assert 0.9 <= r2 <= 1.0
