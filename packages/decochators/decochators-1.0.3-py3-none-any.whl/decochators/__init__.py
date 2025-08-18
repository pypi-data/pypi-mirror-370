from .dimensions.one_dimension.attach_chaos_1d import attach_chaos_tests_1d
from .dimensions.three_dimensions.attach_chaos_3d import attach_chaos_tests_3d

def attach_chaos_tests(dim: str = "1d"):
    dim = dim.lower()
    if dim == "1d":
        return attach_chaos_tests_1d
    elif dim == "3d":
        return attach_chaos_tests_3d
    else:
        raise ValueError(f"Dimension not supported: {dim}. Try '1d' or '3d'.")

__all__ = [
    "attach_chaos_tests",
]
