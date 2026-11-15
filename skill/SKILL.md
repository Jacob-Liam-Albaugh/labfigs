---
name: labfigs
description: Make figures with the lab's house style (labfigs). Use whenever writing or editing any plotting code, or when asked for a plot, figure, chart of results, posterior or posterior-predictive plot, convergence trace, or method comparison, in any project. Use it before writing matplotlib code.
---

# labfigs

`labfigs` is the lab's one plotting library: a house style modelled on Kairui Hao's thesis
figures and the design principles of Andrey Churkin's BeautifulFigures, plus helpers for the
plot elements that recur. Source lives at
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
7. Run the design checklist below on every figure that goes into a paper or report.

## API

```python
import labfigs as lf

lf.use()                                  # style; LaTeX text when latex is installed
fig, axes = lf.subplots(3, 1, aspect=0.24)  # width 6.5 in; aspect = panel height / width
lf.band(ax, x, samples, label="Posterior")  # 95% band from draws, shape (draws, len(x))
lf.paths(ax, x, samples, label="Posterior predictive")  # faint line per draw (100 shown) over a grey 95% band
lf.paths(ax, x, samples, gradient=True)   # no grey band unless level=0.95; heat-shaded bands: dark within 1 sd of the mean, mid to 2 sd, pale beyond
lf.paths(ax, x, samples, gradient="C1")   # same bands in shades of one colour (any colour), or a ramp name ("viridis")
ax.plot(x, y, color=lf.TRUE, label="True")
lf.split(ax, 1.0)                         # dashed line between observed and forecast
lf.ribbon(ax, x, lo, mid, hi, label="IFT")  # median line + light band, one per method
lf.data(ax, x, y, label="Sensors")        # black measurement dots
lf.trace(ax, x, y, label="76 Torr")       # dots joined by a line (convergence, sweeps)
lf.intervals(ax, x, lo, mid, hi, shift=dx)  # dot with a vertical 95% bar per x
lf.legend_above(axes[0])                  # one-row legend above the top panel
lf.legend_above(fig)                      # same, for a grid: labels deduplicated over all panels
lf.legend_above(fig, ncols=3)             # wrap a long legend (five or more entries) onto two rows
fig, axes = lf.subplots(2, 3, n=5)        # five panels, short bottom row centred; axes comes back flat
lf.density(ax, samples, label="SVI")      # density curve of draws; fill=True for a filled one
lf.shade(ax)                              # grey background marking a panel as different (unconditioned, held out)
lf.signal(ax, t, y, label="Measurement")  # dense measured time series: hairline, open dashes, blue
lf.zoom(top, bottom, 0, 0.1)              # dashed lines from the span [0, 0.1] of top to the panel below it
for y, c in zip(curves, lf.ramp(len(curves), "heat")):  # ordered sweep, dark to light
    ax.plot(x, y, color=c)
lf.heatmap(ax, x, y, z, vmin=0, vmax=1)   # 2D field with its colourbar; z has shape (len(y), len(x))
lf.heatmap(ax, x, y, error, center=0)     # signed field: teal below, white at 0, crimson above
free = lf.region(ax, corners, "C2", label="No coordination")  # polygon outline; dashed=True for a thin dashed one
lf.contours(ax, x, y, z, levels, colors, within=free)  # thin contour lines, clipped to a region
lf.level_key(ax, labels, colors, "Limit:")  # row of boxed level values above the panel, one colour each
lf.ramp(n, ("crimson", "C2"))             # n colours blending from one colour to another
lf.grid(ax)                               # fine major and minor grid for reading values off; save with trim=False
lf.save(fig, "out/name")                  # trims spines, writes name.pdf and name.png
```

`lf.quantiles(samples)` returns `(lo, median, hi)`, ready to unpack into `ribbon` or
`intervals`. `lf.dodge(n)` gives the `shift` for each of `n` methods sharing an x position;
`intervals(connect=True)` joins the dots.

Options: `band(level=0.95, color=, alpha=)`, `paths(color=, alpha=, draws=100, level="auto", gradient=False | True | colour | ramp name)`,
`heatmap(ramp="heat", center=None, label=)` plus any `pcolormesh` option,
`subplots(width=, aspect=, sharex=...)`, `save(trim=False)` for axes that should keep full
spines (log axes), `use(tex=False)` for fast drafts.

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
sand, the default), `"blues"` and `"ylgnbu"` (ColorBrewer), `"viridis"`, `"magma"`, `"plasma"`, `"cividis"`
(colour-blind safe), `"rocket"`, `"mako"`, `"flare"`, `"crest"`. Each stops before its pale
end so thin lines stay readable. The full colormaps are `lf.RAMPS[name][0]`. Any colour works in
place of a ramp name and gives shades of that colour (`lf.ramp(n, "C1")`,
`gradient="tab:blue"`), so single-hue ramps need no entry of their own.

2D fields use `lf.heatmap`: the same ramps, pale for low values and dark for high
(`ramp="heat"` by default; ramps that run dark to light, such as `"mako"` and `"viridis"`,
are flipped to match). Different quantities in one figure take different ramps (a field
and its standard deviation). A signed field (an error, a residual) takes `center=0`, which
switches to the teal-white-crimson map with limits symmetric about the centre. Panels that
are compared against each other share `vmin` and `vmax`. Set `aspect="equal"` on the axes
when x and y are the same physical quantity. Overlay sensors with `lf.data`.

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
- A true parameter value is a plain line: `ax.axhline(v, color=lf.TRUE, ls="--", label="True")`,
  or `ax.axvline` on a density. A reference method's interval across a sweep is
  `ax.axhspan(lo, hi, color=lf.REFERENCE, alpha=0.3, lw=0, label="NUTS")`.
