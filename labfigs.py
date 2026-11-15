import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap, is_color_like
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import ConnectionPatch, Polygon
from matplotlib.transforms import offset_copy

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
STRETCH = {
    "Blues": (1.0, 0.35), "viridis": (0.0, 0.95), "magma": (0.15, 0.85), "plasma": (0.0, 0.9), "cividis": (0.0, 0.95),
    "rocket": (0.15, 0.85), "mako": (0.15, 0.85), "flare": (1.0, 0.0), "crest": (1.0, 0.0), "YlGnBu": (1.0, 0.3),
}
RAMPS = {"heat": (HEAT, 1.0, 0.4)} | {name.lower(): (plt.get_cmap(name), *ends) for name, ends in STRETCH.items()}
TEXT_WIDTH = 6.5
SPINE_OFFSET = 5


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


def subplots(nrows=1, ncols=1, width=TEXT_WIDTH, aspect=0.62, n=None, **kw):
    figsize = (width, nrows * (width / ncols) * aspect)
    if n is None:
        return plt.subplots(nrows, ncols, figsize=figsize, **kw)
    fig = plt.figure(figsize=figsize, **kw)
    grid = fig.add_gridspec(nrows, 2 * ncols)
    indent = nrows * ncols - n
    spots = [(i // ncols, 2 * (i % ncols) + indent * (i // ncols == nrows - 1)) for i in range(n)]
    return fig, np.array([fig.add_subplot(grid[row, col:col + 2]) for row, col in spots])


def shades(name):
    if isinstance(name, str) and name in RAMPS:
        return RAMPS[name]
    if not is_color_like(name):
        return LinearSegmentedColormap.from_list("", name), 0.0, 1.0
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
    cmap, dark, light = shades(ramp)
    cmap = cmap if dark > light else cmap.reversed()
    if center is not None:
        reach = np.nanmax(np.abs(z - center))
        cmap, kw = DIVERGING, {"vmin": center - reach, "vmax": center + reach, **kw}
    mesh = ax.pcolormesh(x, y, z, cmap=cmap, shading="auto", rasterized=True, **kw)
    ax.figure.colorbar(mesh, ax=ax, label=label, pad=0.03).outline.set_visible(False)
    return mesh


def density(ax, samples, fill=False, **kw):
    return sns.kdeplot(x=np.asarray(samples), ax=ax, fill=fill, **kw)


def shade(ax):
    ax.set_facecolor("0.85")


def region(ax, corners, color, dashed=False, **kw):
    style = {"ls": "--", "lw": 0.8} if dashed else {"lw": 1.6}
    return ax.add_patch(Polygon(corners, fill=False, ec=color, **style, **kw))


def contours(ax, x, y, z, levels, colors, within=None, **kw):
    lines = ax.contour(x, y, z, levels=levels, colors=colors, linewidths=0.6, **kw)
    lines.set_clip_path(within)
    return lines


def level_key(ax, labels, colors, title=None):
    for i, (label, color) in enumerate(zip(labels, colors)):
        ax.annotate(
            label, ((i + 0.5) / len(labels), 1), xycoords="axes fraction", xytext=(0, 8), textcoords="offset points",
            ha="center", size="xx-small", bbox={"boxstyle": "round,pad=0.12", "fc": "none", "ec": color, "lw": 0.8})
    if title:
        ax.annotate(title, (1, 1), xycoords="axes fraction", xytext=(0, 20), textcoords="offset points", ha="right")


def grid(ax):
    ax.minorticks_on()
    ax.tick_params(which="minor", length=0)
    ax.grid(which="major", color=REFERENCE, lw=0.4, alpha=0.4)
    ax.grid(which="minor", color=REFERENCE, lw=0.2, alpha=0.3)
    ax.set_axisbelow(True)


def signal(ax, x, y, color=SERIES[2], **kw):
    return ax.plot(x, y, color=color, ls=(0, (3, 3)), lw=0.3, **kw)


def zoom(wide, detail, x0, x1, room=0.12):
    fig, rc = wide.figure, plt.rcParams
    fig.get_layout_engine().set(hspace=room)
    labels = SPINE_OFFSET + rc["xtick.major.size"] + rc["xtick.major.pad"] + 1.4 * rc["font.size"]
    below_labels = offset_copy(wide.get_xaxis_transform(), fig, y=-labels, units="points")
    for start, end in zip((x0, x1), detail.dataLim.intervalx):
        fig.add_artist(ConnectionPatch(
            (start, 0), (end, 1), below_labels, detail.get_xaxis_transform(), color=TRUE, ls="--", lw=0.5))


def split(ax, x, overshoot=0.12):
    return ax.axvline(x, -overshoot, 1 + overshoot, color=TRUE, ls="--", lw=0.8, clip_on=False)


def legend_above(target, gap=0.18, ncols=None, **kw):
    axes = target.axes if isinstance(target, Figure) else [target]
    unique = {label: h for ax in axes for h, label in zip(*ax.get_legend_handles_labels())}
    handles = [
        Line2D([], [], color=h.get_color(), ls=h.get_linestyle(), marker=h.get_marker(), ms=h.get_markersize())
        if isinstance(h, Line2D) else h
        for h in unique.values()
    ]
    if isinstance(target, Figure):
        return target.legend(handles, unique.keys(), ncols=ncols or len(unique), loc="outside upper right", **kw)
    return target.legend(
        handles, unique.keys(), ncols=ncols or len(unique),
        loc="lower right", bbox_to_anchor=(1, 1 + gap), borderaxespad=0, **kw,
    )


def save(fig, path, trim=True, formats=("pdf", "png")):
    if trim:
        for ax in fig.axes:
            if ax.get_label() != "<colorbar>":
                sns.despine(ax=ax, offset=SPINE_OFFSET, trim=True)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    for ext in formats:
        fig.savefig(path.with_suffix(f".{ext}"))
    return path
