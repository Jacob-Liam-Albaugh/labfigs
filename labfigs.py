import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.lines import Line2D

POSTERIOR = "crimson"
PREDICTIVE = "lightseagreen"
REFERENCE = "0.55"
TRUE = "black"
TEXT_WIDTH = 6.5


def use(tex=None, font_size=10):
    if tex is None:
        tex = shutil.which("latex") is not None
    sns.set_style("ticks")
    plt.rcParams.update({
        "text.usetex": tex,
        "font.family": "serif",
        "font.serif": ["CMU Serif", "Latin Modern Roman", "DejaVu Serif"],
        "mathtext.fontset": "cm",
        "font.size": font_size,
        "axes.labelsize": font_size,
        "xtick.labelsize": font_size,
        "ytick.labelsize": font_size,
        "legend.fontsize": font_size,
        "lines.linewidth": 0.8,
        "patch.linewidth": 0.5,
        "axes.linewidth": 0.6,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "figure.constrained_layout.use": True,
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
    })


def subplots(nrows=1, ncols=1, width=TEXT_WIDTH, aspect=0.62, **kw):
    height = nrows * (width / ncols) * aspect
    return plt.subplots(nrows, ncols, figsize=(width, height), **kw)


def band(ax, x, samples, level=0.95, color=POSTERIOR, alpha=0.5, **kw):
    tail = (1 - level) / 2
    lo, hi = np.quantile(samples, [tail, 1 - tail], axis=0)
    return ax.fill_between(x, lo, hi, color=color, alpha=alpha, **kw)


def paths(ax, x, samples, color=PREDICTIVE, alpha=0.1, **kw):
    return ax.plot(x, np.asarray(samples).T, color=color, alpha=alpha, **kw)


def split(ax, x, overshoot=0.12):
    return ax.axvline(x, -overshoot, 1 + overshoot, color=TRUE, ls="--", lw=0.8, clip_on=False)


def legend_above(ax, gap=0.18, **kw):
    unique = dict(zip(*reversed(ax.get_legend_handles_labels())))
    handles = [
        Line2D([], [], color=h.get_color(), ls=h.get_linestyle()) if isinstance(h, Line2D) else h
        for h in unique.values()
    ]
    return ax.legend(
        handles, unique.keys(), ncols=len(unique),
        loc="lower right", bbox_to_anchor=(1, 1 + gap), borderaxespad=0, **kw,
    )


def save(fig, path, trim=True, formats=("pdf", "png")):
    if trim:
        for ax in fig.axes:
            sns.despine(ax=ax, offset=5, trim=True)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    for ext in formats:
        fig.savefig(path.with_suffix(f".{ext}"))
    return path
