"""Shows the figure types of Hao's thesis that the other examples lack, on synthetic data (no inference is run)."""
from pathlib import Path

import numpy as np

import labfigs as lf

rng = np.random.default_rng(2)
out = Path(__file__).parent
lf.use()

beta = 10.0 ** np.arange(1, 6)
fig, axes = lf.subplots(2, 3, n=5, aspect=0.7)
for ax, name, truth in zip(axes, "abcde", (0.5, 1.0, 0.5, 0.75, 1.0)):
    draws = truth * (1 + 2 / beta + 0.4 * rng.normal(size=(500, 5)) / (beta / 10) ** 0.4)
    ax.axhspan(0.9 * truth, 1.1 * truth, color=lf.REFERENCE, alpha=0.3, lw=0, label="NUTS")
    lf.intervals(ax, beta, *lf.quantiles(draws), label="IFT")
    ax.axhline(truth, color=lf.TRUE, ls="--", label="True")
    ax.set(xscale="log", xticks=beta, yticks=[0, truth, 2 * truth], xlabel=r"$\beta$", ylabel=rf"${name}/\bar{{{name}}}$")
lf.legend_above(fig)
lf.save(fig, out / "intervals")

methods = ("Non-relaxed SVI", "Relaxed SVI", "Relaxed SGLD", "Relaxed PSGLD")
fig, axes = lf.subplots(2, 3, aspect=0.55)
for j, truth in enumerate((0.3, -1.0, 1.0)):
    for m, method in enumerate(methods):
        lf.density(axes[0, j], truth + 0.02 * rng.normal() + 0.01 * (m + 1) * rng.normal(size=400), label=method)
    lf.density(axes[1, j], truth + 0.03 * rng.normal(size=400), fill=True, color="C1")
    for ax in axes[:, j]:
        ax.axvline(truth, color=lf.TRUE, label="True")
        ax.set(xlabel=rf"$k_{j + 1}/\bar{{k}}_{j + 1}$", ylabel="")
fig.supylabel("Probability density")
lf.legend_above(fig, ncols=3)
lf.save(fig, out / "densities")

t = np.linspace(0, 12, 200)
fig, axes = lf.subplots(2, 3, aspect=0.7, sharex=True, sharey=True)
for i, ax in enumerate(axes.flat):
    state = 32 * np.sin(2 * np.pi * t / 12 + 0.4)
    ax.plot(t, 42 * np.sin(2 * np.pi * t / 12 + 0.8), color="C1", label="Measured input")
    lf.band(ax, t, state + (1 + i % 3) * rng.normal(size=(200, 1)), label="State posterior predictive")
    ax.plot(t, state + 1.5, color=lf.TRUE, ls="--", label="Measured output")
    ax.set_title(rf"$T_{{\mathrm{{ex}},{i + 1}}}$", loc="left", color="C1")
    ax.set_title(rf"$T_{{\mathrm{{in}},{i + 1}}}$", loc="right", color="C0")
    ax.set(xticks=[0, 6, 12], yticks=[-40, 0, 40])
for ax in axes.flat[[1, 5]]:
    lf.shade(ax)
fig.supxlabel("$t$ (hr)")
fig.supylabel(r"$T$ ($^\circ$C)")
lf.legend_above(fig)
lf.save(fig, out / "shaded_panels")

steps = np.linspace(0, 2, 300)
fig, axes = lf.subplots(1, 3, aspect=0.75, sharex=True)
for j, (ax, truth) in enumerate(zip(axes, (0.3, -1.0, 1.0))):
    settle = truth * (1 - np.exp(-steps / 0.2))
    width = 0.05 + 0.6 * np.exp(-steps / 0.1)
    lf.ribbon(ax, steps, settle - width, settle, settle + width, label="Relaxed SVI")
    chains = settle + 0.03 * rng.normal(size=(5, 300)).cumsum(1) * np.exp(-steps)
    lf.paths(ax, steps, chains, color="C1", alpha=0.7, level=None, label="Relaxed SGLD")
    ax.axhline(truth, color=lf.TRUE, label="True")
    ax.set(xticks=[0, 1, 2], yticks=[-1, 0, 1], ylim=(-1.3, 1.3), ylabel=rf"$k_{j + 1}/\bar{{k}}_{j + 1}$")
fig.supxlabel(r"Iterations ($\times 10^6$)")
lf.legend_above(fig)
lf.save(fig, out / "convergence")

names = ("intervals", "densities", "shaded_panels", "convergence")
assert all((out / f"{name}.svg").stat().st_size > 0 for name in names)
print("wrote", *(out / f"{name}.svg" for name in names))
