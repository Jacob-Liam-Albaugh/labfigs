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
from matplotlib.colors import LinearSegmentedColormap, ListedColormap, Normalize, get_named_colors_mapping, is_color_like, rgb_to_hsv, to_hex, to_rgb
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import ConnectionPatch, Polygon
from matplotlib.text import Text
from matplotlib.ticker import FixedFormatter, MaxNLocator
from matplotlib.transforms import offset_copy

from labfigs_combos import COMBOS, KINDS

CRIMSON = "crimson"
TEAL = "lightseagreen"
# points matplotlib's "teal" at the house teal, so the name is one colour as a line and as a ramp
get_named_colors_mapping()["teal"] = to_hex(TEAL)
REFERENCE = "0.55"
TRUE = "black"
CYCLE = [CRIMSON, TEAL, *(COMBOS["seaborn_deep"][i] for i in (0, 1, 2, 4, 5, 8))]
HEAT = LinearSegmentedColormap.from_list(
    "heat", ["#E2E6BD", "#F1DE81", "#F6C971", "#EEAB65", "#DA8459", "#B9534C", "#8E063B"])
DIVERGING = LinearSegmentedColormap.from_list("diverging", [TEAL, "white", CRIMSON])
# holds the lowest tenth flat so a surface's floor reads as one colour and only the peaks glow
SUNSET = LinearSegmentedColormap.from_list("sunset", list(zip(
    [0, 0.1, 0.28, 0.46, 0.64, 0.82, 1], ["#2d0b4e", "#2d0b4e", "#a11477", "#c1246b", "#e13661", "#fd4c55", "#ff6f4b"])))
NIGHT = {"centre": "#12302f", "edge": "#071414", "ink": "#f2f2f0", "grid": "#2c4a48"}
def tint(colour):
    return LinearSegmentedColormap.from_list(str(colour), ["white", colour, "black"]), 0.9, 0.2


# pairs each colormap with the stretch (dark end, light end) that still reads as a line on white
STRETCH = {
    "Blues": (1.0, 0.35), "viridis": (0.0, 0.95), "magma": (0.15, 0.85), "plasma": (0.0, 0.9), "cividis": (0.0, 0.95),
    "rocket": (0.15, 0.85), "mako": (0.15, 0.85), "flare": (1.0, 0.0), "crest": (1.0, 0.0), "YlGnBu": (1.0, 0.3),
}
RAMPS = {"crimson": tint(CRIMSON), "teal": tint(TEAL), "heat": (HEAT, 1.0, 0.4), "sunset": (SUNSET, 0.0, 1.0)} | {name.lower(): (plt.get_cmap(name), *ends) for name, ends in STRETCH.items()}
TEXT_WIDTH = 6.5
SPINE_OFFSET = 5
NARROW = 1.4
FLAT = 0.5
ROOMY = 5.0
ACROSS = 3


