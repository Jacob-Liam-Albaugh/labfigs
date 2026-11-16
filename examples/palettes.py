"""Shows every sequential ramp on the same decaying curves."""
from pathlib import Path

import numpy as np

import labfigs as lf

x = np.linspace(0, 1, 200)
lf.use()
palettes = {name: lf.ramp(6, name) for name in lf.RAMPS}
fig, axes = lf.subplots(2, 7, width=13, aspect=0.75, sharex=True, sharey=True)
for ax, (name, colors) in zip(axes.flat, palettes.items()):
    for rate, color in enumerate(colors, start=1):
        ax.plot(x, np.exp(-rate * x), color=color, lw=1.5)
    ax.set(title=name, xticks=[0, 0.5, 1], yticks=[0, 0.5, 1])
fig.supxlabel("$x$")
fig.supylabel(r"$e^{-kx}$")

out = lf.save(fig, Path(__file__).parent / "palettes")
assert len(palettes) == axes.size and all(len(c) >= 3 for c in palettes.values()) and out.with_suffix(".svg").stat().st_size > 0
print("wrote", out.with_suffix(".svg"))
