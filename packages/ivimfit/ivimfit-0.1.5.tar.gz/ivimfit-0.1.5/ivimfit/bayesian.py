import numpy as np
import pymc as pm
import pytensor.tensor as pt


def ivim_model(b, f, D, D_star):
    """
    IVIM biexponential model:
    S(b)/S0 = f * exp(-b * D*) + (1 - f) * exp(-b * D)
    """
    return f * pt.exp(-b * D_star) + (1 - f) * pt.exp(-b * D)


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


def fit_bayesian(b_values, signal, omit_b0=False, draws=500, chains=4, progressbar=False):
    """
    Fit IVIM model using Bayesian inference with PyMC.

    Parameters:
        b_values (array-like): b-values
        signal (array-like): signal intensities
        omit_b0 (bool): exclude b=0 from fitting
        draws (int): number of MCMC samples per chain
        chains (int): number of chains
        progressbar (bool): show PyMC progress bar

    Returns:
        f_mean, D_mean, D_star_mean
    """
    b, s = prepare_signal(b_values, signal, omit_b0=omit_b0)

    if len(b) < 4:
        raise ValueError("Not enough data for Bayesian IVIM fitting.")

    s = s / s[0]  # Normalize to S0
    b = b.astype("float32")
    s = s.astype("float32")

    with pm.Model():
        # Priors
        f = pm.Uniform("f", 0.0, 0.3)
        D = pm.Uniform("D", 0.0005, 0.003)
        D_star = pm.Uniform("D_star", 0.005, 0.05)
        sigma = pm.HalfNormal("sigma", sigma=0.05)

        # IVIM model
        S_model = ivim_model(b[:, None], f, D, D_star)

        # Likelihood
        pm.Normal("obs", mu=S_model.flatten(), sigma=sigma, observed=s)

        # Sampling
        trace = pm.sample(draws=draws, chains=chains, progressbar=progressbar, target_accept=0.9)

    f_mean = trace.posterior["f"].mean().item()
    D_mean = trace.posterior["D"].mean().item()
    D_star_mean = trace.posterior["D_star"].mean().item()

    return f_mean, D_mean, D_star_mean
