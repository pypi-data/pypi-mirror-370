import numpy as np
from typing import Callable
from scipy.integrate import cumulative_trapezoid

def lyapunov(step_func: Callable[[np.ndarray], np.ndarray], xyz0: np.ndarray,
                eps: float = 1e-8, idx: int = 10000, discard: int = 100) -> float:
    xyz = np.array(xyz0, dtype=float)
    xyz_pert = xyz + eps
    acc = 0.0

    for i in range(int(idx)):
        xyz = np.array(step_func(xyz))
        xyz_pert = np.array(step_func(xyz_pert))
        delta = np.linalg.norm(xyz_pert - xyz)
        if delta == 0.0:
            delta = eps
        xyz_pert = xyz + eps * (xyz_pert - xyz) / delta

        if i >= discard:
            acc += np.log(delta / eps)

    effective = max(1, int(idx) - int(discard))
    return acc / effective

# binarized test 0-1
def btest01(series: np.ndarray, threshold: float = 0.5) -> np.ndarray:
    series = np.asarray(series)
    result = np.empty(3)
    for i in range(3):
        mean = np.mean(series[:, i])
        binary = (series[:, i] > mean).astype(int)
        result[i] = np.mean(binary)
    return result

def test01(step_func_raw, xyz0, N=5000, burn_in=100, c=np.pi, *args, **kwargs):
    xyz = np.array(xyz0, dtype=float)
    series = np.empty((N, 3), dtype=float)

    for _ in range(burn_in):
        xyz = step_func_raw(xyz, *args, **kwargs)

    for i in range(N):
        xyz = step_func_raw(xyz, *args, **kwargs)
        series[i] = xyz

    time = np.arange(N)
    K_vals = np.empty(3)
    for i in range(3):
        phi = series[:, i]
        integral_phi = cumulative_trapezoid(phi, time, initial=0.0)
        theta = c * time + integral_phi
        integrand = phi * np.cos(theta)
        p = cumulative_trapezoid(integrand, time, initial=0.0)

        n = len(p)
        max_lag = max(2, n // 10)
        M = np.array([np.mean((p[j:] - p[:-j]) ** 2) for j in range(1, max_lag)])
        t_vals = time[1:max_lag]

        log_M = np.log(M + 1e-16)
        log_t = np.log(t_vals + 1e-16)
        K, _ = np.polyfit(log_t, log_M, 1)
        K_vals[i] = K

    return K_vals   

def ks(series: np.ndarray, bins: int = 10) -> np.ndarray:
    series = np.asarray(series)
    result = np.empty(3)
    for i in range(3):
        hist, _ = np.histogram(series[:, i], bins=bins, density=True)
        p = hist / np.sum(hist)
        p = p[p > 0]
        result[i] = -np.sum(p * np.log(p))
    return result