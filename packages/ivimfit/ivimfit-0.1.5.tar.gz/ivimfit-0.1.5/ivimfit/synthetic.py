# ivimfit/synthetic.py
from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
from dataclasses import dataclass
from typing import Iterable, Tuple, Optional

@dataclass
class PhantomParams:
    shape: Tuple[int, int] = (128, 128)
    square_size: int = 64
    s0_bright: float = 1.0     
    s0_dark: float = 0.30      
    D_bright: float = 0.0015   
    D_dark: float = 0.0030     
    noise_sigma: float = 0.02  

def _make_maps(pp: PhantomParams) -> Tuple[np.ndarray, np.ndarray]:
    H, W = pp.shape
    S0 = np.full((H, W), pp.s0_dark, dtype=np.float32)
    D  = np.full((H, W), pp.D_dark,  dtype=np.float32)
    r0 = (H - pp.square_size) // 2
    c0 = (W - pp.square_size) // 2
    S0[r0:r0+pp.square_size, c0:c0+pp.square_size] = pp.s0_bright
    D[r0:r0+pp.square_size, c0:c0+pp.square_size]   = pp.D_bright
    return S0, D

def generate_dwi_stack(
    b_values: Iterable[float],
    params: PhantomParams = PhantomParams(),
    seed: Optional[int] = 42
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    
    b_vals = np.asarray(list(b_values), dtype=float)
    if b_vals.size == 0:
        raise ValueError("b_values boş olamaz.")
    S0, D = _make_maps(params)
    rng = np.random.default_rng(seed)
    stack = []
    for b in b_vals:
        img = S0 * np.exp(-b * D)
        noise = rng.normal(0.0, params.noise_sigma * img.max(), size=img.shape)
        img_noisy = np.clip(img + noise, 0, None).astype(np.float32)
        stack.append(img_noisy)
    stack = np.stack(stack, axis=0)  # (N,H,W)
    return stack, S0, D

def _pick_square_roi(image2d: np.ndarray) -> Tuple[int, int, int]:
    
    
   
    from matplotlib.patches import Rectangle

    H, W = image2d.shape
    fig, ax = plt.subplots()
    ax.imshow(
        image2d, cmap="gray", origin="upper",
        vmin=0, vmax=max(1e-6, float(image2d.max()))
    )
    ax.set_title("Draw ROI and Press Enter")

    
    roi_patch = Rectangle((0, 0), 1, 1, fill=False, linewidth=2)
    ax.add_patch(roi_patch)

    roi = {"r0": None, "c0": None, "size": None}

    def onselect(eclick, erelease):
        
        if (eclick.xdata is None) or (eclick.ydata is None) or \
           (erelease.xdata is None) or (erelease.ydata is None):
            return

        r_min, r_max = sorted([eclick.ydata, erelease.ydata])
        c_min, c_max = sorted([eclick.xdata, erelease.xdata])
        h = float(r_max - r_min)
        w = float(c_max - c_min)
        if h < 1 or w < 1:
            return  

        
        size = int(max(1, min(h, w)))
        r_c = (r_min + r_max) / 2.0
        c_c = (c_min + c_max) / 2.0
        r0 = int(round(r_c - size / 2.0))
        c0 = int(round(c_c - size / 2.0))

        
        r0 = max(0, min(H - size, r0))
        c0 = max(0, min(W - size, c0))

        
        roi["r0"], roi["c0"], roi["size"] = r0, c0, size
        roi_patch.set_xy((c0, r0))
        roi_patch.set_width(size)
        roi_patch.set_height(size)
        fig.canvas.draw_idle()

    def on_key(event):
        if event.key == "enter":
            plt.close(fig)

    
    selector = RectangleSelector(
        ax, onselect,
        interactive=True,
        useblit=False,          
        minspanx=2, minspany=2, 
        drag_from_anywhere=True,
        spancoords="data"
        
    )
    fig._selector_ref = selector  

    fig.canvas.mpl_connect("key_press_event", on_key)
    plt.show()

    if roi["size"] is None:
        raise RuntimeError(
            "ROI seçilmedi. Lütfen fareyle sürükleyerek bir kare çizip Enter’a basın."
        )
    return roi["r0"], roi["c0"], roi["size"]



def _mean_signal_in_roi(stack: np.ndarray, roi: Tuple[int, int, int]) -> np.ndarray:
    r0, c0, size = roi
    patch = stack[:, r0:r0+size, c0:c0+size]
    return patch.mean(axis=(1, 2))

def generate_measure_signals(
    b_values: Iterable[float],
    params: PhantomParams = PhantomParams(),
    roi: Optional[Tuple[int, int, int]] = None,
    seed: Optional[int] = 42,
    show_lowest_b: bool = True
) -> Tuple[np.ndarray, np.ndarray, Tuple[int, int, int]]:
    
    stack, S0, D = generate_dwi_stack(b_values, params=params, seed=seed)
    b_vals = np.asarray(list(b_values), dtype=float)
    idx_low = int(np.argmin(b_vals))

    if roi is None:
        if show_lowest_b:
            _ = _pick_square_roi(stack[idx_low])
            roi = _
        else:
            raise ValueError("roi=None ise etkileşimli seçim için show_lowest_b=True olmalı.")

    mean_signal = _mean_signal_in_roi(stack, roi)
    return stack, mean_signal.astype(np.float32), roi
def show_stack_grid(
    stack: np.ndarray,
    b_values: Iterable[float],
    roi: Optional[Tuple[int, int, int]] = None,
    cols: int = 4,
    suptitle: Optional[str] = "Synthetic DWI Stack"
) -> None:
    """
    DWI yığınını tek figürde 2D grid olarak gösterir.
    - b-değerlerine göre artan sırada (en düşük b solda/üstte)
    - Varsayılan düzen: 4 sütun; 8 görüntü varsa 4+4 (üst+alt)
    - Tüm görüntüler için aynı vmin/vmax kullanır (parlaklık karşılaştırılabilir)
    - roi verilirse ilk karede (en düşük b) kutuyu çizer
    """
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    b_vals = np.asarray(list(b_values), dtype=float)
    order = np.argsort(b_vals)
    b_sorted = b_vals[order]
    stack_sorted = stack[order]

    N = len(b_sorted)
    rows = int(np.ceil(N / cols))
    vmax = float(stack_sorted.max())
    vmin = 0.0

    fig, axes = plt.subplots(rows, cols, figsize=(3.0*cols, 3.0*rows))
    # axes'i 2D array'e zorla
    if rows == 1:
        axes = np.array([axes])
    if cols == 1:
        axes = axes.reshape(rows, 1)

    k = 0
    for r in range(rows):
        for c in range(cols):
            ax = axes[r, c]
            if k < N:
                img = stack_sorted[k]
                ax.imshow(img, cmap="gray", origin="upper", vmin=vmin, vmax=vmax)
                ax.set_title(f"b = {b_sorted[k]:.0f}")
                ax.axis("off")
                # ROI sadece ilk karede (en düşük b) gösterilsin (isteğe bağlı)
                if roi is not None and k == 0:
                    r0, c0, size = roi
                    ax.add_patch(Rectangle((c0, r0), size, size, fill=False, linewidth=2))
            else:
                ax.axis("off")
            k += 1

    if suptitle:
        fig.suptitle(suptitle)
    fig.tight_layout()
    plt.show()

