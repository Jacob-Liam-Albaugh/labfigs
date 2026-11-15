"""Redraws thesis Fig. 6.3 and Figs. 14 and 16 of the neural information field filter paper on synthetic data."""
from pathlib import Path

import numpy as np

import labfigs as lf

rng = np.random.default_rng(3)
out = Path(__file__).parent
lf.use()

steps = np.linspace(0, 2e6, 4001)
early = slice(0, 201)


def wander(scale, chains=5, keep=0.98):
    noise = np.zeros((chains, steps.size))
    for i in range(1, steps.size):
        noise[:, i] = keep * noise[:, i - 1] + scale * rng.normal(size=chains)
    return noise


fig, axes = lf.subplots(2, 3, aspect=0.8, sharey=True)
for j, truth in enumerate((0.3, -1.0, 1.0)):
    start = rng.uniform(-0.4, 0.5)
    guides = {
        name: (truth + (start - truth) * np.exp(-steps / rate), 0.02 + 0.5 * np.exp(-2 * steps / rate))
        for name, rate in (("Non-relaxed SVI", 2.5e4), ("Relaxed SVI", 1.2e4))
    }
    chains = {
        name: truth + (start + rng.normal(0, 0.3, (5, 1)) - truth) * np.exp(-steps / rate) + wander(scale)
        for name, rate, scale in (("Relaxed SGLD", 2e5, 0.004), ("Relaxed preconditioned SGLD", 3e4, 0.008))
    }
    for ax, part, unit in ((axes[0, j], slice(None), 1e6), (axes[1, j], early, 1e5)):
        x = steps[part] / unit
        for name, (mid, width) in guides.items():
            lf.ribbon(ax, x, (mid - width)[part], mid[part], (mid + width)[part], label=name)
        for (name, chain), color in zip(chains.items(), ("C2", "C3")):
            lf.paths(ax, x, chain[:, part], color=color, alpha=0.6, level=None, lw=0.5, label=name)
        ax.axhline(truth, color=lf.TRUE, label="True")
        ax.set(yticks=[-1, 0, 1], ylim=(-1.3, 1.3), ylabel=rf"$k_{j + 1}/\bar{{k}}_{j + 1}$")
    axes[0, j].set(xticks=[0, 1, 2], xticklabels=["0", "$10^6$", r"$2\times10^6$"])
    axes[1, j].set(xticks=[0, 0.5, 1], xticklabels=["0", r"$5\times10^4$", "$10^5$"])
    lf.zoom(axes[0, j], axes[1, j], 0, 0.1)
fig.supxlabel("Iterations")
lf.legend_above(fig, ncols=3)
lf.save(fig, out / "fig_6_3")


def sweep(t, envelope, noise):
    clean = envelope * np.sin(2 * np.pi * (4 * t + 0.008 * t**2))
    draws = clean * (1 + 0.04 * rng.normal(size=(200, 1))) + 0.02 * envelope.max() * rng.normal(size=(200, t.size))
    return draws, 1.05 * clean + noise * (envelope + 0.03 * envelope.max()) * rng.normal(size=t.size)


def ramp_up(t, start, peak, power):
    return np.clip((t - start) / (peak - start), 0, 1) ** power * np.clip(1 - (t - peak) / 6, 0, 1) ** 2


def diamond(t, centre, reach, power):
    return np.clip(1 - np.abs(t - centre) / reach, 0, 1) ** power


def compare(ax, t, draws, measured, keep, label, color):
    lf.ribbon(ax, t[keep], *lf.quantiles(draws)[:, keep], color=color, lw=0.3, label=label)
    lf.signal(ax, t[keep], measured[keep], label="Measurement")


t = np.arange(0, 90, 0.01)
rows = (
    (r"$y_1$ (m)", 0.038 * ramp_up(t, 20, 80, 0.6), 0.02, 0.025, (75, 85)),
    (r"$y_2$ (m/s$^2$)", 50 * ramp_up(t, 20, 80, 2.5), 0.08, 50, (75, 85)),
    (r"$y_3$ (m)", 0.038 * diamond(t, 45, 38, 0.7), 0.02, 0.025, (40, 50)),
    (r"$y_4$ (m/s$^2$)", 50 * diamond(t, 45, 35, 2.5), 0.08, 50, (40, 50)),
)
fig, axes = lf.subplots(4, 2, aspect=0.36, sharey="row")
for (wide, detail), (name, envelope, noise, tick, (lo, hi)) in zip(axes, rows):
    draws, measured = sweep(t, envelope, noise)
    compare(wide, t, draws, measured, slice(None), "NSVI posterior", lf.POSTERIOR)
    compare(detail, t, draws, measured, (t >= lo) & (t <= hi), "NSVI posterior", lf.POSTERIOR)
    wide.set(xticks=np.arange(0, 91, 30), yticks=[-tick, 0, tick], ylabel=name)
    detail.set(xticks=np.arange(lo, hi + 1, 2))
fig.supxlabel("$t$ (s)")
lf.legend_above(fig)
lf.save(fig, out / "fig_14")

t = np.arange(5, 98, 0.01)
shaker = np.convolve(rng.normal(size=t.size), np.ones(25) / 25, "same") * ((t > 19) & (t < 80))
jump = np.where(t < 42, 0.3 * ramp_up(t, 15, 42, 2), (1 - 0.3 * (t - 42) / 46) * np.clip((92 - t) / 4, 0, 1))
rows = (
    (r"$x_1$ (m)", r"$a_1$ (m/s$^2$)", None, 0.005, 0.5),
    (r"$x_2$ (m)", r"$a_2$ (m/s$^2$)", jump, 0.025, 20),
    (r"$x_3$ (m)", r"$a_3$ (m/s$^2$)", ramp_up(t, 28, 85, 0.7), 0.025, 25),
    (r"$x_4$ (m)", r"$a_4$ (m/s$^2$)", diamond(t, 57, 40, 0.7), 0.025, 25),
)
fig, axes = lf.subplots(4, 2, aspect=0.36, sharex=True)
for pair, (x_name, a_name, envelope, x_tick, a_tick) in zip(axes, rows):
    for ax, name, tick, power in zip(pair, (x_name, a_name), (x_tick, a_tick), (1, 2.5)):
        if envelope is None:
            clean = 1.5 * tick * shaker
            draws = clean + 0.03 * tick * rng.normal(size=(200, t.size))
            measured = 1.2 * clean + 0.03 * tick * rng.normal(size=t.size)
        else:
            draws, measured = sweep(t, 1.1 * tick * envelope**power, 0.05)
        compare(ax, t, draws, measured, slice(None), "NSVI posterior predictive", lf.POSTERIOR)
        ax.set(xticks=np.arange(20, 101, 20), yticks=[-tick, 0, tick], ylabel=name)
fig.supxlabel("$t$ (s)")
lf.legend_above(fig)
lf.save(fig, out / "fig_16")

names = ("fig_6_3", "fig_14", "fig_16")
assert all((out / f"{name}.svg").stat().st_size > 0 for name in names)
print("wrote", *(out / f"{name}.svg" for name in names))
