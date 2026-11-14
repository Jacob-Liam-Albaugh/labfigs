import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

POSTERIOR = "crimson"
PREDICTIVE = "lightseagreen"
REFERENCE = "0.55"
TRUE = "black"
SERIES = [POSTERIOR, PREDICTIVE, "tab:blue", "tab:orange", "tab:green", "tab:purple", "tab:brown", "tab:olive"]
MUTED = ["#BC5A55", "#66909F", "#DBA3AD", "#BF6468", "#6B7883", "#9A7078", "#8795A2"]
HEAT = LinearSegmentedColormap.from_list(
    "heat", ["#E2E6BD", "#F1DE81", "#F6C971", "#EEAB65", "#DA8459", "#B9534C", "#8E063B"])
DIVERGING = LinearSegmentedColormap.from_list("diverging", [PREDICTIVE, "white", POSTERIOR])
# pairs each colormap with the stretch (dark end, light end) that still reads as a line on white
RAMPS = {"heat": (HEAT, 1.0, 0.4), "blues": (plt.get_cmap("Blues"), 1.0, 0.35), "viridis": (plt.get_cmap("viridis"), 0.0, 0.95)}
TEXT_WIDTH = 6.5


def use(tex=None, font_size=10, series=SERIES):
    if tex is None:
        tex = shutil.which("latex") is not None
    sns.set_style("ticks")
    plt.rcParams.update({
        "text.usetex": tex,
        "axes.prop_cycle": plt.cycler(color=series),
        "font.family": "serif",
        "font.serif": ["CMU Serif", "Latin Modern Roman", "DejaVu Serif"],
        "mathtext.fontset": "cm",
        "font.size": font_size,
        "axes.labelsize": font_size,
        "axes.titlesize": font_size,
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


def shades(name):
    if isinstance(name, str) and name in RAMPS:
        return RAMPS[name]
    return LinearSegmentedColormap.from_list("", ["white", name, "black"]), 0.9, 0.2


def ramp(n, name="heat"):
    cmap, dark, light = shades(name)
    return cmap(np.linspace(dark, light, n))


def quantiles(samples, level=0.95):
    tail = (1 - level) / 2
    return np.nanquantile(samples, [tail, 0.5, 1 - tail], axis=0)


def band(ax, x, samples, level=0.95, color=POSTERIOR, alpha=0.5, **kw):
    lo, _, hi = quantiles(samples, level)
    return ax.fill_between(x, lo, hi, color=color, alpha=alpha, **kw)


def ribbon(ax, x, lo, mid, hi, color=None, alpha=0.25, **kw):
    line, = ax.plot(x, mid, color=color, **kw)
    ax.fill_between(x, lo, hi, color=line.get_color(), alpha=alpha, lw=0)
    return line


def data(ax, x, y, **kw):
    return ax.plot(x, y, "o", color=TRUE, ms=2.5, zorder=3, **kw)


def trace(ax, x, y, **kw):
    return ax.plot(x, y, "o-", ms=3, **kw)[0]


def dodge(n, width=0.17):
    return (np.arange(n) - (n - 1) / 2) * width


def intervals(ax, x, lo, mid, hi, shift=0.0, connect=False, **kw):
    fmt = "o-" if connect else "o"
    return ax.errorbar(np.asarray(x) + shift, mid, [mid - lo, hi - mid], fmt=fmt, ms=3, **kw)


def paths(ax, x, samples, color=PREDICTIVE, alpha=None, draws=100, level="auto", gradient=False, **kw):
    samples = np.asarray(samples)
    if level == "auto":
        level = None if gradient else 0.95
    if level:
        percent = r"\%" if plt.rcParams["text.usetex"] else "%"
        band(ax, x, samples, level, color=REFERENCE, alpha=0.3, lw=0, label=f"{100 * level:g}{percent} interval")
    keep = np.linspace(0, len(samples) - 1, min(draws, len(samples))).astype(int)
    if not gradient:
        return ax.plot(x, samples[keep].T, color=color, alpha=alpha or 0.1, **kw)
    cmap, dark, light = shades("heat" if gradient is True else gradient)
    sigmas = np.abs(samples[keep] - samples.mean(0)) / (samples.std(0) + np.finfo(float).tiny)
    points = np.stack([np.broadcast_to(x, sigmas.shape), samples[keep]], -1)
    segments = np.stack([points[:, :-1], points[:, 1:]], 2).reshape(-1, 2, 2)
    ax.plot([], [], color=cmap(dark + (light - dark) / 3), label=kw.pop("label", None))
    depth = np.minimum((sigmas[:, :-1] + sigmas[:, 1:]).ravel() // 2, 2) / 3 + 1 / 3
    central_last = np.argsort(-depth)
    shade = dark + (light - dark) * depth[central_last]
    lines = LineCollection(segments[central_last], array=shade, cmap=cmap, clim=(0, 1), alpha=alpha or 0.4, **kw)
    ax.add_collection(lines)
    ax.autoscale_view()
    return lines


def heatmap(ax, x, y, z, ramp="heat", center=None, label=None, **kw):
    cmap = shades(ramp)[0]
    if center is not None:
        reach = np.nanmax(np.abs(z - center))
        cmap, kw = DIVERGING, {"vmin": center - reach, "vmax": center + reach, **kw}
    mesh = ax.pcolormesh(x, y, z, cmap=cmap, shading="auto", rasterized=True, **kw)
    ax.figure.colorbar(mesh, ax=ax, label=label, pad=0.03).outline.set_visible(False)
    return mesh


def split(ax, x, overshoot=0.12):
    return ax.axvline(x, -overshoot, 1 + overshoot, color=TRUE, ls="--", lw=0.8, clip_on=False)


def legend_above(target, gap=0.18, **kw):
    axes = target.axes if isinstance(target, Figure) else [target]
    unique = {label: h for ax in axes for h, label in zip(*ax.get_legend_handles_labels())}
    handles = [
        Line2D([], [], color=h.get_color(), ls=h.get_linestyle(), marker=h.get_marker(), ms=h.get_markersize())
        if isinstance(h, Line2D) else h
        for h in unique.values()
    ]
    if isinstance(target, Figure):
        return target.legend(handles, unique.keys(), ncols=len(unique), loc="outside upper right", **kw)
    return target.legend(
        handles, unique.keys(), ncols=len(unique),
        loc="lower right", bbox_to_anchor=(1, 1 + gap), borderaxespad=0, **kw,
    )


def save(fig, path, trim=True, formats=("pdf", "png")):
    if trim:
        for ax in fig.axes:
            if ax.get_label() != "<colorbar>":
                sns.despine(ax=ax, offset=5, trim=True)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    for ext in formats:
        fig.savefig(path.with_suffix(f".{ext}"))
    return path
