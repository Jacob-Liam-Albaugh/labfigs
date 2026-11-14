"""Shows gradient draws and the 2D field style on synthetic data (no inference is run)."""
from pathlib import Path

import numpy as np

import labfigs as lf

rng = np.random.default_rng(1)
out = Path(__file__).parent.parent / "out"
lf.use()

x = np.linspace(0, 1, 200)
k = np.arange(1, 6)[None, :, None]
waves = rng.normal(size=(2000, 5, 1)) / k * np.sin(np.pi * k * x + rng.uniform(0, 2 * np.pi, (2000, 5, 1)))
draws = np.sin(2 * np.pi * x) + 0.35 * waves.sum(1)
fig, axes = lf.subplots(1, 2, aspect=0.7, sharey=True)
for ax, gradient in zip(axes, (False, True)):
    lf.paths(ax, x, draws, gradient=gradient, label="Posterior draws")
    ax.plot(x, np.sin(2 * np.pi * x), color=lf.TRUE, ls="--", label="True")
    ax.set(title="gradient" if gradient else "flat", xlabel="$x$", xticks=[0, 0.5, 1], yticks=[-2, -1, 0, 1, 2])
axes[0].set_ylabel("$u$")
lf.legend_above(fig)
lf.save(fig, out / "gradient_draws")

X, Y = np.meshgrid(np.linspace(0, 1, 80), np.linspace(0, 1, 80))
true = np.exp(-((X - 0.3) ** 2 + (Y - 0.6) ** 2) / 0.03) + 0.6 * np.exp(-((X - 0.7) ** 2 + (Y - 0.3) ** 2) / 0.05)
mean = true + 0.08 * np.sin(5 * X) * np.cos(4 * Y)
sensors = rng.uniform(0.1, 0.9, (2, 12))
fig, axes = lf.subplots(1, 3, width=8, aspect=0.95, sharey=True)
panels = [("True", true, {"vmin": 0, "vmax": 1}), ("Posterior mean", mean, {"vmin": 0, "vmax": 1}), ("Error", mean - true, {"center": 0})]
for ax, (title, z, kw) in zip(axes, panels):
    lf.heatmap(ax, X, Y, z, **kw)
    lf.data(ax, *sensors, label="Sensors")
    ax.set(title=title, xlabel="$x$", xticks=[0, 0.5, 1], yticks=[0, 0.5, 1], aspect="equal")
axes[0].set_ylabel("$y$")
lf.legend_above(fig)
lf.save(fig, out / "field")

assert all((out / f"{name}.png").stat().st_size > 0 for name in ("gradient_draws", "field"))
print("wrote", out / "gradient_draws.png", out / "field.png")
