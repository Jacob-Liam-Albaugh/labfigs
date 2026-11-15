"""Shows the analogous colour combinations in the library: Sanzo Wada's by number, ColorSchemes.jl's by name."""
from pathlib import Path

import labfigs as lf

out = Path(__file__).parent
sets = lf.analogous()
wada = [key for key in sets if isinstance(key, int)]
columns = {
    "Wada, two colours": [key for key in wada if len(sets[key]) == 2],
    "Wada, three and four": [key for key in wada if len(sets[key]) > 2],
    "ColorSchemes.jl": [key for key in sets if isinstance(key, str)],
}
rows = max(map(len, columns.values()))

lf.use()
fig, axes = lf.subplots(1, 3, width=7.5, aspect=3.4, gridspec_kw={"wspace": 0.45})
for ax, (title, keys) in zip(axes, columns.items()):
    lf.swatches(ax, {key: sets[key] for key in keys})
    ax.set(title=title, ylim=(rows - 0.4, -0.6))
lf.save(fig, out / "combos", trim=False)

assert len(lf.COMBOS) == 348 + len(columns["ColorSchemes.jl"]) and all(lf.hue_arc(colours) <= 60 for colours in sets.values())
assert lf.hue_arc(lf.COMBOS[1]) > 120 and lf.hue_arc(["crimson", "lightseagreen"]) > 120
print("wrote", out / "combos.svg", {title: len(keys) for title, keys in columns.items()})
