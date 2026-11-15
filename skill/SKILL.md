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
6. Figures are vector only: `lf.save` writes SVG. Look at every figure before reporting it
   as done: `rsvg-convert -w 1600 name.svg -o <scratch>/name.png`, then open that preview.
   The preview is for checking, never the deliverable.
7. Run the design checklist below on every figure that goes into a paper or report.

## API

```python
import labfigs as lf

lf.use()                                  # style; LaTeX text when latex is installed
fig, axes = lf.subplots(3, 1, aspect=0.24)  # width 6.5 in; aspect = panel height / width
lf.band(ax, x, samples, label="Posterior")  # 95% band from draws, shape (draws, len(x))
lf.paths(ax, x, samples, label="Posterior predictive")  # faint line per draw (100 shown); level=0.95 adds a grey band under them
lf.paths(ax, x, samples, gradient=True)   # heat-shaded bands: dark within 1 sd of the mean, mid to 2 sd, pale beyond
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
lf.points(ax, x, y, color="C0", label="Setosa")  # scatter markers with a darker edge of their own hue, drawn above lines
fig, ax = lf.subplots(aspect=0.75, subplot_kw={"projection": "3d"})
lf.surface(ax, x, y, z, ramp="sunset", label="Price")  # 3D surface with its colourbar; x, y, z are 2D grids
lf.save(fig, "out/name")                  # trims spines, writes name.svg
```

`lf.quantiles(samples)` returns `(lo, median, hi)`, ready to unpack into `ribbon` or
`intervals`. `lf.dodge(n)` gives the `shift` for each of `n` methods sharing an x position;
`intervals(connect=True)` joins the dots.

Options: `band(level=0.95, color=, alpha=)`, `paths(color=, alpha=, draws=100, level=None, gradient=False | True | colour | ramp name)`,
`heatmap(ramp="heat", center=None, label=)` plus any `pcolormesh` option,
`subplots(width=, aspect=, sharex=...)`, `save(trim=False)` for axes that should keep full
spines (log axes), `save(formats=("svg", "pdf"))` when LaTeX needs a PDF, `use(tex=False)` for fast drafts.

Looks, all set in the one `lf.use` call: `use(font="mono")` sets every label in Courier
(Churkin's look; LaTeX is off, so write plain-text labels), `use(dark=True)` gives a dark
teal page with a soft glow and light ink (slides and posters, not papers),
`use(series=lf.PURPLE_TEAL)` or `use(series=lf.MUTED)` swaps the colour cycle.

## Colours

| Name | Use |
|---|---|
| `lf.POSTERIOR` | our method's posterior, bands and fills |
| `lf.PREDICTIVE` | forecast and posterior-predictive draws |
| `lf.REFERENCE` | the baseline method being compared against (grey) |
| `lf.TRUE` | ground truth, always drawn last so it sits on top |

Several series (methods, a sweep over a parameter): use the default colour cycle, `"C0"`,
`"C1"`, ... It runs crimson, teal, then muted blue, orange, green, purple, brown, olive (seaborn's
`deep` set, nothing neon), so the first two series always match Fig. 3.11. Give one method the same `"Cn"` in every figure of
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
mauve, blue-grey), via `lf.use(series=lf.MUTED)`. Its first two are the house pair with the
saturation turned down: opposite hues that still sit quietly side by side. The other five
are close in hue, so use them for light/dark variants of one method, not for telling
methods apart.

`lf.PURPLE_TEAL` is Churkin's three-colour set: purple, grey, teal. `"C0"` and `"C2"` are two
data subsets and `"C1"` is the neutral for trend lines, via `lf.use(series=lf.PURPLE_TEAL)`.
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

`lf.COMBOS` is the library to pull from, so no script needs a hex colour:

- `lf.COMBOS[120]`: Sanzo Wada's 348 combinations by number, two to four colours each.
- `lf.COMBOS["devon"]`: 38 single-family ColorSchemes.jl schemes by name (`"amp"`,
  `"oslo"`, `"sienna"`, ...), up to nine stops in the source's order. These are ramps for
  ordered data, not series colours.
- `lf.combos(size=None, vivid=1.0, arc=(0, 360))`: the combinations of `size` colours whose
  most vivid colour is at most `vivid` and whose hues span between `arc[0]` and `arc[1]`
  degrees (greys and near-blacks count as neutral). `lf.combos(2, vivid=0.5, arc=(120, 360))`
  is the muted complementary pairs; `examples/combos.svg` shows everything under 0.5.

