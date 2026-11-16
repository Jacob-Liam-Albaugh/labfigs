"""Redraws Andrey Churkin's eight design steps, from the matplotlib default to the finished labfigs figure."""
from pathlib import Path

import matplotlib as mpl
import numpy as np
from sklearn.datasets import load_iris

import labfigs as lf

out = Path(__file__).parent
iris = load_iris()
STEPS = ("Matplotlib defaults", "Range set around the data", "Font size and style", "Grid lines, equal aspect",
         "Colour scheme", "Larger markers, heavier lines", "Display order", "Compact legend")
SPECIES = ((0, "tab:blue", "C0"), (2, "tab:orange", "C1"))
FITS = ((1, "-", "LR", "tab:green"), (2, "--", "PR", "tab:red"))
span = np.linspace(2, 10, 200)


def panel(ax, step):
    for kind, plain, color in SPECIES:
        x, y = iris.data[iris.target == kind, :2].T
        if step >= 5:
            lf.points(ax, x, y, color=color, label=iris.target_names[kind].title())
        else:
            ax.scatter(x, y, s=4, color=color if step >= 4 else plain)
    for kind, degree, style, label, bare in ((k, *fit) for k, *_ in SPECIES for fit in FITS):
        x, y = iris.data[iris.target == kind, :2].T
        look = dict(color="C2", ls=style) if step >= 4 else dict(color=bare)
        ax.plot(span, np.polyval(np.polyfit(x, y, degree), span), lw=1.3 if step >= 5 else 0.6,
                zorder=2 if step >= 6 else 4, label=label, **look)
    ax.set(xlabel="Sepal length (cm)", ylabel="Sepal width (cm)", box_aspect=1)
    if step >= 1:
        ax.set(xlim=(3.9, 8.3), ylim=(1.2, 5.6), xticks=range(4, 9), yticks=range(2, 6))
    if step >= 3:
        lf.grid(ax)
        ax.set(aspect="equal")
    if step == 7:
        lf.legend_above(ax, gap=0.04, frameon=False, columnspacing=0.8, handletextpad=0.3)


lf.use(font="mono", series="Kandinsky")
fig, axes = lf.subplots(2, 4, width=13, aspect=1.15)
fig.get_layout_engine().set(hspace=0.16)
for step, ax in enumerate(axes.flat):
    if step < 2:
        ax.remove()
        # fixes the default look of the first two panels before the house style reaches them
        with mpl.rc_context(mpl.rcParamsDefault):
            ax = fig.add_subplot(2, 4, step + 1)
            panel(ax, step)
            ax.tick_params(labelsize=5)
            ax.xaxis.label.set_size(5)
            ax.yaxis.label.set_size(5)
            fig.canvas.draw()
    else:
        panel(ax, step)
    ax.text(0.5, 1.17, f"{step + 1}. {STEPS[step]}", transform=ax.transAxes, ha="center", weight="bold")
lf.save(fig, out / "design_steps", trim=False)

assert len(fig.axes) == len(STEPS) and (out / "design_steps.svg").stat().st_size > 0
print("wrote", out / "design_steps.svg")
