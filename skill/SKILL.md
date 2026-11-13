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
lf.paths(ax, x, samples, label="Posterior predictive")  # faint line per draw (100 shown) over a grey 95% band
ax.plot(x, y, color=lf.TRUE, label="True")
lf.split(ax, 1.0)                         # dashed line between observed and forecast
lf.ribbon(ax, x, lo, mid, hi, label="IFT")  # median line + light band, one per method
lf.data(ax, x, y, label="Sensors")        # black measurement dots
lf.trace(ax, x, y, label="76 Torr")       # dots joined by a line (convergence, sweeps)
lf.intervals(ax, x, lo, mid, hi, shift=dx)  # dot with a vertical 95% bar per x
lf.legend_above(axes[0])                  # one-row legend above the top panel
lf.legend_above(fig)                      # same, for a grid: labels deduplicated over all panels
for y, c in zip(curves, lf.ramp(len(curves), "heat")):  # ordered sweep, dark to light
    ax.plot(x, y, color=c)
lf.save(fig, "out/name")                  # trims spines, writes name.pdf and name.png
```

`lf.quantiles(samples)` returns `(lo, median, hi)`, ready to unpack into `ribbon` or
`intervals`. `lf.dodge(n)` gives the `shift` for each of `n` methods sharing an x position;
`intervals(connect=True)` joins the dots.

Options: `band(level=0.95, color=, alpha=)`, `paths(color=, alpha=, draws=100, level=0.95)`,
`subplots(width=, aspect=, sharex=...)`, `save(trim=False)` for axes that should keep full
spines (heatmaps, log axes), `use(tex=False)` for fast drafts.

## Colours

| Name | Use |
|---|---|
| `lf.POSTERIOR` | our method's posterior, bands and fills |
| `lf.PREDICTIVE` | forecast and posterior-predictive draws |
| `lf.REFERENCE` | the baseline method being compared against (grey) |
| `lf.TRUE` | ground truth, always drawn last so it sits on top |

Several series (methods, a sweep over a parameter): use the default colour cycle, `"C0"`,
`"C1"`, ... It runs crimson, teal, then blue, orange, green, purple, brown, olive, so the
first two series always match Fig. 3.11. Give one method the same `"Cn"` in every figure of
a report. Do not pick colours by hand.

An ordered sweep (pressure, noise level, step count) is not a set of methods: colour it with
`lf.ramp(n, name)`, which returns `n` colours from dark to light. Ramps: `"heat"` (maroon to
sand, the default), `"blues"` (ColorBrewer), `"viridis"`. Each stops before its pale end so
thin lines stay readable. The full colormaps are `lf.RAMPS[name][0]`.

`lf.MUTED` is a softer seven-colour set (brick red, steel teal, dusty pink, rose, slate,
mauve, blue-grey). Its neighbours are close in hue, so use it for light/dark pairs of one
method or a quiet figure, via `lf.use(series=lf.MUTED)`; keep the default cycle for telling
methods apart.

## Conventions

- Axis labels are LaTeX math, normalised quantities written as `$x_1/\bar{x}_1$`.
- Set ticks explicitly on axes with a natural range (`yticks=[-1, 0, 1]`); the spines are
  trimmed to the outermost ticks, so ticks define the frame.
- One legend per figure, above the top panel. No figure title; the caption carries it. In a
  grid, a column title names the case (`ax.set(title="76 Torr")` on the top row only).
- `band` (crimson, α 0.5) is for one posterior; `ribbon` is for several methods overlaid.
- Draw order: band, sample paths, truth.
- `paths` puts a neutral grey credible band under the draws by default, computed from all
  draws. Pass `level=None` when the panel already has a band (another method's `ribbon`, a
  `band` of the same posterior).
- At most one series per panel is shown as draws; every other method in that panel is a
  `ribbon`. Two sets of draws on top of each other hide both.
- Sample paths need the draws: every sampling script saves its draws (`.npz`), not only
  summaries, so `lf.paths` can show them later without re-running the sampler.

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
