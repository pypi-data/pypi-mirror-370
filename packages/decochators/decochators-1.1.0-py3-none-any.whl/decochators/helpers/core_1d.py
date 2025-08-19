import numpy as np
from typing import Callable
from scipy.integrate import cumulative_trapezoid

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

# binarized test 0-1
def btest01(series: np.ndarray, threshold: float = 0.5) -> float:
    series = np.asarray(series)
    mean = np.mean(series)
    binary = (series > mean).astype(int)
    return np.mean(binary)

# complex test 0-1
def test01(step_func_raw, x0, N=5000, burn_in=100, c=np.pi, *args, **kwargs):
    x = float(x0)
    series = np.empty(N, dtype=float)

    for _ in range(burn_in):
        x = float(step_func_raw(x, *args, **kwargs))

    for i in range(N):
        x = float(step_func_raw(x, *args, **kwargs))
        series[i] = x

    time = np.arange(N)
    phi = series
    integral_phi = cumulative_trapezoid(phi, time, initial=0.0)
    theta = c * time + integral_phi
    integrand = phi * np.cos(theta)
    p = cumulative_trapezoid(integrand, time, initial=0.0)

    max_lag = max(2, len(p)//10)
    M = np.array([np.mean((p[j:] - p[:-j])**2) for j in range(1, max_lag)])
    t_vals = time[1:max_lag]

    log_M = np.log(M + 1e-16)
    log_t = np.log(t_vals + 1e-16)
    K, _ = np.polyfit(log_t, log_M, 1)

    return K

#kolmogorov_sinai
def ks(series: np.ndarray, bins: int = 10) -> float:
    series = np.asarray(series)
    hist, edges = np.histogram(series, bins=bins, density=True)
    p = hist / np.sum(hist)
    p = p[p > 0]
    return -np.sum(p * np.log(p))