def use(tex=None, font_size=10, series=CYCLE, font="serif", dark=False):
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
        "axes.prop_cycle": plt.cycler(color=COMBOS[series] if isinstance(series, str) else series),
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
        fig.panel_aspect = aspect
        return fig, axes
    fig = plt.figure(figsize=figsize, **kw)
    backdrop(fig)
    fig.panel_aspect = aspect
    grid = fig.add_gridspec(nrows, 2 * ncols)
    indent = nrows * ncols - n
    spots = [(i // ncols, 2 * (i % ncols) + indent * (i // ncols == nrows - 1)) for i in range(n)]
    return fig, np.array([fig.add_subplot(grid[row, col:col + 2]) for row, col in spots])


def cases(names, quantities, sharey=False, aspect=None, **kw):
    """Makes one panel per case and quantity, indexed [case, quantity]: cases side by side up to ACROSS, stacked as rows beyond."""
    if len(names) > ACROSS:
        fig, axes = subplots(len(names), len(quantities), aspect=aspect or 0.36, sharex="col", sharey="col" if sharey else False, squeeze=False, **kw)
        across, down = quantities, names
    else:
        fig, grid = subplots(len(quantities), len(names), aspect=aspect or 0.8, sharey="row" if sharey else False, squeeze=False, **kw)
        axes, across, down = grid.T, names, quantities
    for ax, label in zip(fig.axes[:len(across)], across):
        ax.set_title(label)
    for ax, label in zip(fig.axes[::len(across)], down):
        ax.set_ylabel(label)
    return fig, axes


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
        return tint(name)
    if isinstance(name, (str, int)):
        # orders a set of separate colours dark to light, so it shades like a ramp
        name = sorted(COMBOS[name], key=luma) if discrete(name) else COMBOS[name]
    ends = (0.0, 1.0) if luma(name[0]) < luma(name[-1]) else (1.0, 0.0)
    return LinearSegmentedColormap.from_list("", name), *ends


def discrete(name):
    """Tells a set of separate colours (a list, a Wada number, a series scheme) from a ramp or a single colour."""
    return not is_color_like(name) and (not isinstance(name, str) or name in KINDS["categorical"])


def luma(color):
    return np.dot(to_rgb(color), [0.299, 0.587, 0.114])


def hue_arc(colours):
    hsv = rgb_to_hsv([to_rgb(colour) for colour in colours])
    # leaves greys and near-blacks out, since their hue is noise and a neutral goes with anything
    hues = np.sort(360 * hsv[(hsv[:, 1] > 0.1) & (hsv[:, 2] > 0.15), 0])
    return 0.0 if len(hues) < 2 else 360 - np.diff(np.append(hues, hues[0] + 360)).max()


def vividness(colours):
    return np.ptp([to_rgb(colour) for colour in colours], axis=1).max()


def kind_of(key):
    named = next((kind for kind, names in KINDS.items() if key in names), "sequential")
    return named if isinstance(key, str) else "combination"


def combos(size=None, vivid=1.0, arc=(0, 360), kind=None):
    return {
        key: colours for key, colours in COMBOS.items()
        if size in (None, len(colours)) and vividness(colours) <= vivid and arc[0] <= hue_arc(colours) <= arc[1]
        and kind in (None, kind_of(key))}


def swatches(ax, sets):
    for row, colours in enumerate(sets.values()):
        n = len(colours)
        # edges a long set in its own colours, so a gradient shows no seams or stripes
        ax.barh(row, np.full(n, 1 / n), left=np.arange(n) / n, height=0.8, color=colours, edgecolor="0.85" if n < 20 else colours, lw=0.3)
    ax.set(yticks=range(len(sets)), yticklabels=[str(key).replace("_", " ") for key in sets], xticks=[])
    ax.set(xlim=(0, 1), ylim=(len(sets) - 0.4, -0.6))
    ax.tick_params(length=0)
    # blanks the spines instead of hiding them, since the trim in save would show hidden ones again
    ax.spines[:].set_color("none")


def ramp(n, name="heat"):
    cmap, dark, light = shades(name)
    return cmap(np.linspace(dark, light, n))


def steps(name, n=3):
    """Gives n colours from the centre out: a colour set's own colours, darkest first, or a ramp's run from a third in."""
    cmap, dark, light = shades(name)
    own = len(COMBOS[name] if isinstance(name, (str, int)) else name) if discrete(name) else 0
    # lands on a set's own colours when it has enough of them, and blends between them when it has too few
    stops = np.linspace(0, own - 1, n).astype(int) / (own - 1) if own >= n > 1 else np.linspace(0 if own else 1 / n, 1, n)
    return cmap(dark + (light - dark) * stops)


def quantiles(samples, level=0.95):
    tail = (1 - level) / 2
    return np.nanquantile(samples, [tail, 0.5, 1 - tail], axis=0)


def band(ax, x, samples, level=0.95, color=CRIMSON, alpha=0.5, **kw):
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


def paths(ax, x, samples, color=TEAL, alpha=None, draws=None, level=None, gradient=False, **kw):
    samples = np.asarray(samples)
    # thins the draws and their lines in a small panel, where a hundred merge into one smear
    room = np.clip(ax.get_position().width * ax.figure.get_figwidth() / ROOMY, 0.25, 1)
    draws = draws or round(100 * room)
    if "linewidth" not in kw:
        kw.setdefault("lw", plt.rcParams["lines.linewidth"] * room ** 0.5)
    if level:
        band(ax, x, samples, level, color=REFERENCE, alpha=0.3, lw=0, label=f"{100 * level:g}% interval")
    keep = np.linspace(0, len(samples) - 1, min(draws, len(samples))).astype(int)
    if not gradient:
        return ax.plot(x, samples[keep].T, color=color, alpha=alpha or 0.1 / room, **kw)
    colours = steps("heat" if gradient is True else gradient)
    sigmas = np.abs(samples[keep] - samples.mean(0)) / (samples.std(0) + np.finfo(float).tiny)
    points = np.stack([np.broadcast_to(x, sigmas.shape), samples[keep]], -1)
    segments = np.stack([points[:, :-1], points[:, 1:]], 2).reshape(-1, 2, 2)
    ax.plot([], [], color=colours[0], label=kw.pop("label", None))
    depth = np.minimum((sigmas[:, :-1] + sigmas[:, 1:]).ravel() // 2, 2)
    central_last = np.argsort(-depth)
    # keeps the SVG small: one path per segment would run to tens of megabytes
    lines = LineCollection(
        segments[central_last], array=depth[central_last], cmap=ListedColormap(colours), clim=(-0.5, 2.5), alpha=alpha or 0.4, rasterized=True, **kw)
    ax.add_collection(lines)
    ax.autoscale_view()
    return lines


def heatmap(ax, x, y, z, ramp="heat", center=None, label=None, **kw):
    cmap = low_to_high(ramp)
    if center is not None:
        reach = np.nanmax(np.abs(z - center))
        named = isinstance(ramp, str) and ramp in KINDS["diverging"]
        cmap = LinearSegmentedColormap.from_list(ramp, COMBOS[ramp]) if named else DIVERGING
        kw = {"vmin": center - reach, "vmax": center + reach, **kw}
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


def signal(ax, x, y, color="C2", **kw):
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
    # wraps five or more entries onto two rows, so the legend stays inside the page width
    ncols = ncols or (len(unique) if len(unique) < 5 else -(-len(unique) // 2))
    if isinstance(target, Figure):
        return target.legend(handles, unique.keys(), ncols=ncols, loc="outside upper right", **kw)
    return target.legend(
        handles, unique.keys(), ncols=ncols,
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


def fit(fig):
    """Grows the figure until its flattest panel has the shape subplots was asked for, so legends and labels never squeeze the data."""
    aspect = getattr(fig, "panel_aspect", None)
    panels = [ax for ax in fig.axes if ax.get_label() != "<colorbar>" and ax.name == "rectilinear" and ax.get_subplotspec()]
    for _ in range(2 if aspect and panels else 0):
        fig.draw_without_rendering()
        width, height = fig.get_size_inches()
        short = max(aspect * ax.get_position().width * width - ax.get_position().height * height for ax in panels)
        if short < 0.02:
            break
        fig.set_figheight(height + short * panels[0].get_gridspec().nrows)


def check(fig, name):
    pairs = overlaps(fig)
    if pairs:
        warnings.warn(f"{name}: {len(pairs)} pairs of labels overlap, first {pairs[0][0]!r} and {pairs[0][1]!r} "
                      "(checklist 6): fewer ticks, fewer columns, or more room", stacklevel=3)
    panels = [ax for ax in fig.axes if ax.get_label() != "<colorbar>" and ax.axison and ax.name == "rectilinear"]
    spans = [ax.get_subplotspec() for ax in panels if ax.get_subplotspec() and len(ax.get_xticks())]
    width = min((fig.get_figwidth() * len(s.colspan) / s.get_gridspec().ncols for s in spans), default=NARROW)
    if width < NARROW:
        warnings.warn(f"{name}: panels are {width:.1f} in wide (checklist 6): lf.cases to stack the cases as rows, fewer columns, or a wider page", stacklevel=3)
    height = min((ax.get_position().height * fig.get_figheight() for ax in panels), default=FLAT)
    if height < FLAT:
        warnings.warn(f"{name}: panels are {height:.1f} in tall (checklist 6): a larger aspect, fewer rows, or a legend with fewer rows", stacklevel=3)
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
    for ax in fig.axes:
        if len(ax.get_shared_x_axes().get_siblings(ax)) > 1 and not ax.xaxis.get_tick_params().get("labelbottom", True):
            ax.set_xlabel("")
    fit(fig)
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
