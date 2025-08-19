from ...core import ChaosDecoratorBase
from ...helpers import *
from scipy.integrate import cumulative_trapezoid
import numpy as np
import matplotlib.pyplot as plt

class Chaos3D(ChaosDecoratorBase):
	dim = 3

	def _build_mth(self, wrapper):
		class mth:
			@staticmethod
			def lyapunov(xyz0, *args, eps=1e-8, idx=10000, discard=100, **kwargs):
				return lyapunov_3d(lambda x: self.step_func(x, *args, **kwargs),
								   np.array(xyz0), eps=eps, idx=idx, discard=discard)

			@staticmethod
			def btest01(xyz0, *args, N=1000, burn_in=0, **kwargs):
				serie = wrapper(xyz0, *args, N=N, burn_in=burn_in, **kwargs)
				return btest01_3d(serie)

			@staticmethod
			def test01(step_func_raw, xyz0, *args, N=5000, burn_in=100, c=np.pi, **kwargs):
				return test01_3d(step_func_raw, xyz0, *args, N=5000, burn_in=100, c=np.pi, **kwargs)

			@staticmethod
			def ks(xyz0, *args, N=1000, burn_in=0, bins=10, **kwargs):
				serie = wrapper(xyz0, *args, N=N, burn_in=burn_in, **kwargs)
				return ks_3d(serie, bins=bins)
		return mth

	def _build_vwr(self, wrapper):
		class vwr:
			@staticmethod
			def draw(step_func_raw, xyz0, N=5000, burn_in=100, *args, **kwargs):
				xyz = np.array(xyz0, dtype=float)
				out = np.empty((N,3))

				for _ in range(burn_in):
					xyz = step_func_raw(xyz, *args, **kwargs)

				for i in range(N):
					xyz = step_func_raw(xyz, *args, **kwargs)
					out[i] = xyz

				fig, axs = plt.subplots(1,3, figsize=(15,4))
				axs[0].scatter(out[:,0], out[:,1], s=0.1, alpha=0.5)
				axs[0].set_title("XY"); axs[0].set_xlabel("x"); axs[0].set_ylabel("y")

				axs[1].scatter(out[:,0], out[:,2], s=0.1, alpha=0.5)
				axs[1].set_title("XZ"); axs[1].set_xlabel("x"); axs[1].set_ylabel("z")

				axs[2].scatter(out[:,1], out[:,2], s=0.1, alpha=0.5)
				axs[2].set_title("YZ"); axs[2].set_xlabel("y"); axs[2].set_ylabel("z")

				plt.show()

			@staticmethod
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

				plt.figure(figsize=(4,1))
				plt.imshow(K_vals[np.newaxis, :], cmap='viridis', aspect='auto')
				plt.colorbar(label='K (0–1 test)')
				plt.yticks([])
				plt.xticks([0,1,2], ['X','Y','Z'])
				plt.title('0–1 Chaos Test per coordinate')
				plt.show()

				return K_vals

			@staticmethod
			def bifurcation(step_func, xyz0, param_name: str, param_range,
							coord: int = 0, N=1000, burn_in=500, last_points=100, *args, **kwargs):
				xyz0 = np.array(xyz0, dtype=float)
				param_values = np.array(param_range)
				plt.figure(figsize=(10,6))

				for p in param_values:
					kwargs[param_name] = p
					traj = wrapper(xyz0, *args, N=N, burn_in=0, **kwargs)
					series = traj[burn_in:, coord]
					if last_points < len(series):
						series = series[-last_points:]
					plt.plot([p]*len(series), series, ',k', alpha=0.5)

				plt.xlabel(param_name)
				plt.ylabel(f'coord {coord}')
				plt.title(f'Bifurcation diagram of {param_name}')
				plt.show()
		return vwr


def attach_chaos_tests_3d(step_func):
	return Chaos3D(step_func)()
