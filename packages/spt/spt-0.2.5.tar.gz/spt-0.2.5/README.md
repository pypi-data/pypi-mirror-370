# spt

[![PyPi](https://img.shields.io/pypi/v/spt?logo=pypi&logoColor=white&label=PyPI)](https://pypi.org/project/spt/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/spt?logo=pypi&logoColor=white&color=blue&label=PyPI%20downloads)](https://pypi.org/project/spt)
[![Requires Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg?logo=python&logoColor=white)](https://python.org/downloads)

<pre style="text-align: center;">
           _
 ___ _ __ | |_
/ __| '_ \| __|
\__ \ |_) | |_
|___/ .__/ \__|
    |_|
</pre>

spt: A Scientific Matplotlib plot rcParams configuration template Python package.

- **Repo**: [GitHub](https://github.com/Bit-Part-Young/spt) | [Gitee](https://gitee.com/yangsl306/spt)

---

## Installation

- via pip:

```bash
pip install -U spt

# install spt and examples dependencies
pip install ".[examples]"
```

- via git:

```bash
pip install git+https://github.com/Bit-Part-Young/spt.git
# or
pip install git+https://gitee.com/yangsl306/spt.git
```

- via source code:

```bash
git clone https://github.com/Bit-Part-Young/spt.git
# or
git clone https://gitee.com/yangsl306/spt.git

cd spt

# create virtual environment
python -m venv venv
source venv/bin/activate

pip install .
# or
pip install -r requirements.txt

# editable mode
pip install -e .
```

---

## Usage

Full example codes can be found in [examples](https://github.com/Bit-Part-Young/spt/tree/master/examples) folder.

---

### fonts

- **Times New Roman**: Copy `TimesNewRoman*.ttf` fonts to `~/.fonts` or `~/.local/share/fonts` or matplotlib font path in specific conda env, then remove matplotlib cache, relogin.

```bash
cp fonts/TimesNewRoman*.ttf ~/.fonts
# or
cp fonts/TimesNewRoman*.ttf ~/.local/share/fonts
# or
cp fonts/TimesNewRoman*.ttf <conda_env>/lib/pythonXXX/site-packages/matplotlib/mpl-data/fonts/ttf/

# remove matplotlib cache
rm -rf ~/.cache/matplotlib

# check fonts
fc-list lang:en | grep -i "Times New Roman"
```

- **Chinese**: Copy `SimHei.ttf` font to `~/.fonts` or `~/.local/share/fonts` or matplotlib font path in specific conda env, backup original matplotlibrc file, copy modified matplotlibrc file to `mpl-data` path, then remove matplotlib cache, relogin.

```bash
cp fonts/SimHei.ttf ~/.fonts
# or
cp fonts/SimHei.ttf ~/.local/share/fonts
# or
cp fonts/SimHei.ttf <conda_env>/lib/pythonXXX/site-packages/matplotlib/mpl-data/fonts/ttf/

# backup matplotlibrc file
cp fonts/matplotlibrc <conda_env>/lib/pythonXXX/site-packages/matplotlib/mpl-data/

# remove matplotlib cache
rm -rf ~/.cache/matplotlib

# check fonts
fc-list lang:zh | grep -i "SimHei"
```

---

`matplotlibrc` modification:

```bash
# Original
font.sans-serif: DejaVu Sans, Bitstream Vera Sans, Computer Modern Sans Serif, Lucida Grande, Verdana, Geneva, Lucid, Arial, Helvetica, Avant Garde, sans-serif
axes.unicode_minus: True  # use Unicode for the minus symbol rather than hyphen.  See

# Modification
font.sans-serif: DejaVu Sans, Bitstream Vera Sans, Computer Modern Sans Serif, Lucida Grande, Verdana, Geneva, Lucid, Arial, Helvetica, Avant Garde, sans-serif, SimHei, Times New Roman, Times
axes.unicode_minus: False  # use Unicode for the minus symbol rather than hyphen.  See
```

---

### set_plot_params()

- code snippets (complete script: [plot.py](https://github.com/Bit-Part-Young/spt/blob/master/examples/plot.py)):

```python
import matplotlib.pyplot as plt
from spt.plot_params import set_plot_params

...

set_plot_params()

fig, ax = plt.subplots()

...

```

---

Figure:

![sin.png](./assets/figures/sin.png)

---

### set_roman_plot_params()

- code snippets (complete script: [plot_roman.py](https://github.com/Bit-Part-Young/spt/blob/master/examples/plot_roman.py)):

```python
import matplotlib.pyplot as plt
from spt.plot_params import set_roman_plot_params

...

set_roman_plot_params()

fig, ax = plt.subplots()

...

```

---

Figure:

![sin_roman.png](./assets/figures/sin_roman.png)

---

- 3d plot code snippets (complete script: [plot_3d.py](https://github.com/Bit-Part-Young/spt/blob/master/examples/plot_3d.py)):

```python
import matplotlib.pyplot as plt
from spt.plot_params import set_roman_plot_params

...

set_roman_plot_params(
    axes_labelpad=15,
    legend_handletextpad=0.0,
    legend_fontsize=22,
    savefig_bbox="standard",
)

fig, ax = plt.subplots(subplot_kw={"projection": "3d"}, figsize=(10, 8))

...

```

---

Figure:

![scatter_3d.png](./assets/figures/scatter_3d.png)

---

### Chinese characters plot

- code snippets (complete script: [plot_zh.py](https://github.com/Bit-Part-Young/spt/blob/master/examples/plot_zh.py))

```python
import matplotlib.pyplot as plt
from spt.plot_params import set_roman_plot_params

...

set_roman_plot_params()

fig, ax = plt.subplots()

ax.plot(x, y, label="正弦函数")

ax.set(xlabel="x", ylabel="y")

# legend 字体设置为 SimHei
ax.legend(prop={"family": "SimHei"})

...

```

---

Figure

![sin_zh.png](./assets/figures/sin_zh.png)

---

## Scientific Figure Examples

- Example 1 (complete script: [dot_line_plot.py](https://github.com/Bit-Part-Young/spt/blob/master/examples/dot-line-plot/dot_line_plot.py)):

Figure:

![dot_line.png](./assets/figures/dot_line.png)

---

- Example 2 (complete script: [phase_stability_Nb3Si_plot.py](https://github.com/Bit-Part-Young/spt/blob/master/examples/phase-stability-Nb3Si-plot/phase_stability_Nb3Si_plot.py)):

Figure:

![substitution_energy_Nb3Si.png](./assets/figures/substitution_energy_Nb3Si.png)

---

- Example 3 (complete script: [b_fit_cal.py](https://github.com/Bit-Part-Young/spt/blob/master/examples/fit-cal-b-plot/b_fit_cal.py)):

Figure:

![b_fit_cal.png](./assets/figures/b_fit_cal.png)

---

- Example 4 (complete script: [xrd_plot.py](https://github.com/Bit-Part-Young/spt/blob/master/examples/xrd-plot/xrd_plot.py)):

Figure:

![xrd.png](./assets/figures/xrd.png)

- Example 5 (complete script: [ternary_plot.py](https://github.com/Bit-Part-Young/spt/blob/master/examples/ternary-plot/ternary_plot.py)):

Figure:

![AlMoZr_ternary.png](./assets/figures/AlMoZr_ternary.png)

- Example 5 (complete script: [ternary_convex_hull.py](https://github.com/Bit-Part-Young/spt/blob/master/examples/ternary-convex-hull/ternary_convex_hull.py)):

Figure:

![AlMoZr_convex_hull.png](./assets/figures/AlMoZr_convex_hull.png)
