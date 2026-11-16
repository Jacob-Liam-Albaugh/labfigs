"""Draws feasible operating regions with nested limit contours, on synthetic data."""
from pathlib import Path

import numpy as np

import labfigs as lf

out = Path(__file__).parent
lf.use()

limits = np.arange(0.1, 1.01, 0.1)
p, q = np.meshgrid(np.linspace(8, 33, 300), np.linspace(-2, 23, 300))
cases = (
    ("C2", [(14.5, 19.9), (30.5, 20.3), (31.5, 19), (31.7, 3.4), (14, 2.2), (13.8, 3)],
     [(14.1, 2.3), (15.3, 16.5), (20.5, 15), (29.9, 6.3), (27.3, 4.1)], (19, 10.7), 11, (22.8, 11.3)),
    ("C3", [(11.8, 18.6), (28.3, 19.2), (29, 18.3), (29, 2), (11.6, 1), (11.3, 2)],
     [(11.5, 4.8), (12.8, 17.6), (19.5, 18.3), (27, 11.6)], (22, 8.8), 12, (19.7, 9.9)),
    ("C4", [(11, 17.9), (27.3, 18.6), (28, 17.6), (28, 1.3), (10.7, 0.5), (10.5, 1.5)],
     [(15.7, 0.8), (19.2, 15.6), (21.6, 14.9), (27.5, 9.3), (27.1, 3.2), (25, 2)], (20, 13.3), 11.5, (19, 9)),
)
fig, axes = lf.subplots(1, 3, aspect=1.45, sharey=True)
for ax, letter, (color, outer, inner, centre, reach, point) in zip(axes, "abc", cases):
    shades = lf.ramp(len(limits), (lf.CRIMSON, color))
    lf.region(ax, outer, color, dashed=True, label="Perfect coordination")
    free = lf.region(ax, inner, color, label="No coordination")
    unbalance = np.hypot(p - centre[0], (q - centre[1]) / 1.2) / reach
    lf.contours(ax, p, q, unbalance, limits, shades, within=free)
    ax.plot(*point, "+", color=lf.TRUE)
    lf.level_key(ax, [f"{v:.1f}" for v in limits[::-1]], shades[::-1], r"VUF limit (\%):")
    lf.legend_above(ax, gap=0.24, ncols=1, frameon=False)
    lf.grid(ax)
    ax.set(aspect="equal", xlim=(8, 33), ylim=(-2, 23), xticks=np.arange(10, 31, 5), yticks=np.arange(0, 21, 5))
    ax.set_xlabel(f"$P$ (kW)\n({letter})")
axes[0].set_ylabel("$Q$ (kVAr)")
lf.save(fig, out / "feasible_regions", trim=False)

assert (out / "feasible_regions.svg").stat().st_size > 0
print("wrote", out / "feasible_regions.svg")
