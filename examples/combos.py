"""Shows the muted colour combinations in the library: Sanzo Wada's by number, ColorSchemes.jl's by name."""
from pathlib import Path

import labfigs as lf

out = Path(__file__).parent
sets = lf.combos(vivid=0.5)
wada = [key for key in sets if isinstance(key, int)]
pairs = [key for key in wada if len(sets[key]) == 2]
columns = {
    "Two colours, hues apart": [key for key in pairs if lf.hue_arc(sets[key]) > 60],
    "Two colours, hues close": [key for key in pairs if lf.hue_arc(sets[key]) <= 60],
    "Three colours": [key for key in wada if len(sets[key]) == 3],
    "Four colours": [key for key in wada if len(sets[key]) == 4],
    "Named ramps": [key for key in sets if isinstance(key, str)],
}
rows = max(map(len, columns.values()))

lf.use()
fig, axes = lf.subplots(1, 5, width=10, aspect=3.2, gridspec_kw={"wspace": 0.5})
for ax, (title, keys) in zip(axes, columns.items()):
    lf.swatches(ax, {key: sets[key] for key in keys})
    ax.set(title=title, ylim=(rows - 0.4, -0.6))
lf.save(fig, out / "combos", trim=False)

assert sum(map(len, columns.values())) == len(sets) and all(lf.vividness(colours) <= 0.5 for colours in sets.values())
assert lf.vividness(["yellow"]) == 1 and lf.vividness(lf.MUTED[:2]) < 0.5 < lf.vividness([lf.PREDICTIVE]) < lf.vividness([lf.POSTERIOR])
assert lf.hue_arc(lf.MUTED[:2]) > 120 and len(lf.combos()) == len(lf.COMBOS) > len(lf.combos(arc=(0, 60))) > 100
print("wrote", out / "combos.svg", {title: len(keys) for title, keys in columns.items()})