Use them through the calls that already exist: `lf.use(series=lf.COMBOS[44])` then `"C0"`,
`"C1"`; `lf.ramp(n, lf.COMBOS["devon"])` for `n` shades, dark first; `ramp=lf.COMBOS["amp"]`
in `heatmap` and `surface`, `gradient=lf.COMBOS["amp"]` in `paths`. When the choice is open,
draw the candidates with `lf.swatches(ax, sets)` (a dict of label to colours) and look
before picking. Two measures back the eye: `lf.vividness(colours)` is the strongest colour
of a set, from 0 (grey) to 1 (neon); stay under about 0.6 for solid fills and thick lines.
`lf.hue_arc(colours)` is the spread of hues in degrees: under 60 is one family, over 120 is
complementary. The house crimson (0.78) and teal (0.57) are about 170 apart; crimson is
only ever a half-transparent band or a thin line, which is what keeps it calm.

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
- `paths` draws the draws alone: a hundred faint lines already show the spread, so an
  interval under them is redundant. Pass `level=0.95` for a neutral grey credible band
  under them (computed from all draws) only when a bound has to be read off the figure.
- Flat draws are the default look. `gradient` is the alternative: it shades each draw by its
  distance from the pointwise mean in standard deviations (three flat bands: under 1, 1 to
  2, over 2).
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
- A scatter of two measured quantities: `lf.points` per subset, trend lines in the neutral
  colour (solid and dashed, not two colours), `lf.grid`, `lf.save(trim=False)`.
- A 3D surface carries no z label; the colourbar's `label=` names the quantity. Set the view
  with `ax.view_init(elev=30, azim=-60)` and keep ticks sparse.

## From a request to a figure

A request such as "make a graph showing ..." leaves most choices open. Fill them in this
order, which is Churkin's eight steps from a default plot to a finished one. `lf.use()`,
the helpers and `lf.save` already do steps 3, 5, 6 and 7, so the script only decides 1, 2,
4 and 8.

0. Message. Write the one sentence the figure must show, then pick the form:

| What is shown | Form |
|---|---|
| One posterior of a function, against the truth | `band` or `paths`, truth on top |
| Several methods on the same function | one `ribbon` per method |
| Parameter estimates over a sweep | `intervals` with `dodge` |
| Distribution of a scalar | `density` |
| Convergence, error against cost | `trace` |
| An ordered family of curves | lines coloured by `ramp` |
| A 2D field | `heatmap` (signed: `center=0`) |
| Two measured quantities against each other | `points`, neutral trend line, `grid` |
| A surface whose shape is the message | `surface` |
| A dense signal against a measurement | `ribbon(lw=0.3)` and `signal`, zoomed panel beside it |
| Regions in a plane | `region`, `contours`, `level_key` |

1. Data. Plot only what supports the sentence; the rest goes to the text.
2. Range. Set `xlim` and `ylim` around the data with an even margin, and explicit ticks.
3. Font. Never touched in a script. Set `width=` to the printed width so nothing is rescaled.
4. Grid and aspect. `lf.grid` when values are read off; `aspect="equal"` when both axes
   share a unit; otherwise trimmed spines and no grid.
5. Colour. Posterior against predictive keeps the house crimson then teal. Other series
   take clearly different hues at moderate saturation (`lf.MUTED`, or a set from
   `lf.combos(n, vivid=0.5)`); an ordered sweep takes shades of one hue (`lf.ramp(n, colour)`).
   Grey for context and trend lines. Nothing neon.
6. Weight. Markers and lines must read at print size: `lf.points` and the default widths
   are sized for that. Stress a series with weight or a dash pattern before a new colour.
7. Order. Context first, then bands, lines, points, and the truth last.
8. Legend. `lf.legend_above`, entries in reading order: data, then lines.

Then render, look, and repeat. When the request does not say, default to: full text width
(6.5 in), 95% intervals, flat draws with no interval under them, axis labels with units, no title.

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
   means. Every axis and every colourbar has a label with its unit.

Page

6. Size for the page. Set `lf.subplots(width=)` to the printed width (6.5 in for full text
   width, 3.5 in for one column of a two-column paper) and include the figure unscaled, so
   the 10 pt text prints at body-text size. No text below the template's smallest font
   (about 8 pt).
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
key and a fine grid. `examples/churkin.py` redraws Churkin's two examples: an edged scatter
with trend lines in the mono font, and a dark 3D surface in the sunset ramp.
`examples/combos.py` draws the muted combinations in `lf.COMBOS` as labelled swatches.

## Not covered yet

Corner plots, filled contour plots, and one-call recipes for whole figure types. Ask before
inventing a style for these.
