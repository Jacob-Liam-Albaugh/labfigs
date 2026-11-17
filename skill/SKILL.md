---
name: labfigs
description: Make figures with the lab's house style (labfigs), each delivered as a Jupyter notebook the user can tweak by hand. Use whenever writing or editing any plotting code, or when asked for a plot, figure, chart of results, posterior or posterior-predictive plot, convergence trace, or method comparison, in any project. Use it before writing matplotlib code.
---

# labfigs

`labfigs` is the lab's one plotting library: a house style modelled on Kairui Hao's thesis
figures and the design principles of Andrey Churkin's BeautifulFigures, plus helpers for the
plot elements that recur. Source lives at
`~/Documents/Predictive Science Lab/labfigs` (private repo `Jacob-Liam-Albaugh/labfigs`).

## Rules

1. Call `lf.use()` once, before creating any figure. Never set `rcParams`, fonts, DPI, or
   `plt.style` yourself.
2. Use the named colours. Never write a hex colour.
3. Create figures with `lf.subplots` and finish every figure with `lf.save`.
4. If a figure needs an element the library lacks, add a helper to `labfigs.py`, use it,
   then commit and push the library. Do not write the element inline in the notebook.
5. Deliver every figure as a Jupyter notebook (`.ipynb`) laid out as in "The notebook", so
   the user can change a setting by hand and re-run one cell. Never leave a `.py` plotting
   script in a project. A figure cell is its settings plus a handful of `lf.` calls; if
   the drawing part passes about 20 lines, something belongs in the library.
6. Figures are vector only: `lf.save` writes SVG. Run the notebook and look at every figure
   before reporting it as done: `jupyter nbconvert --to notebook --execute --inplace name.ipynb`
   (which also stores each figure under its cell), then
   `rsvg-convert -w 1600 name.svg -o <scratch>/name.png` and open that preview.
   The preview is for checking, never the deliverable.
7. Run the design checklist below on every figure that goes into a paper or report.
8. When a request goes against the checklist, make the figure as asked and say so. Never
   change the request silently and never stay silent. See "When the request goes against
   the guidelines".

## The notebook

The deliverable is a notebook next to its SVG files, saved with its figures inside: each
figure shows under the cell that draws it, and the same cell writes the SVG. The user opens
it, changes a setting at the top of a figure's cell and re-runs that cell. Everything they might want to change
is named and explained; nothing they need is buried in drawing code.

Cells, in this order. Every notebook in `examples/` follows it: copy the nearest one.

1. Header (markdown). `# Title`, then one line each:
   `**Shows:**` what the reader sees, in plain words.
   `**Graph type:**` the form and the `lf.` calls that draw it.
   `**Writes:**` the SVG files and where they land.
   `**To tweak:**` which cell to change and re-run.
   `**Runs on:**` the kernel, with its Python and the versions of the packages that matter
   (JAX, PyTorch), and the command that makes the kernel when it is missing.
   `**To run it all:**` the `jupyter nbconvert` command below.
