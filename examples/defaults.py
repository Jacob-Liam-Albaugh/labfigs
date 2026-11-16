"""What labfigs does without being asked: enclosing ticks, a dodge in points, the % sign, and warnings from lf.save."""
import warnings
from pathlib import Path

import numpy as np

import labfigs as lf

lf.use()
rng = np.random.default_rng(0)
pressure = np.array([1e-3, 1.0, 76.0, 300.0, 760.0])
truth = np.array([5.2, 4.1, 3.6, 3.3, 3.1])

fig, (a, b, c) = lf.subplots(1, 3, aspect=0.9)
for method, dx in zip(("IFT", "Diffusion"), lf.dodge(2)):
    draws = truth + rng.normal(0, 0.35, (400, 5))
    lf.intervals(a, pressure, *lf.quantiles(draws), shift=dx, label=method)
    lf.intervals(b, range(5), *lf.quantiles(draws * [4, 1, 1, 1, 1]), shift=dx, label=method)
lf.marks(a, pressure, truth, label="True")
a.set(xscale="log", xticks=[1e-3, 1e-1, 1e1, 1e3], xlabel="Pressure (Torr)", ylabel="$k(T_h)/k(T_c)$")
b.set(xticks=range(5), xlabel="Case", ylabel="$k(T_h)/k(T_c)$")
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
assert not lf.overlaps(fig)
c.text(0, 1.02, "Steps", transform=c.transAxes, va="top")
c.text(0, 1.02, "Error", transform=c.transAxes, va="top")
assert lf.overlaps(fig) == [("Steps", "Error")], lf.overlaps(fig)
