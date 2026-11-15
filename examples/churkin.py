"""Redraws Andrey Churkin's two BeautifulFigures examples: an edged scatter and a dark 3D surface."""
from pathlib import Path

import numpy as np
from sklearn.datasets import load_iris

import labfigs as lf

out = Path(__file__).parent
iris = load_iris()
keep = iris.target != 1
length, width, species = iris.data[keep, 0], iris.data[keep, 1], iris.target[keep]

lf.use(font="mono", series=lf.PURPLE_TEAL)
fig, ax = lf.subplots(width=3.4, aspect=1)
for kind, color in ((0, "C0"), (2, "C2")):
    lf.points(ax, length[species == kind], width[species == kind], color=color, label=iris.target_names[kind].title())
span = np.linspace(3.9, 8.3, 100)
for kind in (0, 2):
    for degree, style, label in ((1, "-", "LR"), (2, "--", "PR")):
        fit = np.polyfit(length[species == kind], width[species == kind], degree)
        ax.plot(span, np.polyval(fit, span), color="C1", lw=1.3, ls=style, label=label)
lf.grid(ax)
ax.set(aspect="equal", xlim=(3.9, 8.3), ylim=(1.2, 5.6), xticks=range(4, 9), yticks=range(2, 6))
ax.set(xlabel="Sepal length (cm)", ylabel="Sepal width (cm)")
lf.legend_above(ax, gap=0.04, frameon=False, columnspacing=0.8, handletextpad=0.3)
lf.save(fig, out / "edged_scatter", trim=False)

hour, day = np.meshgrid(np.linspace(0, 23, 70), np.linspace(0, 364, 120))
daily = 25 * np.exp(-(hour - 8) ** 2 / 6) + 45 * np.exp(-(hour - 18.5) ** 2 / 5)
price = 30 + daily * (1 + 0.6 * np.cos(2 * np.pi * day / 365)) * (1 + 0.15 * np.sin(2 * np.pi * day / 28))

lf.use(font="mono", dark=True)
fig, ax = lf.subplots(width=6.5, aspect=0.75, subplot_kw={"projection": "3d"})
lf.surface(ax, hour, day, price, ramp="sunset", label="Price (EUR/MWh)")
ax.set(xlabel="Hour of day", ylabel="Day of year", xticks=range(0, 24, 6), yticks=range(0, 361, 90))
ax.view_init(elev=30, azim=-60)
fig.suptitle("Synthetic day-ahead prices", weight="bold")
lf.save(fig, out / "surface_3d")

names = ("edged_scatter", "surface_3d")
assert lf.darker("white") == (0.7, 0.7, 0.7) and all((out / f"{name}.svg").stat().st_size > 0 for name in names)
print("wrote", *(out / f"{name}.svg" for name in names))
