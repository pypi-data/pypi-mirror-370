from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
from functools import wraps
from typing import Callable

class ChaosDecoratorBase:
    dim: int = None
    helpers: dict = {}

    def __init__(self, step_func: Callable):
        self.step_func = step_func

    def __call__(self):
        @wraps(self.step_func)
        def wrapper(x0, *args, N=1000, burn_in=0, seed=None, **kwargs):
            rng = np.random.default_rng(seed) if seed is not None else None
            state = np.array(x0, dtype=float)

            # Burn-in
            for _ in range(int(burn_in)):
                state = np.array(self.step_func(state, *args, **kwargs))

            # Output
            out_shape = (int(N),) if self.dim == 1 else (int(N), self.dim)
            out = np.empty(out_shape, dtype=float)

            for i in range(int(N)):
                out[i] = state
                state = np.array(self.step_func(state, *args, **kwargs))

            return out

        # inject classes
        wrapper.mth = self._build_mth(wrapper)
        wrapper.vwr = self._build_vwr(wrapper)

        return wrapper

    # methods that override subclasses
    def _build_mth(self, wrapper): raise NotImplementedError
    def _build_vwr(self, wrapper): raise NotImplementedError