2. Setup (code). Imports, then `lf.use()` after every other import (a project module may
   switch matplotlib's backend; `lf.use` puts figures back under the cell), the random
   generator if any. Nothing else.
3. `## Data` (markdown, then code). The markdown lists every array the figure uses, with
   its shape and meaning. The code loads saved results from a path named at the top of the
   cell (`RUN = Path("../runs/thermal")`). No sampling or training here.
4. `## Figure` (markdown, then ONE code cell), once per figure. The markdown has one bullet
   per setting: what it changes in the figure, its unit, the allowed values. The code cell
   is the settings in capitals, a blank line, the drawing, and `lf.save(fig, NAME)` as its
   last line.
5. `## Checks` (markdown, then code), only when there is something real to assert. Its
   markdown says what a failure means and ends with "Nothing to tweak."

What makes it easy to tweak:

- Settings and drawing share one cell, so re-running that cell alone always gives the new
  figure, whatever was run before.
- Every label, colour, tick list, limit, level, panel shape and file name the drawing uses
  is a setting. No number or string a user would change sits in the drawing code.
- A setting is named for what it is in the figure (`FORECAST_STARTS`, `BASELINE_LABEL`,
  `PANEL_ASPECT`), never for the argument it feeds (`X0`, `KW`). Related ones share a line:
  `X_LABEL, X_TICKS = "$t$ (s)", [0, 5, 10]`.
- Explanations go in the markdown above the cell, not in code comments.
- With several figures in one notebook, each gets its own Data and Figure cells
  (`## Data for the densities`, `## Figure 2: densities`) and its own variable names
  (`draw_axes`, `field_axes`), so no figure's cell depends on another's.
- When many figures share one form (the profile figures of a report), draw that form once:
  a `## Shared settings` cell holds the names, colours and labels every figure uses, and a
  `## How a ... figure is drawn` cell defines one function that returns the figure, with
  its arguments explained in the markdown above. Each figure cell is then its own settings
  and one call, ending in `lf.save`; a family of same-form figures may be one cell with a
  loop. Say in the header that a shared cell is re-run before the figure cells.
- A figure with its own look calls `lf.use(series=SERIES)` or `lf.use(dark=DARK)` at the
  top of its drawing, with those as settings. `lf.use` starts from a clean style each time.
- `lf.save(fig, NAME)` last: the cell then shows the figure (as SVG) and the path written.
  A plain name lands next to the notebook, which is also its working directory. For a
  report folder, set `OUT = Path("../report/figures")` in setup and save to `OUT / NAME`.

Settings to expose, by graph type (on top of `NAME`, `PANEL_ASPECT`, axis labels, and any
ticks or limits set by hand, which every figure has):

| Graph type | Settings |
|---|---|
| Band, draws, ribbon | legend labels, colours, `LEVEL`, `FORECAST_STARTS` (the split), `DRAWS` when overridden |
| Gradient draws | `GRADIENT` (ramp, colour or scheme name) |
| Intervals, `compare` | method labels, `LEVEL`, case names, the baseline's label and band |
| Density | labels, `FILL_COLOUR`, `LEGEND_COLUMNS` |
| Grid of panels, `cases` | `ROWS`, `COLUMNS`, panel titles, `SHADED` (which panels) |
| Heatmap, surface | `RAMP`, `VALUE_RANGE` (both ends of the colourbar), `CENTER`, colourbar label, `VIEW` for 3D |
| Sweep of curves | `RAMP`, `SHADES`, `LINE_WIDTH` |
| Regions and contours | `LEVELS`, the two ends of the level colours, region labels |
| Scatter | subset labels and colours, the trend line's label |
| Trace, signal, zoom | labels, `ZOOM_WINDOW`, tick steps |
| A look of its own | `SERIES`, `FONT`, `DARK` |

Making one:

- New notebook: write the cells as a draft in the scratch directory, then convert it. In a
  draft, `# %% [markdown]` starts a markdown cell (each line prefixed with `# `) and `# %%`
  starts a code cell. `python -m labfigs <scratch>/draft.py figures/name.ipynb` writes the
  notebook; a third argument names its kernel (see "Running"). Never write notebook JSON by hand, and never put the draft in the project.
- Existing notebook: edit the one cell with the NotebookEdit tool. Never rebuild it from a
  draft; the user's hand tweaks live in the notebook.
- Then `jupyter nbconvert --to notebook --execute --inplace figures/name.ipynb`: it runs
  every cell top to bottom on the notebook's kernel, fails on any error or failed check, and
  saves the notebook with each figure under its cell. Run it again after every edit, so
  the stored figures never lag behind the code.

```python
# %% [markdown]
# # Posterior of the temperature at 76 Torr
#
# **Shows:** the posterior of the temperature as a band, with the true profile on top.
#
# **Graph type:** posterior band (`lf.band`, `lf.truth`).
#
# **Writes:** `temperature.svg` next to this notebook.
#
# **To tweak:** change the capitalised settings at the top of the **Figure** cell and re-run that cell.
#
# **Runs on:** the default `python3` kernel: Python 3.10 or newer with labfigs installed.
#
# **To run it all:** `jupyter nbconvert --to notebook --execute --inplace temperature.ipynb`, which also saves the figure in this notebook.

# %%
from pathlib import Path

import numpy as np

import labfigs as lf

lf.use()

# %% [markdown]
# ## Data
#
# - `x`: positions along the rod in mm, length 200
# - `true_profile`: the true temperature at `x`
# - `draws`: posterior draws, shape `(draws, len(x))`

# %%
RUN = Path("../runs/thermal")

saved = np.load(RUN / "posterior.npz")
x, true_profile, draws = saved["x"], saved["truth"], saved["draws"]

# %% [markdown]
# ## Figure
#
# - `NAME`: file name of the figure, without `.svg`
# - `PANEL_ASPECT`: height of the panel divided by its width
# - `POSTERIOR_LABEL`, `POSTERIOR_COLOUR`: legend entry and colour of the band
# - `LEVEL`: probability inside the band
# - `X_LABEL`, `Y_LABEL`: axis labels, with units

# %%
NAME = "temperature"
PANEL_ASPECT = 0.5
POSTERIOR_LABEL, POSTERIOR_COLOUR = "Posterior", lf.CRIMSON
LEVEL = 0.95
X_LABEL, Y_LABEL = "$x$ (mm)", "$T$ (K)"

fig, ax = lf.subplots(aspect=PANEL_ASPECT)
lf.band(ax, x, draws, level=LEVEL, color=POSTERIOR_COLOUR, label=POSTERIOR_LABEL)
lf.truth(ax, x, true_profile)
ax.set(xlabel=X_LABEL, ylabel=Y_LABEL)
lf.legend_above(ax)
lf.save(fig, NAME)
```

## API

```python
import labfigs as lf

lf.use()                                  # style; LaTeX text when latex is installed
fig, axes = lf.subplots(3, 1, aspect=0.24)  # width 6.5 in; aspect = height / width of each panel's data area
lf.band(ax, x, samples, label="Posterior")  # 95% band from draws, shape (draws, len(x))
lf.paths(ax, x, samples, label="Posterior predictive")  # faint line per draw (100 in a full-width panel, fewer in small ones); level=0.95 adds a grey band under them
lf.paths(ax, x, samples, gradient=True)   # heat-shaded bands: dark within 1 sd of the mean, mid to 2 sd, pale beyond
lf.paths(ax, x, samples, gradient="C1")   # same bands in shades of one colour (any colour), or a ramp name ("viridis")
lf.paths(ax, x, samples, gradient="Kandinsky")  # one colour of a set per band: a series scheme, a Wada number (120), or a list
lf.truth(ax, x, y)                        # the truth: black, labelled "True", above bands and draws
lf.truth(ax, value)                       # a true parameter value: dashed level; vertical=True on a density
lf.reference(ax, value, label="Noise floor")  # grey dashed level or curve under the data: a floor, a baseline
lf.split(ax, 1.0)                         # dashed line between observed and forecast
lf.ribbon(ax, x, samples, label="IFT")    # median line + light 95% band from draws, one per method
lf.data(ax, x, y, label="Sensors")        # black measurement dots
lf.trace(ax, x, y, label="76 Torr")       # dots joined by a line (convergence, sweeps)
lf.intervals(ax, x, samples, shift=dx)    # dot with a vertical 95% bar per x, from draws of shape (draws, len(x))
lf.compare(ax, names, {"IFT": a, "Diffusion": b}, true=values)  # dodged intervals per case and method on a categorical axis, with the true values
lf.marks(ax, x, truth, label="True")      # short black bar at the true value of each x, over the intervals
lf.tag(fig, "Case 3")                     # names the case top-left, when there is one figure per case
lf.legend_above(axes[0])                  # one-row legend above the top panel
lf.legend_above(fig)                      # same, for a grid: labels deduplicated over all panels
lf.legend_above(fig, ncols=2)             # five or more entries wrap onto two rows by themselves; ncols= overrides
fig, axes = lf.cases(names, [ylabel_T, ylabel_k])  # one panel per case and quantity, axes[case, quantity]; sharey=True shares y per quantity
fig, axes = lf.subplots(2, 3, n=5)        # five panels, short bottom row centred; axes comes back flat
lf.density(ax, samples, label="SVI")      # density curve of draws; fill=True for a filled one
lf.shade(ax)                              # grey background marking a panel as different (unconditioned, held out)
lf.signal(ax, t, y, label="Measurement")  # dense measured time series: hairline, open dashes, blue
lf.zoom(top, bottom, 0, 0.1)              # dashed lines from the span [0, 0.1] of top to the panel below it
for y, c in zip(curves, lf.ramp(len(curves), "heat")):  # ordered sweep, dark to light
    ax.plot(x, y, color=c)
lf.heatmap(ax, x, y, z, vmin=0, vmax=1)   # 2D field with its colourbar; z has shape (len(y), len(x))
lf.heatmap(ax, x, y, error, center=0)     # signed field: teal below, white at 0, crimson above; ramp="vik" for another pair
free = lf.region(ax, corners, "C2", label="No coordination")  # polygon outline; dashed=True for a thin dashed one
lf.contours(ax, x, y, z, levels, colors, within=free)  # thin contour lines, clipped to a region
lf.level_key(ax, labels, colors, "Limit:")  # row of boxed level values above the panel, one colour each
lf.ramp(n, ("crimson", "C2"))             # n colours blending from one colour to another
lf.grid(ax)                               # fine major and minor grid for reading values off; save with trim=False
lf.points(ax, x, y, color="C0", label="Setosa")  # scatter markers with a darker edge of their own hue, drawn above lines
fig, ax = lf.subplots(aspect=0.75, subplot_kw={"projection": "3d"})
lf.surface(ax, x, y, z, ramp="sunset", label="Price")  # 3D surface with its colourbar; x, y, z are 2D grids
lf.save(fig, "out/name")                  # fits ticks to the data, trims spines, writes name.svg, warns on checklist 6 and 13; returns the path
lf.notebook(draft, "figures/name", kernel="python3")  # draft cells (# %% and # %% [markdown]) to name.ipynb; same as python -m labfigs
lf.kernel("ift-thermal", "--extra", "ift")  # registers a Jupyter kernel for the uv project in the working directory, with labfigs added
```

`ribbon` and `intervals` take the draws themselves (`level=0.95`); pass `lo, mid, hi`
instead when the interval is already computed, and never call `lf.quantiles` just to unpack
it. `lf.compare` takes draws of shape `(draws, cases)` per method, or a list of draws per
case when the counts differ; `true=` is one value per case, or a single level. `lf.dodge(n)` gives the `shift` for each of `n` methods sharing an x position.
Shifts are in points (5 pt apart; `lf.dodge(n, 8)` for more), so the same call works on a
categorical, a numeric and a log axis. `intervals(connect=True)` joins the dots. `trace`
takes any `ax.plot` option (`ls="--"`, `marker="s"`).

Options: `band(level=0.95, color=, alpha=)`, `paths(color=, alpha=, draws=, lw=, level=None, gradient=False | True | colour | ramp name)`,
`heatmap(ramp="heat", center=None, label=)` plus any `pcolormesh` option,
`subplots(width=, aspect=, sharex=...)`, `save(trim=False)` for axes that should keep full
spines (a grid), `save(formats=("svg", "pdf"))` when LaTeX needs a PDF, `use(tex=False)` for fast drafts.

What `lf.subplots` and `lf.save` do without being asked, so a notebook does not:

- Panel shape. `aspect` is the height over width of each panel's data area. It defaults
  to 0.62 up to three columns and grows with the column count past that. `lf.save` makes
  the figure taller until every panel has that shape, so a legend, tick labels and axis
  labels add height to the figure and never squeeze the data. Never set `figsize`.
- Cases. `lf.cases(names, quantities)` is the grid for several cases (pressures, layouts,
  methods) of the same quantities. Up to three cases sit side by side, with the case as
  the column title and the quantity as the y label. Four or more are stacked as rows about
  3 in wide, with the quantity as the column title, the case as the y label of its row
  and one shared x axis per column. `axes[case, quantity]` either way, so the plotting
  loop is the same. Do not build such a grid from `lf.subplots` by hand.
- Shared x axis. A panel whose x tick labels are hidden by `sharex` loses its x label
  too, so set `xlabel` on every panel and only the bottom one shows it.
- Legend. Five or more entries wrap onto two rows, so the legend stays inside the page.
- Ticks. Every linear or log axis whose ticks were left automatic gets ticks widened to the
  nearest ones enclosing its data, at the step that fits the final panel size. The trimmed
  spine then covers the data (to within 3% of its range). A log axis gets decades, thinned
  to fit the panel, or 1-2-5 steps when the data spans under two decades. So a log axis
  needs only `xscale="log"`: no `trim=False`, hand-set ticks or `minorticks_off()`. Axes
  with explicit ticks and heatmaps are left alone.
- Draws. `lf.paths` shows 100 draws in a panel about 5 in wide and fewer, thinner ones in
  smaller panels, down to 25 in a five-column grid, so single draws stay visible. Set
  `draws=`, `lw=` or `alpha=` only to override: more draws when the tails matter, and a
  band (`lf.band`) when the draws still merge into one stripe.
- Per cent. Write `%` plainly in any label (`"Error (%)"`); it is escaped for LaTeX, and
  `\%` is unescaped when LaTeX is off.
- Warnings. `lf.save` warns when a panel has under 1.4 in of page width, which is five
  columns at text width (checklist 6), when a panel's data area is under 0.5 in tall
  (checklist 6: raise `aspect` or use fewer rows), when two labels overlap (checklist 6), and when one
  x position of an interval plot sits apart and sets the range (checklist 13).

Looks, all set in the one `lf.use` call: `use(font="mono")` sets every label in Courier
(Churkin's look; LaTeX is off, so write plain-text labels), `use(dark=True)` gives a dark
teal page with a soft glow and light ink (slides and posters, not papers),
`use(series="tol_muted")` swaps the colour cycle for a named series scheme.

## Colours

| Name | Use |
|---|---|
| `lf.CRIMSON` | first of the house pair: our method's posterior, bands and fills |
| `lf.TEAL` | second of the house pair: forecast and posterior-predictive draws |
| `lf.REFERENCE` | the baseline method being compared against (grey) |
| `lf.TRUE` | ground truth, always drawn last so it sits on top |

`"crimson"` and `"teal"` are also plain colour names (`color="teal"` is the house teal, not
matplotlib's darker one) and sequential ramps, white through the colour to black:
`lf.ramp(n, "teal")`, `gradient="crimson"`, `ramp="teal"`.

Several series (methods, a sweep over a parameter): use the default colour cycle, `"C0"`,
`"C1"`, ... It runs crimson, teal, then muted blue, orange, green, purple, brown, olive (the
`"seaborn_deep"` scheme, nothing neon), so the first two series always match Fig. 3.11. Give one method the same `"Cn"` in every figure of
a report. Do not pick colours by hand.

An ordered sweep (pressure, noise level, step count) is not a set of methods: colour it with
`lf.ramp(n, name)`, which returns `n` colours from dark to light. Ramps: `"heat"` (maroon to
sand, the default), `"crimson"`, `"teal"`, `"blues"` and `"ylgnbu"` (ColorBrewer), `"viridis"`, `"magma"`, `"plasma"`, `"cividis"`
(colour-blind safe), `"rocket"`, `"mako"`, `"flare"`, `"crest"`. Each stops before its pale
end so thin lines stay readable. The full colormaps are `lf.RAMPS[name][0]`. Any colour works in
place of a ramp name and gives shades of that colour (`lf.ramp(n, "C1")`,
`gradient="tab:blue"`), so single-hue ramps need no entry of their own.

2D fields use `lf.heatmap`: the same ramps, pale for low values and dark for high
(`ramp="heat"` by default; ramps that run dark to light, such as `"mako"` and `"viridis"`,
are flipped to match). Different quantities in one figure take different ramps (a field
and its standard deviation). A signed field (an error, a residual) takes `center=0`, which
switches to the teal-white-crimson map with limits symmetric about the centre. A second signed
quantity in the same figure takes a named diverging scheme, low end first:
`center=0, ramp="vik"` (blue to red-brown), `"broc"`, `"cork"`, `"BrBG"`, `"PRGn"`; `"berlin"`
and `"tofino"` have a dark centre, for `use(dark=True)`. An angle or a phase takes a cyclic
scheme, whose two ends are one colour: `ramp="vikO"` (or `"brocO"`, `"corkO"`) with `vmin`
and `vmax` one period apart. Panels that
are compared against each other share `vmin` and `vmax`. Set `aspect="equal"` on the axes
when x and y are the same physical quantity. Overlay sensors with `lf.data`.

Another set of series colours is one word: `lf.use(series="tol_muted")`, then `"C0"`,
`"C1"`, ... The series schemes, listed in `lf.KINDS["categorical"]`:

- `"seaborn_deep"` (ten colours): the source of the default cycle.
- `"tol_bright"` (seven), `"tol_muted"` (nine), `"tol_medcontrast"` (six, as three
  light and dark pairs): Paul Tol's sets, for a figure that must survive colour-blind reading.
- `"Klimt"` (six), `"Thomas"` (eight), `"Tiepolo"` (eight), `"Hokusai1"` (seven),
  `"Derain"` (seven): painters' palettes, muted, with hues all round the wheel.
- `"Kandinsky"` (four: teal, ochre, grey, near-black): `"C0"` and `"C1"` are two data
  subsets and `"C2"` is the neutral for trend lines (Churkin's layout).

Keep the palest colours of a scheme for fills and thick lines.
`lf.points` gives each marker an edge in a darker shade of its fill (`lf.darker(color)`).
The `"sunset"` ramp (deep purple to orange) holds its lowest tenth at one colour, so a
surface's floor stays flat and only the peaks glow. Under `use(dark=True)`, `heatmap` and
`surface` run dark for low values and bright for high; on white they run pale to dark.

### Colour combinations

Saturation is the thing to control, not hue. Neon colours (fully saturated and bright:
pure yellow, lime, cyan, magenta) are hard on the eyes; a complementary pair is fine once
both colours are muted. Two things that must be told apart take different hues: shades of
one hue (a deep and a pale rose) blur together as band against lines, so keep single-hue
steps for ordered sweeps. Grey is free and goes with anything.

`lf.COMBOS` is the library to pull from, so no notebook needs a hex colour:

- `lf.COMBOS["devon"]`: 46 sequential ColorSchemes.jl schemes by name (`"amp"`, `"oslo"`,
  `"acton"`, `"navia"`, `"grayC"` for a neutral grey, ...), up to nine stops in the source's
  order. These are ramps for ordered data, not series colours. A name works wherever a ramp
  name does: `lf.ramp(n, "acton")`, `ramp="navia"`, `gradient="davos"`. A name that is also
  a plain colour (`"gold"`, `"pink"`, `"sienna"`) means the colour; pass `lf.COMBOS["gold"]`
  for the scheme.
- The other kinds, listed in `lf.KINDS`: `"diverging"` (`"vik"`, `"broc"`, `"cork"`,
  `"BrBG"`, `"PRGn"`, `"berlin"`, `"tofino"`; for `heatmap(center=)`), `"cyclic"` (`"vikO"`,
  `"brocO"`, `"corkO"`; for angles) and `"categorical"` (the ten series schemes above, for
  `lf.use(series=name)`). Every one of these has vividness at most 0.6;
  `examples/schemes.svg` shows them.
- Backup: `lf.COMBOS[120]`, Sanzo Wada's 348 combinations by number, two to four colours
  each. Reach for one only when no named scheme fits.
- `lf.combos(size=None, vivid=1.0, arc=(0, 360), kind=None)`: the combinations of `size`
  colours whose most vivid colour is at most `vivid` and whose hues span between `arc[0]`
  and `arc[1]` degrees (greys and near-blacks count as neutral), of one `kind`
  (`"combination"` for Wada's, `"sequential"`, `"diverging"`, `"cyclic"`, `"categorical"`).
  `lf.combos(kind="categorical")` is the series schemes;
  `examples/colours.svg` shows every scheme by kind, with Wada's last.

Use them through the calls that already exist: `lf.use(series="Klimt")` then `"C0"`,
`"C1"`; `lf.ramp(n, lf.COMBOS["devon"])` for `n` shades, dark first; `ramp=lf.COMBOS["amp"]`
in `heatmap` and `surface`, `gradient=lf.COMBOS["amp"]` in `paths`. Every colour argument
(`lf.ramp`, `ramp=`, `gradient=`, `lf.steps`) takes any of: a colour, a ramp name, a scheme
name, a Wada number, or a list of colours. A series scheme or a Wada combination is put in
order dark to light, so it shades like a ramp. `lf.steps(name, n)` is the `n` colours for
ordered levels (standard-deviation bands, nested intervals): a set's own colours, darkest
first, with blends only when the set has fewer than `n`. When the choice is open,
draw the candidates with `lf.swatches(ax, sets)` (a dict of label to colours) and look
before picking. Two measures back the eye: `lf.vividness(colours)` is the strongest colour
of a set, from 0 (grey) to 1 (neon); stay under about 0.6 for solid fills and thick lines.
`lf.hue_arc(colours)` is the spread of hues in degrees: under 60 is one family, over 120 is
complementary. The house crimson (0.78) and teal (0.57) are about 170 apart; crimson is
only ever a half-transparent band or a thin line, which is what keeps it calm.

## Conventions

- Axis labels are LaTeX math, normalised quantities written as `$x_1/\bar{x}_1$`.
- Spines are trimmed to the outermost ticks, so ticks define the frame. Leave them to
  `lf.save`, log axes included, with one exception: an axis with a natural range
  (`yticks=[-1, 0, 1]`) takes explicit ticks.
- One legend per figure, above the top panel, from `lf.legend_above`; never `ax.legend` or
  `fig.legend`. No figure title; the caption carries it. In a
  grid of cases, `lf.cases` names each case (column title, or row label past three cases). A
  figure that shows one case of several names it with `lf.tag(fig, "76 Torr")`.
- `band` (crimson, α 0.5) is for one posterior; `ribbon` is for several methods overlaid.
- Band or draws. A band is the default for a posterior: a state over the observed window, a
  static field, a parameter over iterations. Draws (`paths`) are for a forecast or rollout
  past the data, where paths branch or drift in phase and a pointwise band would fill space
  no trajectory visits; for a sampler's raw chains against a fitted guide; and when the
  shape of one realisation is the message. This is how Hao's thesis uses the two (Fig. 3.11:
  band up to the split, draws after it). For a smooth single-mode posterior, use draws only
  when asked. One form per distribution: fill reads as inferred, lines as simulated forward.
- Draw order: band, sample paths, truth.
- The truth is always `lf.truth`, never a hand-styled `ax.plot`, `axhline` or `axvline`: a
  solid curve from `x, y`, a dashed level from one value (`vertical=True` on a density).
  When the true value differs per x position (a case each), it is
  `lf.marks(ax, x, truth, label="True")`, which `lf.compare(true=)` draws by itself. A floor
  or baseline level is `lf.reference(ax, value, label=...)`. A reference method's interval across a sweep is
  `ax.axhspan(lo, hi, color=lf.REFERENCE, alpha=0.3, lw=0, label="NUTS")`.
- A panel showing two named quantities gets two titles in their colours:
  `ax.set_title(a, loc="left", color="C1")` and `ax.set_title(b, loc="right", color="C0")`.
- Dense oscillating signal against a measurement: `lf.ribbon(..., lw=0.3)` then `lf.signal`,
  posterior in crimson (teal and the blue measurement do not separate), a zoomed panel beside it.
- Plot large values in scaled units and put the scale in the label
  (`r"Iterations ($\times 10^6$)"`), never matplotlib's offset text.
- `paths` draws the draws alone: a hundred faint lines already show the spread, so an
  interval under them is redundant. Pass `level=0.95` for a neutral grey credible band
  under them (computed from all draws) only when a bound has to be read off the figure.
- Flat draws are the default look. `gradient` is the alternative: it shades each draw by its
  distance from the pointwise mean in standard deviations (three flat bands: under 1, 1 to
  2, over 2).
- Use `gradient=True` when the draws are the only posterior in the panel. Next to another
  method's `ribbon` keep them flat; the dark core hides the ribbon's median line.
- `gradient=True` is the heat ramp. Pass a colour for shades of that colour, or a ramp name.
  Pass a set of separate colours (`gradient="tol_muted"`, `gradient=120`,
  `gradient=("crimson", "teal", "0.6")`) and each band takes one colour of the set, the
  darkest at the centre.
  `color=` is ignored once `gradient` is set. Use the choice to tell quantities apart, one
  per quantity in every figure of a report (conductivity in heat, temperature in the
  method's `"Cn"`). The legend entry takes the 1 sd band's colour; when one label is drawn
  in two palettes across panels, the legend shows the last one.
- Draws hide a ribbon narrower than their spread. When band widths are what is compared,
  every method is a `ribbon`.
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
- A scatter of two measured quantities: `lf.points` per subset, trend lines in the neutral
  colour (solid and dashed, not two colours), `lf.grid`, `lf.save(trim=False)`.
- A 3D surface carries no z label; the colourbar's `label=` names the quantity. Set the view
  with `ax.view_init(elev=30, azim=-60)` and keep ticks sparse.

## From a request to a figure

A request such as "make a graph showing ..." leaves most choices open. Fill them in this
order, which is Churkin's eight steps from a default plot to a finished one. `lf.use()`,
the helpers and `lf.save` already do steps 3, 5, 6 and 7, so the notebook only decides 1,
2, 4 and 8, and those decisions are its settings.

0. Message. Write the one sentence the figure must show, then pick the form:

| What is shown | Form |
|---|---|
| One posterior of a smooth function (a state, a field), against the truth | `band`, truth on top |
| A forecast or rollout past the data | `paths` after `lf.split`, truth on top |
| Several methods on the same function | one `ribbon` per method |
| Parameter estimates over a sweep | `intervals` with `dodge` |
| The same estimates for several cases and methods | `compare` |
| Distribution of a scalar | `density` |
| Convergence, error against cost | `trace` |
| An ordered family of curves | lines coloured by `ramp` |
| A 2D field | `heatmap` (signed: `center=0`) |
| Two measured quantities against each other | `points`, neutral trend line, `grid` |
| A surface whose shape is the message | `surface` |
| A dense signal against a measurement | `ribbon(lw=0.3)` and `signal`, zoomed panel beside it |
| Regions in a plane | `region`, `contours`, `level_key` |

1. Data. Plot only what supports the sentence; the rest goes to the text.
2. Range. Leave limits and ticks to `lf.save`, which frames the data. Set `xlim`, `ylim` or
   ticks only to cut to the part that matters or for a natural range.
3. Font. Never touched in a notebook. Set `width=` to the printed width so nothing is rescaled.
4. Grid and aspect. `lf.grid` when values are read off; `aspect="equal"` when both axes
   share a unit; otherwise trimmed spines and no grid. Each panel's data area is `aspect`
   times as tall as it is wide, whatever the legend and labels take; the default keeps
   panels in shape at any column count, so pass `aspect=` only for a different shape. If tick labels of neighbouring panels touch, cap them
   (`ax.locator_params(nbins=4)`).
5. Colour. Posterior against predictive keeps the house crimson then teal. Other series
   take clearly different hues at moderate saturation (a series scheme:
   `lf.use(series="tol_muted")`); an ordered sweep takes shades of one hue (`lf.ramp(n, colour)`).
   Grey for context and trend lines. Nothing neon.
6. Weight. Markers and lines must read at print size: `lf.points` and the default widths
   are sized for that. Stress a series with weight or a dash pattern before a new colour.
7. Order. Context first, then bands, lines, points, and the truth last.
8. Legend. `lf.legend_above`, entries in reading order: data, then lines.

Then render, look, and repeat. When the request does not say, default to: full text width
(6.5 in), 95% intervals, a band for a posterior, flat draws with no interval under them for a
forecast, axis labels with units, no title.

### When the request goes against the guidelines

The figure is the user's, so a poor request still gets its figure, exactly as asked. Check
at three points:

1. The set, before drawing. Read every request together: the same data asked for twice, a
   figure per case for many cases, the number of panels one paragraph of text has to
   carry, one colour per method across the figures, a caption for every figure.
2. Each request, before drawing, against the table below.
3. Each rendered figure, against the checklist. A warning from `lf.save` is a flag:
   report it or remove its cause, never silence it.

Report one line for the set and one line for every request, flagged or not, next to the
figures and in the write-up when there is one:

- Passed: the items checked. "`exp-alex`: items 1 to 6, 9 to 14 checked, pass."
- Flagged: the item, what the reader loses, the alternative that complies.

A request with no line was not checked. Offer the alternative; build it only when asked.
One thing is added without asking: a figure that goes into a report gets a caption line
saying what the line, the band and the markers are, and the level of the band.

| Request | Item | Offer instead |
|---|---|---|
| Methods superimposed whose bands coincide | 1, 3 | one panel per method, or plot the difference or the band width |
| The same data in two figures | 2 | one figure in the text, the other to an appendix |
| A figure per case, for many cases | 1, 2 | one or two representative cases, the rest to an appendix |
| More than three cases side by side at text width | 6 | `lf.cases`, which stacks them as rows; fewer cases; or a wider page |
| One case sets the range for the rest | 13 | a log axis, or that case in its own panel |
| Many coloured lines in one panel | 3, 9 | the mass in grey, colour for the few that matter |
| A colour per series that changes between figures | 10 | one `"Cn"` per method across the report |
| Rainbow, neon, a pie chart, 3D for flat data | 11, 12, 17 | a ramp, a muted set, bars, a heatmap |
| A figure with no caption | 5 | a caption that says what to see |

Example: "Made `exp-three` as asked. It goes against item 3: the three bands coincide and
read as one, so the pinch at the sensors is lost. One panel per method would show it."

## Design checklist

Adapted from Andrey Churkin's BeautifulFigures (https://github.com/AndreyChurkin/BeautifulFigures)
and his two tutorials: principles (https://youtu.be/i-HAjex6VtM) and the full process
(https://youtu.be/KQ6Zg9B5Mxs).

Message

1. Story first. Say in one sentence what the figure shows, then plot only the data that
   supports that sentence. Never plot data because it exists.
2. For every element ask: is it needed, can it be simpler, can it go? Detail moves to the
   text or an appendix.
3. Many lines: draw the mass in `lf.REFERENCE` or at low alpha and colour only the few that
   matter. No spaghetti plots. No second y axis piled with bars and lines.
4. Readers scan from the top-left in a Z, so the legend or key sits at the top and panels
   read left to right.
5. The caption says what to see: which panel is the good case, what each colour and marker
   means, and the level of every band (95% unless set). Every axis and every colourbar has
   a label with its unit.

Page

6. Size for the page. Set `lf.subplots(width=)` to the printed width (6.5 in for full text
   width, 3.5 in for one column of a two-column paper) and include the figure unscaled, so
   the 10 pt text prints at body-text size. No text below the template's smallest font
   (about 8 pt). A panel whose data area is flatter than about 0.5 in is cramped: the
   curves become slivers. `lf.save` grows the figure to stop this and warns if it remains.
7. Check it in the real layout: compile the manuscript, view the page at 100% and compare
   figure text with caption text, then zoom out. Readable without zooming in is the bar.
8. One style per paper: every figure from labfigs, panels of the same size, few line and
   marker types.

Colour

9. Design in black, grey and line styles first. Then add one colour, two at most.
10. One data subset keeps one colour in every figure of a manuscript. A new colour appears
    only when it carries new information.
11. No neon: nothing fully saturated and bright, no yellow on white. Complementary pairs
    are fine when both colours are muted (`lf.vividness` under about 0.6); it is high
    saturation that tires the eye, not opposite hues. Red reads as wrong and green as
    right, so use them only when that is meant. The house crimson is vivid as a solid:
    keep it a half-transparent band or a thin line, never a solid fill beside the teal.
    Colours that must be told apart differ in hue, not only in lightness.
12. Ordered data takes a ramp, never a rainbow. Every `lf.ramp` runs dark to light, so the
    order survives greyscale printing. A gradient should mean something (crimson is the
    tight or worse end).

Craft

13. Limits frame the data that matters: set `xlim` and `ylim` around the points with an even
    margin and let trend lines run off the edge.
14. Legend compact, above the axes, never over the data; data entries first, then lines.
15. Points sit above lines. When the points are the subject, the trend line is neutral
    (`lf.REFERENCE`).
16. Both axes in the same unit: `aspect="equal"`. Values meant to be read off: `lf.grid(ax)`.
17. No pie charts; use bars. No 3D unless the shape of the surface is the message, and then
    `lf.surface`; any other 2D field is `lf.heatmap`.

Output

18. Vector only. `lf.save` writes SVG, which goes straight into Word, slides, web pages and
    Inkscape for hand touch-ups (legend spacing, an arrow, a note). LaTeX cannot include SVG
    directly: pass `formats=("svg", "pdf")` there. Never save a PNG as the figure.
19. Rasterise only a layer too dense to draw as vectors, inside an otherwise vector figure
    (`lf.heatmap`, `lf.surface` and gradient `lf.paths` do this). Check the journal proof: some journals rasterise figures.
20. Plan for several rounds: render, look, fix, place in the manuscript, come back the next
    day, ask a colleague.

## Running

The library and Jupyter are installed in the default `python3`:

```bash
python3 -m labfigs <scratch>/draft.py figures/name.ipynb
```

```bash
jupyter nbconvert --to notebook --execute --inplace figures/name.ipynb
```

A notebook runs on the kernel named inside it, in VS Code, JupyterLab and `nbconvert` alike.
The default, `python3`, is right when the notebook needs only labfigs and what the default
`python3` has. A notebook that imports a project's own code needs that project's
environment. In a `uv` project, register a kernel once from the project root (anything
after the name is passed to `uv run`), then name it when making the notebook:

```bash
python3 -m labfigs kernel ift-thermal --no-sync --extra ift
```

```bash
python3 -m labfigs <scratch>/draft.py report/figures.ipynb ift-thermal
```

The kernel starts through `uv run --with-editable labfigs --with ipykernel`, so it is the
project's own environment with labfigs added, and nothing is installed into the project.
Check that it works before handing over: the `nbconvert` run above must pass on it. Read
the versions for the header's `**Runs on:**` line from the project's environment, never
from memory. `jupyter kernelspec list` shows the kernels already registered.

Worked examples in the library, each a notebook to copy from:
`examples/duffing_311.ipynb` reproduces thesis Fig. 3.11,
`examples/field.ipynb` shows gradient draws and a 2D field in every ramp,
`examples/palettes.ipynb` shows every ramp as a sweep, `examples/hao_figures.ipynb` has the
other thesis figure types: parameter intervals over a sweep (Fig. 3.2), densities per method
(Fig. 6.2, 4.6), a grid with shaded panels (Fig. 4.9), convergence traces (Fig. 6.7).
`examples/hao_replicas.ipynb` redraws three whole figures: a zoomed second row (thesis
Fig. 6.3) and dense signal against measurement (filter paper Figs. 14 and 16).
`examples/feasible_regions.ipynb` draws feasible regions with nested limit contours, a level
key and a fine grid. `examples/churkin.ipynb` redraws Churkin's two examples: an edged
scatter with trend lines in the mono font, and a dark 3D surface in the sunset ramp.
`examples/schemes.ipynb` draws the diverging, cyclic and series schemes, each in use.
`examples/colours.svg` shows every colour option with its name: open it to pick one by eye.
`examples/defaults.ipynb` shows what needs no code: intervals straight from draws on a log
axis with fitted ticks, `lf.compare` over cases, a case tag, a `%` label and a warning from `lf.save`.
`examples/design_steps.ipynb` draws Churkin's eight steps from a default plot to a finished one.

## Not covered yet

Corner plots, filled contour plots, and one-call recipes for whole figure types. Ask before
inventing a style for these.
