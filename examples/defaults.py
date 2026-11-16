"""What labfigs does without being asked: enclosing ticks on linear and log axes, intervals from draws, a dodge in points, the % sign, and warnings from lf.save."""
import warnings
from pathlib import Path

import numpy as np

import labfigs as lf

lf.use()
rng = np.random.default_rng(0)
pressure = np.array([1e-3, 1.0, 76.0, 300.0, 760.0])
truth = np.array([5.2, 4.1, 3.6, 3.3, 3.1])

fig, (a, b, c) = lf.subplots(1, 3, aspect=0.9)
draws = {method: truth + rng.normal(0, 0.35, (400, 5)) for method in ("IFT", "Diffusion")}
for (method, samples), dx in zip(draws.items(), lf.dodge(2)):
    lf.intervals(a, pressure, samples, shift=dx, label=method)
lf.marks(a, pressure, truth, label="True")
a.set(xscale="log", xlabel="Pressure (Torr)", ylabel="$k(T_h)/k(T_c)$")
wide_first = np.array([4, 1, 1, 1, 1])
lf.compare(b, list("ABCDE"), {method: samples * wide_first for method, samples in draws.items()}, true=truth * wide_first)
b.set(xlabel="Case", ylabel="$k(T_h)/k(T_c)$")
cost = np.arange(1, 9)
lf.trace(c, cost, 37.3 / cost, ls="--", label="Error of the median")
c.set(xlabel="Steps ($\\times 10^3$)", ylabel="Error (%)")
lf.tag(fig, "Case 3")
lf.legend_above(fig)

with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    lf.save(fig, Path(__file__).with_suffix(""))
assert [str(w.message).split(":")[1][:14] for w in caught] == [" one x positio"], [str(w.message) for w in caught]
assert c.get_yticks()[0] <= 37.3 / 8 and c.get_yticks()[-1] >= 37.3, c.get_yticks()
assert lf.percent(r"50\%") == lf.percent("50%")
assert a.spines["bottom"].get_bounds()[0] <= 1e-3 and a.spines["bottom"].get_bounds()[1] >= 760, a.spines["bottom"].get_bounds()
assert np.allclose(lf.log_ticks(0.04, 0.7), [0.02, 0.05, 0.1, 0.2, 0.5, 1]) and np.allclose(lf.log_ticks(2e-9, 0.8, 4), [1e-9, 1e-6, 1e-3, 1])
assert [label.get_text() for label in b.get_xticklabels()] == list("ABCDE") and len(b.lines) == len(a.lines)
assert not lf.overlaps(fig)
c.text(0, 1.02, "Steps", transform=c.transAxes, va="top")
c.text(0, 1.02, "Error", transform=c.transAxes, va="top")
assert lf.overlaps(fig) == [("Steps", "Error")], lf.overlaps(fig)

walks = rng.normal(0, 1, (200, 20)).cumsum(1)
wide, narrow = lf.subplots()[1], lf.subplots(1, 5)[1][0]
level, curve, floor = lf.truth(wide, 1), lf.truth(wide, [0, 1], [0, 1]), lf.reference(wide, 0.5)
assert (level.get_ls(), curve.get_ls(), floor.get_ls(), floor.get_color(), floor.get_label()[:1]) == ("--", "-", "--", lf.REFERENCE, "_")
assert (len(lf.paths(wide, range(20), walks)), len(lf.paths(narrow, range(20), walks))) == (100, 25)
assert len(lf.paths(narrow, range(20), walks, draws=60)) == 60

crowded = lf.subplots(1, 5)[1][0]
lf.compare(crowded, list("AB"), {str(method): rng.normal(size=(50, 2)) for method in range(4)}, true=[0, 0])
crowded.figure.canvas.draw()
dots = [line for line in crowded.lines if line.get_marker() == "o"]
assert len(dots) == 4 and all(dot.get_clip_box().contains(*xy) for dot in dots for xy in dot.get_transform().transform(dot.get_xydata()))
mark = next(line for line in crowded.lines if line.get_marker() == "_")
half = mark.get_markersize() / 2 * crowded.figure.dpi / 72
assert all(mark.get_clip_box().contains(x + side * half, y) for x, y in mark.get_transform().transform(mark.get_xydata()) for side in (-1, 1))

few, many = lf.cases(list("abc"), ["u", "v"])[1], lf.cases(list("abcde"), ["u", "v"])[1]
assert (few.shape, many.shape) == ((3, 2), (5, 2))
assert (few[0, 0].get_gridspec().ncols, many[0, 0].get_gridspec().ncols) == (3, 2)
assert (few[2, 0].get_title(), many[4, 0].get_ylabel(), many[0, 1].get_title()) == ("c", "e", "v")
