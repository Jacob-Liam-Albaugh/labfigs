---
name: labfigs
description: Make figures with the lab's house style (labfigs). Use whenever writing or editing any plotting code, or when asked for a plot, figure, chart of results, posterior or posterior-predictive plot, convergence trace, or method comparison, in any project. Use it before writing matplotlib code.
---

# labfigs

`labfigs` is the lab's one plotting library: a house style modelled on Kairui Hao's thesis
figures, plus helpers for the plot elements that recur. Source lives at
`~/Documents/Predictive Science Lab/labfigs` (private repo `Jacob-Liam-Albaugh/labfigs`).

## Rules

1. Call `lf.use()` once, before creating any figure. Never set `rcParams`, fonts, DPI, or
   `plt.style` in a script.
2. Use the named colours. Never write a hex colour in a script.
3. Create figures with `lf.subplots` and finish every figure with `lf.save`.
4. If a figure needs an element the library lacks, add a helper to `labfigs.py`, use it,
   then commit and push the library. Do not write the element inline in the script.
5. A plotting script should be data loading plus a handful of `lf.` calls. If the plotting
   part passes about 20 lines, something belongs in the library.
6. Open the saved PNG and look at it before reporting the figure as done.

## API

```python
import labfigs as lf

lf.use()                                  # style; LaTeX text when latex is installed
fig, axes = lf.subplots(3, 1, aspect=0.24)  # width 6.5 in; aspect = panel height / width
lf.band(ax, x, samples, label="Posterior")  # 95% band from draws, shape (draws, len(x))
lf.paths(ax, x, samples, label="Posterior predictive")  # one faint line per draw
ax.plot(x, y, color=lf.TRUE, label="True")
lf.split(ax, 1.0)                         # dashed line between observed and forecast
lf.legend_above(axes[0])                  # one-row legend above the top panel
lf.save(fig, "out/name")                  # trims spines, writes name.pdf and name.png
```

Options: `band(level=0.95, color=, alpha=)`, `paths(color=, alpha=)`,
`subplots(width=, aspect=, sharex=...)`, `save(trim=False)` for axes that should keep full
spines (heatmaps, log axes), `use(tex=False)` for fast drafts.

## Colours

| Name | Use |
|---|---|
| `lf.POSTERIOR` | our method's posterior, bands and fills |
| `lf.PREDICTIVE` | forecast and posterior-predictive draws |
| `lf.REFERENCE` | the baseline method being compared against (grey) |
| `lf.TRUE` | ground truth, always drawn last so it sits on top |

Several unordered series (a sweep over a parameter, many methods): use the default colour
cycle, which is matplotlib's `tab10`. Do not pick colours by hand.

## Conventions

- Axis labels are LaTeX math, normalised quantities written as `$x_1/\bar{x}_1$`.
- Set ticks explicitly on axes with a natural range (`yticks=[-1, 0, 1]`); the spines are
  trimmed to the outermost ticks, so ticks define the frame.
- One legend per figure, above the top panel. No titles; the caption carries the title.
- Draw order: band, sample paths, truth.

## Running

The library is installed editable in the default `python3`. In a `uv` project, run without
touching the project's dependencies:

```bash
uv run --with-editable "$HOME/Documents/Predictive Science Lab/labfigs" python scripts/plot.py
```

Worked example: `examples/duffing_311.py` in the library reproduces thesis Fig. 3.11.

## Not covered yet

2D field plots (heatmaps), corner plots, and one-call recipes for whole figure types. Ask
before inventing a style for these.
