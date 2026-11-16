"""Shows the named schemes that are not dark-to-light ramps: diverging, cyclic and categorical, each in use."""
from pathlib import Path

import numpy as np

import labfigs as lf

out = Path(__file__).parent
kinds = {kind: lf.combos(kind=kind) for kind in lf.KINDS}
lf.use(series=lf.COMBOS["tol_muted"])

fig, (top, bottom) = lf.subplots(2, 3, width=10, aspect=0.8)
for ax, (kind, sets) in zip(top, kinds.items()):
    lf.swatches(ax, sets)
    ax.set(title=kind.capitalize(), ylim=(max(map(len, kinds.values())) - 0.4, -0.6))

X, Y = np.meshgrid(np.linspace(0, 1, 80), np.linspace(0, 1, 80))
signed, phase, lines = bottom
lf.heatmap(signed, X, Y, 0.08 * np.sin(5 * X) * np.cos(4 * Y), ramp="vik", center=0)
turn = lf.heatmap(phase, X, Y, np.arctan2(Y - 0.5, X - 0.5), ramp="vikO", vmin=-np.pi, vmax=np.pi)
turn.colorbar.set_ticks([-np.pi, 0, np.pi], labels=[r"$-\pi$", "0", r"$\pi$"])
for ax, title in ((signed, "center=0, ramp=vik"), (phase, "ramp=vikO")):
    ax.set(title=title, xticks=[0, 0.5, 1], yticks=[0, 0.5, 1], xlabel="$x$", ylabel="$y$", aspect="equal")
x = np.linspace(0, 1, 200)
for shift in range(len(lf.COMBOS["tol_muted"])):
    lines.plot(x, np.exp(-2 * x) * np.sin(2 * np.pi * (x + shift / 9)) + shift / 3)
lines.set(title="series: tol muted", xticks=[0, 0.5, 1], yticks=[0, 1, 2, 3], xlabel="$x$", ylabel="$u$")
lf.save(fig, out / "schemes")

named = [key for key in lf.COMBOS if isinstance(key, str)]
assert sum(map(len, lf.KINDS.values())) == len({key for names in lf.KINDS.values() for key in names}) < len(named)
assert all(lf.vividness(colours) <= 0.6 for sets in kinds.values() for colours in sets.values())
assert all(colours[0] == colours[-1] for colours in kinds["cyclic"].values())
for colours in kinds["diverging"].values():
    shade = [lf.luma(colour) for colour in colours]
    assert shade.index(max(shade)) == 5 or shade.index(min(shade)) == 5, colours
assert all(lf.hue_arc(colours) > 180 for colours in kinds["categorical"].values()) and lf.kind_of("devon") == "sequential"
assert signed.collections[0].cmap.name == "vik" and lf.kind_of(120) == "combination" and len(lf.combos(kind="sequential")) > 40
print("wrote", out / "schemes.svg", {kind: len(sets) for kind, sets in kinds.items()})
