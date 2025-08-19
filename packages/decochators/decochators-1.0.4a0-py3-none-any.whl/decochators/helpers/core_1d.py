import numpy as np
from typing import Callable

def lyapunov(step_func: Callable[[float], float], x0: float, eps: float = 1e-8,
                idx: int = 10000, discard: int = 100) -> float:
    x = float(x0)
    x_pert = float(x0 + eps)
    acc = 0.0

    for i in range(int(idx)):
        x = float(step_func(x))
        x_pert = float(step_func(x_pert))
        delta = abs(x_pert - x)
        if delta == 0.0:
            delta = eps
        x_pert = x + eps * (x_pert - x) / delta

        if i >= discard:
            acc += np.log(delta / eps)

    effective = max(1, int(idx) - int(discard))
    return acc / effective

def test01(series: np.ndarray, threshold: float = 0.5) -> float:
    series = np.asarray(series)
    mean = np.mean(series)
    binary = (series > mean).astype(int)
    return np.mean(binary)

#kolmogorov_sinai
def ks(series: np.ndarray, bins: int = 10) -> float:
    series = np.asarray(series)
    hist, edges = np.histogram(series, bins=bins, density=True)
    p = hist / np.sum(hist)
    p = p[p > 0]
    return -np.sum(p * np.log(p))