- A panel showing two named quantities gets two titles in their colours:
  `ax.set_title(a, loc="left", color="C1")` and `ax.set_title(b, loc="right", color="C0")`.
- Dense oscillating signal against a measurement: `lf.ribbon(..., lw=0.3)` then `lf.signal`,
  posterior in crimson (teal and the blue measurement do not separate), a zoomed panel beside it.
- Plot large values in scaled units and put the scale in the label
  (`r"Iterations ($\times 10^6$)"`), never matplotlib's offset text.
- `paths` puts a neutral grey credible band under the draws by default, computed from all
  draws. Pass `level=None` when the panel already has a band (another method's `ribbon`, a
  `band` of the same posterior).
- Flat draws over the grey interval are the default look. `gradient` is the alternative: it
  shades each draw by its distance from the pointwise mean in standard deviations (three
  flat bands: under 1, 1 to 2, over 2) and leaves the grey interval off unless asked for
  with `level=0.95`.
- Use `gradient=True` when the draws are the only posterior in the panel. Next to another
  method's `ribbon` keep them flat; the dark core hides the ribbon's median line.
- `gradient=True` is the heat ramp. Pass a colour for shades of that colour, or a ramp name.
  `color=` is ignored once `gradient` is set. Use the choice to tell quantities apart, one
  per quantity in every figure of a report (conductivity in heat, temperature in the
  method's `"Cn"`). The legend entry takes the 1 sd band's colour; when one label is drawn
  in two palettes across panels, the legend shows the last one.
- At most one series per panel is shown as draws; every other method in that panel is a
  `ribbon`. Two sets of draws on top of each other hide both.
- Sample paths need the draws: every sampling script saves its draws (`.npz`), not only
  summaries, so `lf.paths` can show them later without re-running the sampler.
- Regions in a plane (feasible sets, operating envelopes): `lf.region` for each outline,
  `lf.contours(..., within=region)` for the levels inside it coloured by
  `lf.ramp(n, (tight, loose))`, `lf.level_key` to name the levels, `lf.grid`, equal aspect,
  `lf.save(trim=False)`. When each panel has its own colour, each panel gets its own legend
  (`lf.legend_above(ax, ncols=1, frameon=False)`); crimson is the shared tight end of every blend.
- Panel letters go under the x label: `ax.set_xlabel("$P$ (kW)\n(a)")`.

## Design checklist

Adapted from Andrey Churkin's BeautifulFigures (https://github.com/AndreyChurkin/BeautifulFigures).

1. Message first. Say in one sentence what the figure shows, then remove every element
   that does not serve that sentence.
2. Size for the page. Set `lf.subplots(width=)` to the printed width (6.5 in for full text
   width, 3.5 in for one column of a two-column paper) and include the PDF unscaled, so the
   10 pt text prints at the size of the body text.
3. Check it in the real layout. A figure that looks right on screen can fail on the page:
   compile the manuscript and check font size, line weights, marker sizes and the legend.
4. Few colours, each with a job. One data subset keeps one colour in every figure of a
   manuscript, indicator colours keep one meaning, and a new colour appears only when it
   carries new information.
5. Ordered data takes a ramp, never a rainbow. Every `lf.ramp` runs dark to light, so the
   order survives greyscale printing.
6. Legend compact, above the axes, never over the data.
7. Points sit above lines. When the points are the subject, the trend line is neutral
   (`lf.REFERENCE`).
8. Both axes in the same unit: `aspect="equal"`. Values meant to be read off: `lf.grid(ax)`.
9. Vector output. The PDF goes into the paper; the PNG is for slides and READMEs. Add
   `formats=("pdf", "png", "svg")` when the figure will be edited by hand.
10. No pie charts. No 3D unless the shape of the surface is the message; a 2D field is
    `lf.heatmap`.
11. Plan for several rounds: render, look, fix, render again.

## Running

The library is installed editable in the default `python3`. In a `uv` project, run without
touching the project's dependencies:

```bash
uv run --with-editable "$HOME/Documents/Predictive Science Lab/labfigs" python scripts/plot.py
```

Worked examples in the library: `examples/duffing_311.py` reproduces thesis Fig. 3.11,
`examples/field.py` shows gradient draws and a 2D field in every ramp,
`examples/palettes.py` shows every ramp as a sweep, `examples/hao_figures.py` has the other
thesis figure types: parameter intervals over a sweep (Fig. 3.2), densities per method
(Fig. 6.2, 4.6), a grid with shaded panels (Fig. 4.9), convergence traces (Fig. 6.7).
`examples/hao_replicas.py` redraws three whole figures: a zoomed second row (thesis
Fig. 6.3) and dense signal against measurement (filter paper Figs. 14 and 16).
`examples/feasible_regions.py` draws feasible regions with nested limit contours, a level
key and a fine grid.

## Not covered yet

Corner plots, filled contour plots, 3D surfaces, and one-call recipes for whole figure types. Ask before
inventing a style for these.
