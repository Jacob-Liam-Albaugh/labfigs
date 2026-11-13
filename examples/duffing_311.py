"""Reproduces the layout of Hao thesis Fig. 3.11 on synthetic Duffing data (no inference is run)."""
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

import labfigs as lf

DELTA, ALPHA, RHO, GAMMA, OMEGA = 0.3, -1.0, 1.0, 0.37, 1.2
T, N, DRAWS, SIGMA_Y = 30.0, 600, 100, 0.04
rng = np.random.default_rng(0)


def duffing(t, x, scale=1.0):
    return [x[1], scale * (-DELTA * x[1] - ALPHA * x[0] - RHO * x[0] ** 3) + GAMMA * np.cos(OMEGA * t)]


def smooth_noise(t, size):
    freq = rng.uniform(0.2, 1.5, (DRAWS, 4, 1))
    phase = rng.uniform(0, 2 * np.pi, (DRAWS, 4, 1))
    amp = rng.normal(size=(DRAWS, 4, 1))
    return size * (amp * np.sin(freq * t + phase)).sum(1) / 2


t_all = np.linspace(100, 100 + 2 * T, 2 * N - 1)
t_obs, t_new = t_all[:N], t_all[N - 1:]
true = solve_ivp(duffing, (0, t_all[-1]), [1.0, 0.0], t_eval=t_all, rtol=1e-9, atol=1e-9).y
true = np.vstack([true, true[0] + SIGMA_Y * rng.normal(size=t_all.size)])
unit = np.abs(true).max(axis=1, keepdims=True)

widths = np.array([0.03, 0.09, 0.03])[:, None, None]
post = true[:, None, :N] + np.stack([smooth_noise(t_obs, 1.0) for _ in range(3)]) * widths
post[2] += SIGMA_Y * rng.normal(size=(DRAWS, N))

pred = np.empty((3, DRAWS, N))
for k in range(DRAWS):
    start = post[:2, k, -1]
    sol = solve_ivp(duffing, (t_new[0], t_new[-1]), start, t_eval=t_new, args=(1 + 0.03 * rng.normal(),), rtol=1e-8)
    pred[:2, k] = sol.y
    pred[2, k] = sol.y[0] + SIGMA_Y * rng.normal(size=N)

lf.use()
fig, axes = lf.subplots(3, 1, aspect=0.24)
labels = [r"$x_1/\bar{x}_1$", r"$x_2/\bar{x}_2$", r"$y/\bar{y}$"]
tau_obs, tau_new, tau_all = (t_obs - 100) / T, (t_new - 100) / T, (t_all - 100) / T
for i, ax in enumerate(axes):
    lf.band(ax, tau_obs, post[i] / unit[i], label="Posterior")
    lf.paths(ax, tau_new, pred[i] / unit[i], label="Posterior predictive")
    ax.plot(tau_all, true[i] / unit[i], color=lf.TRUE, label="True")
    lf.split(ax, 1.0)
    ax.set(xlim=(0, 2), xticks=np.arange(0, 2.01, 0.25), yticks=[-1, 0, 1], ylim=(-1.15, 1.15),
           xlabel=r"$t/T$", ylabel=labels[i])
lf.legend_above(axes[0])

out = lf.save(fig, Path(__file__).parent.parent / "out" / "duffing_311")
assert out.with_suffix(".pdf").stat().st_size > 0 and out.with_suffix(".png").stat().st_size > 0
print("wrote", out.with_suffix(".png"))
