from ...core import ChaosDecoratorBase
from ...helpers import lyapunov_1d, test01_1d, ks_1d
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import cumulative_trapezoid

class Chaos1D(ChaosDecoratorBase):
    dim = 1

    def _build_mth(self, wrapper):
        class mth:
            @staticmethod
            def lyapunov(x0, *args, eps=1e-8, idx=10000, discard=100, **kwargs):
                return lyapunov_1d(lambda x: self.step_func(x, *args, **kwargs),
                                   x0, eps=eps, idx=idx, discard=discard)

            @staticmethod
            def test01(x0, *args, N=1000, burn_in=0, **kwargs):
                serie = wrapper(x0, *args, N=N, burn_in=burn_in, **kwargs)
                return test01_1d(serie)

            @staticmethod
            def ks(x0, *args, N=1000, burn_in=0, bins=10, **kwargs):
                serie = wrapper(x0, *args, N=N, burn_in=burn_in, **kwargs)
                return ks_1d(serie, bins=bins)
        return mth

    def _build_vwr(self, wrapper):
        class vwr:
            @staticmethod
            def draw(step_func_raw, x0, N=5000, burn_in=100, *args, **kwargs):
                x = float(x0)
                series = np.empty(N, dtype=float)

                for _ in range(burn_in):
                    x = float(step_func_raw(x, *args, **kwargs))

                for i in range(N):
                    x = float(step_func_raw(x, *args, **kwargs))
                    series[i] = x

                plt.figure(figsize=(10,3))
                plt.plot(series, ',k', alpha=0.7)
                plt.title("1D Chaos Trajectory")
                plt.xlabel("Iteration")
                plt.ylabel("x")
                plt.show()

            @staticmethod
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

                plt.figure(figsize=(8,1))
                plt.imshow([np.array([K])], cmap='viridis', aspect='auto')
                plt.colorbar(label='K (0–1 test)')
                plt.yticks([])
                plt.xticks([0], ['X'])
                plt.title('0–1 Chaos Test')
                plt.show()

                return K

            @staticmethod
            def bifurcation(step_func, x0, param_name: str, param_range,
                            N=1000, burn_in=500, last_points=100, *args, **kwargs):
                x0 = float(x0)
                param_values = np.array(param_range)
                plt.figure(figsize=(10,6))

                for p in param_values:
                    kwargs[param_name] = p
                    traj = wrapper(x0, *args, N=N, burn_in=0, **kwargs)
                    series = traj[burn_in:]
                    if last_points < len(series):
                        series = series[-last_points:]
                    plt.plot([p]*len(series), series, ',k', alpha=0.5)

                plt.xlabel(param_name)
                plt.ylabel('x')
                plt.title(f'Bifurcation diagram of {param_name}')
                plt.show()
        return vwr



def attach_chaos_tests_1d(step_func):
    return Chaos1D(step_func)()
