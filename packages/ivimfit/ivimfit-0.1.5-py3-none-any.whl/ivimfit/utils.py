import numpy as np
import matplotlib.pyplot as plt


def calculate_r_squared(y_true, y_pred):
    """
    Compute coefficient of determination (R²)
    """
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    r2 = 1 - (ss_res / ss_tot)
    return r2


def plot_fit(b_values, signal, fit_func, fit_params, model_name="IVIM"):
    """
    Plot raw signal and fitted curve, display R² and parameters.

    Parameters:
        b_values: b-values used in fitting
        signal: normalized signal intensities
        fit_func: model function to plot
        fit_params: parameters passed to model
        model_name: string for plot title

    Returns:
        matplotlib figure and axis
    """
    b = np.array(b_values)
    s = np.array(signal)
    s = s / s[0]  # normalize

    b_plot = np.linspace(np.min(b), np.max(b), 100)
    y_fit = fit_func(b_plot, *fit_params)
    y_pred = fit_func(b, *fit_params)

    r2 = calculate_r_squared(s, y_pred)
    param_names = {
        1: ["D"],
        2: ["f", "D*"],  # Used only for lambda functions like segmented
        3: ["f", "D", "D*"],
        5: ["f1","f2","D","D1*","D2*"]
    }
    labels = param_names.get(len(fit_params), [f"p{i+1}" for i in range(len(fit_params))])
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(b, s, 'o', label='Observed', color='black')
    ax.plot(b_plot, y_fit, '-', label=f'{model_name} Fit', color='blue')
    ax.set_xlabel('b-value (s/mm²)')
    ax.set_ylabel('Normalized Signal')
    ax.set_title(f"{model_name} Fit\nR² = {r2:.4f}")

    param_text = "\n".join([f"{name} = {val:.4g}" for name, val in zip(labels, fit_params)])
    ax.text(0.05, 0.05, param_text, transform=ax.transAxes, fontsize=9,
            bbox=dict(facecolor='white', alpha=0.7))

    ax.legend()
    ax.grid(True)
    plt.tight_layout()
    return fig, ax
