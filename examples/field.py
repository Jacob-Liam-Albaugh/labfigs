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
fig, axes = lf.subplots(3, 5, width=13, aspect=0.75, sharex=True, sharey=True)
for ax, gradient in zip(axes.flat, (False, *lf.RAMPS, lf.POSTERIOR, lf.PREDICTIVE, "tab:blue")):
    lf.paths(ax, x, draws, gradient=gradient, label="Posterior draws")
    ax.plot(x, np.sin(2 * np.pi * x), color=lf.TRUE, ls="--", label="True")
    ax.set(title=f"gradient={gradient}", xticks=[0, 0.5, 1], yticks=[-2, -1, 0, 1, 2])
fig.supxlabel("$x$")
fig.supylabel("$u$")
lf.legend_above(fig)
lf.save(fig, out / "gradient_draws")
assert ["interval" in " ".join(ax.get_legend_handles_labels()[1]) for ax in axes.flat] == [True] + 14 * [False]

X, Y = np.meshgrid(np.linspace(0, 1, 80), np.linspace(0, 1, 80))
true = np.exp(-((X - 0.3) ** 2 + (Y - 0.6) ** 2) / 0.03) + 0.6 * np.exp(-((X - 0.7) ** 2 + (Y - 0.3) ** 2) / 0.05)
mean = true + 0.08 * np.sin(5 * X) * np.cos(4 * Y)
sensors = rng.uniform(0.1, 0.9, (2, 12))
spread = 0.02 + 0.3 * np.hypot(X[..., None] - sensors[0], Y[..., None] - sensors[1]).min(-1)
fig, axes = lf.subplots(2, 2, aspect=0.9, sharex=True, sharey=True)
value = {"ramp": "mako", "vmin": 0, "vmax": 1}
panels = [("True", true, value), ("Posterior mean", mean, value),
          ("Posterior sd", spread, {"ramp": "rocket", "vmin": 0}), ("Error", mean - true, {"center": 0})]
for ax, (title, z, kw) in zip(axes.flat, panels):
    lf.heatmap(ax, X, Y, z, **kw)
    lf.data(ax, *sensors, label="Sensors")
    ax.set(title=title, xticks=[0, 0.5, 1], yticks=[0, 0.5, 1], aspect="equal")
fig.supxlabel("$x$")
fig.supylabel("$y$")
lf.legend_above(fig)
lf.save(fig, out / "field")

fig, axes = lf.subplots(3, 4, width=9.75, aspect=0.9, sharex=True, sharey=True)
panels = [(name, true, value | {"ramp": name}) for name in lf.RAMPS] + [("center=0", mean - true, {"center": 0})]
for ax, (title, z, kw) in zip(axes.flat, panels):
    lf.heatmap(ax, X, Y, z, **kw)
    ax.set(title=title, xticks=[0, 0.5, 1], yticks=[0, 0.5, 1], aspect="equal")
fig.supxlabel("$x$")
fig.supylabel("$y$")
lf.save(fig, out / "field_palettes")

names = ("gradient_draws", "field", "field_palettes")
assert len({ax.collections[0].cmap.name for ax in axes.flat}) == axes.size and all((out / f"{name}.png").stat().st_size > 0 for name in names)
print("wrote", *(out / f"{name}.png" for name in names))
