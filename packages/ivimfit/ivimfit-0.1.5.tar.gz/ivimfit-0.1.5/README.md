# ivimfit

**ivimfit** is a modular Python library for fitting Intravoxel Incoherent Motion (IVIM) diffusion MRI models.  
It supports monoexponential ADC fitting, biexponential (free and segmented) models, as well as Bayesian inference using PyMC.

Designed for researchers and clinicians working with DWI/IVIM datasets, this package offers signal filtering, robust modeling, and visualization tools for parameter evaluation.

---

## 📦 Features

- ✅ Monoexponential ADC fitting
- ✅ Full biexponential model (nonlinear free fit)
- ✅ Segmented biexponential model (2-step D + [f, D*])
- ✅ Bayesian IVIM modeling using MCMC via PyMC
- ✅ Full Triexponential model (fast and intermediate component calculation)
- ✅ Optional exclusion of b = 0
- ✅ Automatic filtering of b-values > 1000
- ✅ R² calculation and signal-fit visualization utilities
## Changelog 0.1.5
- ✅ Generating Synthetic Data Added to Library
- ✅ Optimizeble Parameters Include for Generating Synthethic Data
---
## 🧳 License

This project is licensed under the MIT License - see the [LICENSE] file for details.

## 📥 Installation



```bash
pip install ivimfit .
```

## 📥 Example Usage

```bash
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from ivimfit.synthetic import PhantomParams, generate_measure_signals
from ivimfit.utils import plot_fit, calculate_r_squared
from ivimfit.adc import fit_adc, monoexp_model
from ivimfit.biexp import fit_biexp_free, biexp_model
from ivimfit.segmented import fit_biexp_segmented, biexp_fixed_D_model

def main():
    
    b = np.array([0, 50, 100, 200, 400, 600, 800,900,1000], dtype=float)

    pp = PhantomParams(
        shape=(128, 128),
        square_size=64,
        s0_bright=1.0,
        s0_dark=0.30,
        D_bright=0.0015,
        D_dark=0.0030,
        noise_sigma=0.02
    )

    stack, s, roi = generate_measure_signals(b, params=pp, seed=123)
    r0, c0, size = roi

    
    img0 = stack[np.argmin(b)]
    plt.imshow(img0, cmap="gray", origin="upper")
    plt.gca().add_patch(Rectangle((c0, r0), size, size, fill=False, linewidth=2))
    plt.title("b (en düşük) + ROI")
    plt.show()
    from ivimfit.synthetic import show_stack_grid

    show_stack_grid(stack, b, roi=roi, cols=4, suptitle="Synthetic DWI (low b → high b)")
   
    adc = fit_adc(b, s)
    r2 = calculate_r_squared(s / s[0], monoexp_model(b, adc))
    fig, ax = plot_fit(b, s, monoexp_model, [adc], model_name=f"ADC Fit (R² = {r2:.4f})")
    plt.show()

   
    f, D, D_star = fit_biexp_free(b, s)
    r2 = calculate_r_squared(s / s[0], biexp_model(b, f, D, D_star))
    fig, ax = plot_fit(b, s, biexp_model, [f, D, D_star], model_name=f"Free Fit (R² = {r2:.4f})")
    plt.show()

    
    f_seg, D_fixed, D_star_seg = fit_biexp_segmented(b, s)
    r2 = calculate_r_squared(s / s[0], biexp_fixed_D_model(b, f_seg, D_star_seg, D_fixed))
    fig, ax = plot_fit(
        b, s,
        lambda b_, f_, D_star_, D_fixed_: biexp_fixed_D_model(b_, f_, D_star_, D_fixed_),
        [f_seg, D_star_seg, D_fixed],
        model_name=f"Segmented Fit (R² = {r2:.4f})"
    )
    plt.show()
   
    
    try:
        from ivimfit.bayesian import fit_bayesian
        f_bay, D_bay, Dstar_bay = fit_bayesian(
            b, s, draws=500, chains=2
        )
        r2 = calculate_r_squared(s / s[0], biexp_model(b, f_bay, D_bay, Dstar_bay))
        fig, ax = plot_fit(b, s, biexp_model, [f_bay, D_bay, Dstar_bay],
                           model_name=f"Bayesian Fit (R² = {r2:.4f})")
        plt.show()
    except Exception as e:
        print("[Bayesian] atlandı:", repr(e))

    
    try:
        from ivimfit.triexp import fit_triexp_free, triexp_model
        f1, f2, Dm, D1s, D2s = fit_triexp_free(b, s)
        pred = triexp_model(b, f1, f2, Dm, D1s, D2s)
        r2 = calculate_r_squared(s / s[0], pred)
        fig, ax = plot_fit(b, s, triexp_model, [f1, f2, Dm, D1s, D2s],
                           model_name=f"Tri-exponential Fit (R² = {r2:.4f})")
        plt.show()
    except Exception as e:
        print("[Triexponential] atlandı:", repr(e))

if __name__ == "__main__":
    main()




