import re
import shutil
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.cm import ScalarMappable
from matplotlib.collections import LineCollection, QuadMesh
from matplotlib.container import ErrorbarContainer
from matplotlib.colors import LinearSegmentedColormap, Normalize, is_color_like, rgb_to_hsv, to_rgb
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import ConnectionPatch, Polygon
from matplotlib.text import Text
from matplotlib.ticker import FixedFormatter, MaxNLocator
from matplotlib.transforms import offset_copy

from labfigs_combos import COMBOS

POSTERIOR = "crimson"
PREDICTIVE = "lightseagreen"
REFERENCE = "0.55"
TRUE = "black"
deep = sns.color_palette("deep").as_hex()
SERIES = [POSTERIOR, PREDICTIVE, *(deep[i] for i in (0, 1, 2, 4, 5, 8))]
MUTED = ["#BC5A55", "#66909F", "#DBA3AD", "#BF6468", "#6B7883", "#9A7078", "#8795A2"]
HEAT = LinearSegmentedColormap.from_list(
    "heat", ["#E2E6BD", "#F1DE81", "#F6C971", "#EEAB65", "#DA8459", "#B9534C", "#8E063B"])
DIVERGING = LinearSegmentedColormap.from_list("diverging", [PREDICTIVE, "white", POSTERIOR])
PURPLE_TEAL = ["#9671bd", "#7e7e7e", "#77b5b6"]
# holds the lowest tenth flat so a surface's floor reads as one colour and only the peaks glow
SUNSET = LinearSegmentedColormap.from_list("sunset", list(zip(
    [0, 0.1, 0.28, 0.46, 0.64, 0.82, 1], ["#2d0b4e", "#2d0b4e", "#a11477", "#c1246b", "#e13661", "#fd4c55", "#ff6f4b"])))
NIGHT = {"centre": "#12302f", "edge": "#071414", "ink": "#f2f2f0", "grid": "#2c4a48"}
# pairs each colormap with the stretch (dark end, light end) that still reads as a line on white
STRETCH = {
    "Blues": (1.0, 0.35), "viridis": (0.0, 0.95), "magma": (0.15, 0.85), "plasma": (0.0, 0.9), "cividis": (0.0, 0.95),
    "rocket": (0.15, 0.85), "mako": (0.15, 0.85), "flare": (1.0, 0.0), "crest": (1.0, 0.0), "YlGnBu": (1.0, 0.3),
}
RAMPS = {"heat": (HEAT, 1.0, 0.4), "sunset": (SUNSET, 0.0, 1.0)} | {name.lower(): (plt.get_cmap(name), *ends) for name, ends in STRETCH.items()}
TEXT_WIDTH = 6.5
SPINE_OFFSET = 5
NARROW = 1.4


