# labfigs

One plotting library for the lab's figures, with a house style modelled on the figures of [Kairui Hao's thesis](https://hammer.purdue.edu/articles/thesis/Information_Field_Theory_Approach_to_Uncertainty_Quantification_for_Differential_Equations_Theory_Algorithms_and_Applications/25665570) and a design checklist adapted from Andrey Churkin's [BeautifulFigures](https://github.com/AndreyChurkin/BeautifulFigures/).
It is matplotlib and seaborn underneath: one style call, plus helpers for the elements that keep coming back (posterior bands, sample draws, method ribbons, intervals, heatmaps, colour ramps).
A Claude Code skill in `skill/` teaches an agent to use it, so figures look the same in every project.

## Install

```bash
git clone https://github.com/Jacob-Liam-Albaugh/labfigs.git
```

```bash
pip install -e labfigs
```

Text is set with LaTeX when `latex` is on your PATH, and with matplotlib's own math text otherwise.

In a `uv` project, use it without adding it to the project's dependencies. Register a Jupyter kernel once from the project root (it is the project's environment with labfigs added), then pick that kernel in the notebook:

```bash
python3 -m labfigs kernel my-project
```

## Use

A figure lives in a Jupyter notebook, so anyone can change a setting by hand and re-run one cell. The smallest one:

```python
import numpy as np
import labfigs as lf

lf.use()
x = np.linspace(0, 1, 200)
truth = np.sin(2 * np.pi * x)
samples = truth * np.random.default_rng(0).normal(1, 0.2, (500, 1))

fig, ax = lf.subplots()
lf.paths(ax, x, samples, label="Posterior draws")
lf.truth(ax, x, truth)
ax.set(xlabel="$x$", ylabel="$u$", xticks=[0, 0.5, 1], yticks=[-2, -1, 0, 1, 2])
lf.legend_above(ax)
lf.show(fig)
```

`lf.show` puts the finished figure under the cell and writes nothing, so you can look and change it first. Save from the next cell:

```python
lf.save(fig, "out/first")                                 # out/first.svg
lf.save(fig, "out/first", formats=("svg", "pdf", "png"))  # all three
```

SVG is the default. Add `"pdf"` for LaTeX and `"png"` (300 dpi) for a place that cannot take a vector file. The rules:

- Call `lf.use()` once, before any figure. Do not set fonts, sizes or `rcParams` yourself.
- Make figures with `lf.subplots`, end the drawing cell with `lf.show(fig)`, and save with `lf.save` in a cell of its own.
- Use the house pair (`lf.CRIMSON`, then `lf.TEAL`), `lf.REFERENCE` and `lf.TRUE`, the cycle (`"C0"`, `"C1"`, ...) for methods, and `lf.ramp(n, name)` for ordered sweeps. `lf.use(series="tol_muted")` swaps the cycle for a named scheme. No hex colours.
- If a figure needs something the library lacks, add a helper to `labfigs.py` instead of writing it in your notebook.
- Lay a notebook out like the ones in `examples/`: a header saying what the figure shows, a data cell, then per figure a draw cell with its settings in capitals at the top and `lf.show` as the last line, and a one-line save cell after it. `FORMATS` in the setup cell names the file types every save cell writes.

The full list of helpers, options and conventions is in [skill/SKILL.md](skill/SKILL.md).

## Examples

Each notebook in `examples/` shows its figures under the cells that draw them and writes them as SVG next to itself. Open one in JupyterLab or VS Code, change a capitalised setting at the top of a figure's cell and re-run that cell. Figures credited to Kairui Hao or Andrey Churkin are not copies of theirs: each is remade with labfigs on synthetic data, and the credit links to the original.

Run them all without opening them, which also saves the figures inside each notebook (needs `jupyter`, plus `scipy` and `scikit-learn` for two of them):

```bash
for notebook in examples/*.ipynb; do jupyter nbconvert --to notebook --execute --inplace "$notebook"; done
```

