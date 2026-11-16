"""Shows every colour option in the library with its name: colours, series sets, ramps, schemes and combinations."""
from pathlib import Path

import numpy as np
from matplotlib.colors import LinearSegmentedColormap

import labfigs as lf

out = Path(__file__).parent
ACROSS, STOPS = 4, 64


def smooth(colours):
    return LinearSegmentedColormap.from_list("", colours)(np.linspace(0, 1, STOPS))


def split(title, sets):
    keys, size = list(sets), -(-len(sets) // ACROSS)
    return [(title if i == 0 else "", {key: sets[key] for key in keys[i * size:(i + 1) * size]}) for i in range(ACROSS)]


wada = lf.combos(kind="combination")
bands = [
    [("Named colours", {name: [getattr(lf, name)] for name in ("POSTERIOR", "PREDICTIVE", "REFERENCE", "TRUE")} | {"NIGHT": list(lf.NIGHT.values())}),
     ("Series sets", {name: getattr(lf, name) for name in ("SERIES", "MUTED", "PURPLE_TEAL")} | lf.combos(kind="categorical")),
     ("Ramps in lf.ramp", {name: lf.ramp(STOPS, name) for name in lf.RAMPS}),
     ("Diverging and cyclic", {"DIVERGING": lf.DIVERGING(np.linspace(0, 1, STOPS))} | {
         key: smooth(colours) for key, colours in (lf.combos(kind="diverging") | lf.combos(kind="cyclic")).items()})],
    split("Sequential schemes", {key: lf.ramp(STOPS, colours) for key, colours in lf.combos(kind="sequential").items()}),
    *(split(f"Wada, {title} colours", {key: colours for key, colours in wada.items() if len(colours) == size})
      for size, title in ((2, "two"), (3, "three"), (4, "four"))),
]
rows = [max(len(sets) for _, sets in band) for band in bands]

lf.use()
fig, axes = lf.subplots(len(bands), ACROSS, width=10, aspect=1.6, gridspec_kw={"height_ratios": [n + 2 for n in rows], "wspace": 0.08})
for line, band, n in zip(axes, bands, rows):
    for ax, (title, sets) in zip(line, band):
        lf.swatches(ax, sets)
        ax.set(title=title, ylim=(n - 0.4, -0.6))
lf.save(fig, out / "colours", trim=False)

shown = [key for band in bands for _, sets in band for key in sets]
assert len(shown) == len(set(shown)) == len(lf.COMBOS) + len(lf.RAMPS) + 9, len(shown)
assert set(lf.COMBOS) | set(lf.RAMPS) <= set(shown)
print("wrote", out / "colours.svg", len(shown), "rows")
