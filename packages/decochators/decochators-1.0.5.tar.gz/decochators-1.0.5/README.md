*decochators* is a library to facilitate the study (visualization and analysis) of chaotic systems focused on application in **CBE** (Chaos-Based-Encryption) algorithms.

## Structure

```
Class chaoticMap
│ 
├── Inherited class mth (Analysis)
│ 	│ 
│   ├── func Lyapunov
│   ├── func Kolmogorov-Sinai
│   └── func Test 0-1 (Binarized!!!)
│
└── Inherited class vwr (Visualization)
	│ 
    ├── func Draw
    ├── func Bifurcation
    └── func Test 0-1
```

## Supported Python Versions

- Python 3.11+

## Supported Chaos Systems

- One-dimensional
- Three-dimensional
	- Continuous dynamic systems
	- Discrete over time

## Installing

Install or upgrade the Python bindings with *`pip <https://pip.pypa.io/>`*.

Latest official release:

```bash
pip install -U decochators
```

Specific version (not recommended for versions lower than 1.1.0):

```bash
pip install -U decochators==N.N.NxN
```

Latest official release from TestPypi:

```bash
pip install -i https://test.pypi.org/simple/ decochators
```

Specific version from TestPypi:

```bash
pip install -i https://test.pypi.org/simple/ decochators==N.N.NxN
```

Where $N \in \mathbb{Z}$ and $x \in \{a, b, c, \dots, z\}$, example: `1.0.4a0`.


Note: you should consider using a [virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments) to create an isolated Python environment for installation.

## Testing Binary Chaos Test 0-1

> Important for versions lower than `decochators1.1.0`, `mth.test01` is a binarized modified test, be careful comparing or testing complex systems.

```python
from decochators import attach_chaos_tests
import numpy as np

@attach_chaos_tests("1d")
def logistic_step(x: float, r: float = 4.0) -> float:
    return r * x * (1 - x)

serie = logistic_step(0.1, r=3.9, N=1000, burn_in=100, seed=42)
k01 = logistic_step.mth.test01(0.1, r=3.9)

print("Results with burn-in & seed:")
print(f"Test 0-1 with the serie binarized: {k01}")

k01_vwr=logistic_step.vwr.test01(
    logistic_step.__wrapped__,
    x0=0.1,
    N=1000,
    burn_in=100,
    r=3.9
),

print(f"Complete Test 0-1: {k01_vwr}")
```

## Calling other 1 Dimensions functions
With the same chaotic system than before:

```python
def logistic_step(x: float, r: float = 4.0) -> float:
    return r * x * (1 - x)
```

### Generating series

```python
logistic_step(0.1, r=3.9, N=1000, burn_in=100, seed=42)
```

#### Lyapunov Exponent Analysis

```python
logistic_step.mth.lyapunov(0.1, r=3.9)
```

#### Kolmorogov-Sinai Analysis

```python
logistic_step.mth.ks(0.1, r=3.9)
```

#### Chaotic Draw Visualization

```python
logistic_step.vwr.draw(logistic_step.__wrapped__, x0=0.3, N=250000, burn_in=100, r=4.0)
```

#### Bifurcation System Visualization

```python
import numpy as np

param_range = np.linspace(2.5, 4.0, 300)
logistic_step.vwr.bifurcation(logistic_step.__wrapped__, x0=0.1, param_name="r", param_range=param_range, N=5000, burn_in=200, last_points=50)
```


## Calling 3 Dimensions functions

Chaotic System sample:

```python
def rossler_step(xyz: np.ndarray, a: float = 0.2, b: float = 0.2, c: float = 5.7) -> np.ndarray:
    x, y, z = xyz
    dt = 0.01
    dx = -y - z
    dy = x + a*y
    dz = b + z*(x - c)
    return np.array([x + dx*dt, y + dy*dt, z + dz*dt])
```

#### Lyapunov Exponent Analysis

```python
rossler_step.mth.lyapunov([0.1,0,0])
```

#### Kolmorogov-Sinai Analysis

```python
rossler_step.mth.ks([0.1,0,0])
```

#### Binary Test Analysis

As in 1 Dimension, 3D `mth.test01` is in base of a binarized test in *lower than decochatorsv1.1.0*, be careful. 

```python
rossler_step.mth.test01([0.1,0,0])
```

#### Chaotic Draw Visualization

```python
rossler_step.vwr.draw(rossler_step.__wrapped__, [0.1, 0.0, 0.0], N=10000, burn_in=500, a=0.2, b=0.2, c=5.7)
```

#### Bifurcation System Visualization

```python
import numpy as np

rossler_step.vwr.bifurcation(
    step_func=rossler_step,
    xyz0=[0.1,0.0,0.0],
    param_name='c',
    param_range=np.linspace(4, 6, 200),
    coord=2,      # Project on Cord Z | 0=X;1=Y;2=Z
    N=2000,
    burn_in=500
)
```

#### Binary Tests Visualization

On the other hand, `vwr.test01` is the completed binary test, without binarization.

```python
rossler_step.vwr.test01(rossler_step.__wrapped__, [0.1,0.0,0.0], N=5000, burn_in=100)
```

---

For further explication: https://yoshlsec.github.io/cbe-blogs/
For source code: https://github.com/yoshlsec/decochators

I hope its useful, first public python module for you all ;)