The house layout: a posterior band, predictive draws, the truth and a forecast split (`duffing_311.ipynb`). Remade with labfigs after Fig. 3.11 of [Hao's thesis](https://hammer.purdue.edu/articles/thesis/Information_Field_Theory_Approach_to_Uncertainty_Quantification_for_Differential_Equations_Theory_Algorithms_and_Applications/25665570):

![Posterior and posterior predictive](examples/duffing_311.svg)

A 2D field in every ramp (`field.ipynb`):

![Fields](examples/field.svg)

Regions with nested contours, a level key and a fine grid (`feasible_regions.ipynb`). Remade with labfigs after Churkin's [main example](https://github.com/AndreyChurkin/BeautifulFigures/tree/main/01_main_simple_example):

![Feasible regions](examples/feasible_regions.svg)

A 3D surface on the dark page (`churkin.ipynb`). Remade with labfigs after Churkin's [3D price surface](https://github.com/AndreyChurkin/BeautifulFigures/tree/main/02_3d_price_surface):

![3D surface](examples/surface_3d.svg)

The eight design steps from the matplotlib default to the finished figure (`design_steps.ipynb`). Remade with labfigs after the iterative design process figure in Churkin's [BeautifulFigures README](https://github.com/AndreyChurkin/BeautifulFigures#readme):

![Design steps](examples/design_steps.svg)

The rest are in [examples/](examples): [gradient draws](examples/gradient_draws.svg), [ramps as line sweeps](examples/palettes.svg), [parameter intervals](examples/intervals.svg), [densities](examples/densities.svg), [shaded panels](examples/shaded_panels.svg), [convergence traces](examples/convergence.svg), three of Hao's figures remade with labfigs ([6.3](examples/fig_6_3.svg) of the [thesis](https://hammer.purdue.edu/articles/thesis/Information_Field_Theory_Approach_to_Uncertainty_Quantification_for_Differential_Equations_Theory_Algorithms_and_Applications/25665570), [14](examples/fig_14.svg) and [16](examples/fig_16.svg) of the [filter paper](https://arxiv.org/abs/2407.16502)), an [edged scatter](examples/edged_scatter.svg) after Churkin's [main example](https://github.com/AndreyChurkin/BeautifulFigures/tree/main/01_main_simple_example), the [diverging, cyclic and series schemes](examples/schemes.svg) and [every colour option by name](examples/colours.svg).

## Design checklist

Before a figure goes into a paper:

- Say in one sentence what it shows, and plot only the data that supports that sentence.
- Set `lf.subplots(width=)` to the printed width and include the figure unscaled, so the text prints at body-text size. No text below about 8 pt.
- Check it in the compiled manuscript at 100%: font size against the caption, line weights, marker sizes, legend.
- Design in black, grey and line styles first, then add one or two colours. Keep one colour per data subset across every figure.
- No neon. Complementary colours are fine at moderate saturation (every series scheme in `lf.KINDS["categorical"]` is); colours that must be told apart differ in hue, not only in lightness.
- Fade the mass of lines to grey and colour only the few that matter.
- Use a ramp for ordered data, never a rainbow. Red reads as wrong and green as right.
- Put the legend at the top, and write a caption that says what to see.
- Vector first: `lf.save` writes SVG. Add `"pdf"` for LaTeX, and `"png"` only where a vector file cannot go.
- Avoid pie charts. Use 3D only when the surface's shape is the message (`lf.surface`).
- Expect several rounds of render, look, fix.

The full checklist is in [skill/SKILL.md](skill/SKILL.md).

## References

- Kairui Hao, *Information Field Theory Approach to Uncertainty Quantification for Differential Equations: Theory, Algorithms and Applications*, PhD thesis, Purdue University ([Purdue Hammer](https://hammer.purdue.edu/articles/thesis/Information_Field_Theory_Approach_to_Uncertainty_Quantification_for_Differential_Equations_Theory_Algorithms_and_Applications/25665570), [ProQuest](https://www.proquest.com/docview/3235007366)), and his [filter paper](https://arxiv.org/abs/2407.16502): the source of the house style (colours, trimmed spines, legend above).
- Andrey Churkin, [BeautifulFigures](https://github.com/AndreyChurkin/BeautifulFigures/) (MIT): the source of the design checklist, the fine grid (`lf.grid`), the feasible-region example layout, the sunset ramp, the dark page, edged markers (`lf.points`) and the 3D surface (`lf.surface`). His two tutorials cover the [principles](https://youtu.be/i-HAjex6VtM) and the [whole process](https://youtu.be/KQ6Zg9B5Mxs), from plotting code to the manuscript page.
- [ColorSchemes.jl](https://github.com/JuliaGraphics/ColorSchemes.jl) (MIT), as listed in the [Plots.jl docs](https://docs.juliaplots.org/stable/generated/colorschemes/): the named schemes in `lf.COMBOS` (sequential, diverging, cyclic, series), among them Fabio Crameri's [Scientific colour maps](https://doi.org/10.5281/zenodo.1243862) (MIT), cmocean (MIT) and ColorBrewer (Apache 2.0).
- Paul Tol, [colour schemes](https://sronpersonalpages.nl/~pault/) (BSD 3-Clause): the colour-blind-safe series schemes `tol_bright`, `tol_muted` and `tol_medcontrast`.
- Michael Waskom, [seaborn](https://seaborn.pydata.org) (BSD 3-Clause): the `seaborn_deep` series scheme, which the default cycle continues with after crimson and teal.
- Blake R. Mills, [MetBrewer](https://github.com/BlakeRMills/MetBrewer) (CC0): the series schemes `Klimt`, `Thomas`, `Tiepolo`, `Hokusai1`, `Derain` and `Kandinsky`.
- Sanzo Wada, *A Dictionary of Color Combinations*, browsed at [colors.elwyn.co](https://colors.elwyn.co) and taken from Matt DesLauriers' [dataset](https://github.com/mattdesl/dictionary-of-colour-combinations) (MIT): the 348 numbered combinations kept in `lf.COMBOS` as a backup.

## Licence

labfigs is under the [MIT licence](LICENSE). The licences of the material it adapts are in [NOTICE](NOTICE). Figures made with it can be published without restriction; a paper that uses one of Crameri's schemes (listed in NOTICE: `devon`, `vik`, `acton` and others) should cite his [Scientific colour maps](https://doi.org/10.5281/zenodo.1243862).

## Claude Code skill

Link the skill once and Claude Code will use the library whenever it plots:

```bash
ln -s "$PWD/labfigs/skill" ~/.claude/skills/labfigs
```
