import numpy as np
from typing import Callable

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

def test01(series: np.ndarray, threshold: float = 0.5) -> np.ndarray:
    series = np.asarray(series)
    result = np.empty(3)
    for i in range(3):
        mean = np.mean(series[:, i])
        binary = (series[:, i] > mean).astype(int)
        result[i] = np.mean(binary)
    return result

def ks(series: np.ndarray, bins: int = 10) -> np.ndarray:
    series = np.asarray(series)
    result = np.empty(3)
    for i in range(3):
        hist, _ = np.histogram(series[:, i], bins=bins, density=True)
        p = hist / np.sum(hist)
        p = p[p > 0]
        result[i] = -np.sum(p * np.log(p))
    return result