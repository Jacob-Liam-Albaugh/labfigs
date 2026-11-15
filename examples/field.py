"""Shows gradient draws and the 2D field style on synthetic data (no inference is run)."""
from pathlib import Path

import numpy as np

import labfigs as lf

rng = np.random.default_rng(1)
out = Path(__file__).parent
lf.use()

x = np.linspace(0, 1, 200)
k = np.arange(1, 6)[None, :, None]
waves = rng.normal(size=(2000, 5, 1)) / k * np.sin(np.pi * k * x + rng.uniform(0, 2 * np.pi, (2000, 5, 1)))
draws = np.sin(2 * np.pi * x) + 0.35 * waves.sum(1)
fig, axes = lf.subplots(4, 4, width=10.4, aspect=0.75, sharex=True, sharey=True)
for ax, gradient in zip(axes.flat, (False, *lf.RAMPS, lf.POSTERIOR, lf.PREDICTIVE, "tab:blue")):
    lf.paths(ax, x, draws, gradient=gradient, label="Posterior draws")
    ax.plot(x, np.sin(2 * np.pi * x), color=lf.TRUE, ls="--", label="True")
    ax.set(title=f"gradient={gradient}", xticks=[0, 0.5, 1], yticks=[-2, -1, 0, 1, 2])
fig.supxlabel("$x$")
fig.supylabel("$u$")
lf.legend_above(fig)
lf.save(fig, out / "gradient_draws")
assert ["interval" in " ".join(ax.get_legend_handles_labels()[1]) for ax in axes.flat] == [True] + 15 * [False]

X, Y = np.meshgrid(np.linspace(0, 1, 80), np.linspace(0, 1, 80))
R = np.hypot(X - 0.5, Y - 0.5)
waves = sum(np.cos(2 * np.pi * (a * X + b * Y) + c) for a, b, c in rng.uniform(-2, 2, (6, 3)))
fields = [
    np.exp(-((X - 0.3) ** 2 + (Y - 0.6) ** 2) / 0.03) + 0.6 * np.exp(-((X - 0.7) ** 2 + (Y - 0.3) ** 2) / 0.05),
    np.exp(-R ** 2 / 0.02),
    np.exp(-(X - Y) ** 2 / 0.02),
    np.sin(2 * np.pi * X) * np.sin(2 * np.pi * Y) / 2 + 0.5,
    np.exp(-(R - 0.3) ** 2 / 0.005),
    (waves - waves.min()) / np.ptp(waves),
    R / R.max(),
    np.sin(3 * np.pi * (X + Y)) ** 2,
    np.cos(12 * R) ** 2,
    np.tanh((X - 0.5 - 0.2 * np.sin(2 * np.pi * Y)) / 0.1) / 2 + 0.5,
    4 * X * (1 - X) * Y,
    X,
]
panels = [(name, z, {"ramp": name, "vmin": 0, "vmax": 1}) for name, z in zip(lf.RAMPS, fields, strict=True)]
panels.append(("center=0", 0.08 * np.sin(5 * X) * np.cos(4 * Y), {"center": 0}))
fig, axes = lf.subplots(3, 5, width=12.2, aspect=0.9, n=len(panels))
for ax, (title, z, kw) in zip(axes.flat, panels):
    lf.heatmap(ax, X, Y, z, **kw)
    ax.set(title=title, xticks=[0, 0.5, 1], yticks=[0, 0.5, 1], aspect="equal")
fig.supxlabel("$x$")
fig.supylabel("$y$")
lf.save(fig, out / "field")

names = ("gradient_draws", "field")
assert len({ax.collections[0].cmap.name for ax in axes.flat}) == axes.size and all((out / f"{name}.svg").stat().st_size > 0 for name in names)
print("wrote", *(out / f"{name}.svg" for name in names))