def use(tex=None, font_size=10, series=SERIES, font="serif", dark=False):
    if tex is None:
        tex = font == "serif" and shutil.which("latex") is not None
    sns.set_style("ticks")
    if dark:
        ink = dict.fromkeys(("text.color", "axes.labelcolor", "axes.edgecolor", "xtick.color", "ytick.color"), NIGHT["ink"])
        plt.rcParams.update(ink | {
            "figure.facecolor": NIGHT["edge"], "savefig.facecolor": NIGHT["edge"], "axes.facecolor": "none",
            "grid.color": NIGHT["grid"]})
    plt.rcParams.update({
        "text.usetex": tex,
        "axes.prop_cycle": plt.cycler(color=series),
        "font.family": {"mono": "monospace"}.get(font, font),
        "font.monospace": ["Courier New", "Courier", "Computer Modern Typewriter"],
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


def subplots(nrows=1, ncols=1, width=TEXT_WIDTH, aspect=None, n=None, **kw):
    # keeps panels from going flat as columns are added
    aspect = aspect or 0.62 * max(ncols, 3) / 3
    figsize = (width, nrows * (width / ncols) * aspect)
    if n is None:
        fig, axes = plt.subplots(nrows, ncols, figsize=figsize, **kw)
        backdrop(fig)
        return fig, axes
    fig = plt.figure(figsize=figsize, **kw)
    backdrop(fig)
    grid = fig.add_gridspec(nrows, 2 * ncols)
    indent = nrows * ncols - n
    spots = [(i // ncols, 2 * (i % ncols) + indent * (i // ncols == nrows - 1)) for i in range(n)]
    return fig, np.array([fig.add_subplot(grid[row, col:col + 2]) for row, col in spots])


def is_dark():
    return plt.rcParams["figure.facecolor"] == NIGHT["edge"]


def backdrop(fig):
    if not is_dark():
        return
    y, x = np.mgrid[-1:1:300j, -1:1:400j]
    glow = LinearSegmentedColormap.from_list("", [NIGHT["centre"], NIGHT["edge"]])
    ax = fig.add_axes([0, 0, 1, 1], zorder=-10)
    ax.imshow(np.hypot(x, y), cmap=glow, vmin=0, vmax=2 ** 0.5, extent=(0, 1, 0, 1), aspect="auto")
    ax.axis("off")


def darker(color, by=0.7):
    return tuple(by * channel for channel in to_rgb(color))


def low_to_high(ramp):
    cmap, dark, light = shades(ramp)
    return cmap if (dark > light) != is_dark() else cmap.reversed()


def shades(name):
    if isinstance(name, str) and name in RAMPS:
        return RAMPS[name]
    if is_color_like(name):
        return LinearSegmentedColormap.from_list("", ["white", name, "black"]), 0.9, 0.2
    ends = (0.0, 1.0) if luma(name[0]) < luma(name[-1]) else (1.0, 0.0)
    return LinearSegmentedColormap.from_list("", name), *ends


def luma(color):
    return np.dot(to_rgb(color), [0.299, 0.587, 0.114])


def hue_arc(colours):
    hsv = rgb_to_hsv([to_rgb(colour) for colour in colours])
    # leaves greys and near-blacks out, since their hue is noise and a neutral goes with anything
    hues = np.sort(360 * hsv[(hsv[:, 1] > 0.1) & (hsv[:, 2] > 0.15), 0])
    return 0.0 if len(hues) < 2 else 360 - np.diff(np.append(hues, hues[0] + 360)).max()


def vividness(colours):
    return np.ptp([to_rgb(colour) for colour in colours], axis=1).max()


def combos(size=None, vivid=1.0, arc=(0, 360)):
    return {
        key: colours for key, colours in COMBOS.items()
        if size in (None, len(colours)) and vividness(colours) <= vivid and arc[0] <= hue_arc(colours) <= arc[1]}


def swatches(ax, sets):
    for row, colours in enumerate(sets.values()):
        n = len(colours)
        ax.barh(row, np.full(n, 1 / n), left=np.arange(n) / n, height=0.8, color=colours, edgecolor="0.85", lw=0.3)
    ax.set(yticks=range(len(sets)), yticklabels=[str(key).replace("_", " ") for key in sets], xticks=[])
    ax.set(xlim=(0, 1), ylim=(len(sets) - 0.4, -0.6))
    ax.tick_params(length=0)
    sns.despine(ax=ax, left=True, bottom=True)


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


def points(ax, x, y, color="C0", **kw):
    return ax.scatter(x, y, s=22, facecolor=color, edgecolor=darker(color), lw=0.75, zorder=3, **kw)


def data(ax, x, y, **kw):
    return ax.plot(x, y, "o", color=TRUE, ms=2.5, zorder=3, **kw)


def trace(ax, x, y, **kw):
    return ax.plot(x, y, **{"marker": "o", "ms": 3, **kw})[0]


def dodge(n, width=5):
    return (np.arange(n) - (n - 1) / 2) * width


def intervals(ax, x, lo, mid, hi, shift=0.0, connect=False, **kw):
    # shifts in points, so one dodge works on any axis, numeric or log
    bars = ax.errorbar(x, mid, [mid - lo, hi - mid], fmt="o-" if connect else "o", ms=3, **kw)
    for artist in (bars[0], *bars[1], *bars[2]):
        artist.set_transform(offset_copy(ax.transData, ax.figure, x=shift, units="points"))
    return bars


def marks(ax, x, y, **kw):
    return ax.plot(x, y, **{"ls": "", "marker": "_", "ms": 16, "mew": 1, "color": TRUE, "zorder": 3, **kw})


def paths(ax, x, samples, color=PREDICTIVE, alpha=None, draws=100, level=None, gradient=False, **kw):
    samples = np.asarray(samples)
    if level:
        band(ax, x, samples, level, color=REFERENCE, alpha=0.3, lw=0, label=f"{100 * level:g}% interval")
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
    # keeps the SVG small: one path per segment would run to tens of megabytes
    lines = LineCollection(
        segments[central_last], array=shade, cmap=cmap, clim=(0, 1), alpha=alpha or 0.4, rasterized=True, **kw)
    ax.add_collection(lines)
    ax.autoscale_view()
    return lines


def heatmap(ax, x, y, z, ramp="heat", center=None, label=None, **kw):
    cmap = low_to_high(ramp)
    if center is not None:
        reach = np.nanmax(np.abs(z - center))
        cmap, kw = DIVERGING, {"vmin": center - reach, "vmax": center + reach, **kw}
    mesh = ax.pcolormesh(x, y, z, cmap=cmap, shading="auto", rasterized=True, **kw)
    ax.figure.colorbar(mesh, ax=ax, label=label, pad=0.03).outline.set_visible(False)
    return mesh


def surface(ax, x, y, z, ramp="heat", label=None, **kw):
    cmap, norm = low_to_high(ramp), Normalize(np.nanmin(z), np.nanmax(z))
    # colours each facet by its highest corner, so the peaks reach the end of the ramp
    peak = np.maximum.reduce([z[:-1, :-1], z[1:, :-1], z[:-1, 1:], z[1:, 1:]])
    faces = ax.plot_surface(
        x, y, z, facecolors=cmap(norm(peak)), lw=0, shade=False, rstride=1, cstride=1, rasterized=True, **kw)
    ax.figure.colorbar(ScalarMappable(norm, cmap), ax=ax, label=label, shrink=0.6, pad=0.12).outline.set_visible(False)
    ax.set_facecolor("none")
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.set(facecolor="none", edgecolor=plt.rcParams["grid.color"])
        axis._axinfo["grid"].update(color=plt.rcParams["grid.color"], linewidth=0.4)
    return faces


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


def tag(fig, text):
    return fig.suptitle(text, x=0.01, ha="left", size=plt.rcParams["font.size"])


def percent(text):
    if plt.rcParams["text.usetex"]:
        return re.sub(r"(?<!\\)%", r"\\%", text)
    return "$".join(part if i % 2 else part.replace(r"\%", "%") for i, part in enumerate(text.split("$")))


def loose(ax):
    if ax.images or any(isinstance(c, QuadMesh) for c in ax.collections):
        return []
    axes = {name: getattr(ax, f"{name}axis") for name in "xy"}
    return [name for name, axis in axes.items() if isinstance(axis.get_major_locator(), MaxNLocator) and axis.get_scale() == "linear"]


def cover(ax):
    for name in loose(ax):
        axis = getattr(ax, f"{name}axis")
        siblings = getattr(ax, f"get_shared_{name}_axes")().get_siblings(ax)
        lo, hi = np.transpose([getattr(s, f"{name}axis").get_data_interval() for s in siblings])
        lo, hi, view = lo.min(), hi.max(), axis.get_view_interval()
        if not (np.isfinite([lo, hi]).all() and view[0] < view[1]):
            continue
        if not getattr(ax, f"get_autoscale{name}_on")():
            lo, hi = view
        step = np.diff(axis.get_major_locator().tick_values(*view))[0]
        lo, hi = max(lo, view[0]) / step, min(hi, view[1]) / step
        # lets data pass the last tick by a line width before adding a whole step for it
        slack = 0.03 * (hi - lo)
        axis.set_ticks(np.arange(np.floor(lo + slack), np.ceil(hi - slack) + 1) * step)


def overlaps(fig):
    # places legend text at the figure's own dpi, which the SVG writer leaves at 72
    fig.draw_without_rendering()
    hidden = {id(label) for ax in fig.axes for axis in (ax.xaxis, ax.yaxis)
              for tick in (*axis.get_major_ticks(), *axis.get_minor_ticks())
              if not min(axis.get_view_interval()) <= tick.get_loc() <= max(axis.get_view_interval())
              for label in (tick.label1, tick.label2)}
    # skips slanted text, whose upright box covers more than its ink
    texts = [t for t in fig.findobj(Text) if t.get_visible() and t.get_text().strip() and id(t) not in hidden and t.get_rotation() % 90 == 0]
    boxes = [t.get_window_extent() for t in texts]
    return [(a.get_text(), b.get_text()) for i, (a, box) in enumerate(zip(texts, boxes))
            for b, other in zip(texts[i + 1:], boxes[i + 1:]) if box.overlaps(other)]


def check(fig, name):
    pairs = overlaps(fig)
    if pairs:
        warnings.warn(f"{name}: {len(pairs)} pairs of labels overlap, first {pairs[0][0]!r} and {pairs[0][1]!r} "
                      "(checklist 6): fewer ticks, fewer columns, or more room", stacklevel=3)
    panels = [ax for ax in fig.axes if ax.get_label() != "<colorbar>" and ax.axison and ax.name == "rectilinear"]
    spans = [ax.get_subplotspec() for ax in panels if ax.get_subplotspec() and len(ax.get_xticks())]
    width = min((fig.get_figwidth() * len(s.colspan) / s.get_gridspec().ncols for s in spans), default=NARROW)
    if width < NARROW:
        warnings.warn(f"{name}: panels are {width:.1f} in wide (checklist 6): fewer columns, more rows, or a wider page", stacklevel=3)
    for ax in panels:
        bars = [np.array(c.lines[2][0].get_segments())[:, :, 1] for c in ax.containers if isinstance(c, ErrorbarContainer)]
        if not bars or len({len(b) for b in bars}) > 1 or len(bars[0]) < 4 or ax.get_yscale() != "linear":
            continue
        ends = np.concatenate(bars, axis=1)
        extreme = np.abs(ends.mean(1) - np.median(ends)).argmax()
        apart, rest = ends[extreme], np.delete(ends, extreme, 0)
        if (apart.min() > rest.max() or apart.max() < rest.min()) and np.ptp(rest) < np.ptp(ends) / 3:
            warnings.warn(f"{name}: one x position sets the range of {ax.get_ylabel()!r} (checklist 13): "
                          "a log axis, or that position in its own panel", stacklevel=3)


def save(fig, path, trim=True, formats=("svg",)):
    path = Path(path)
    for text in fig.findobj(Text):
        text.set_text(percent(text.get_text()))
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            if isinstance(axis.get_major_formatter(), FixedFormatter):
                axis.get_major_formatter().seq = [percent(label) for label in axis.get_major_formatter().seq]
    panels = [ax for ax in fig.axes if trim and ax.get_label() != "<colorbar>" and ax.name == "rectilinear" and ax.axison]
    if any(loose(ax) for ax in panels):
        # settles the layout first, so the tick count fits the final panel size
        fig.draw_without_rendering()
    for ax in panels:
        # widens each automatic axis to the ticks enclosing its data, so a trimmed spine never stops short of it
        cover(ax)
        sns.despine(ax=ax, offset=SPINE_OFFSET, trim=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    for ext in formats:
        fig.savefig(path.with_suffix(f".{ext}"))
    check(fig, path.name)
    return path
