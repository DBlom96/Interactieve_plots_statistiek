import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy.stats import f as f_dist

from utils.explanation_utils import show_explanation
from utils.streamlit_utils import load_css, page_header, apply_dark_style
from utils.constants import *

st.set_page_config(
    page_title="F-verdeling",
    initial_sidebar_state="expanded",
    layout="wide"
)

# ----------------------------------
# CSS
# ----------------------------------
load_css()

# ----------------------------------
# PARAMETERS
# ----------------------------------
page_header("📊 F-verdeling", "Continue kansverdelingen")

with st.sidebar:
    st.header("Parameters")
    df1    = st.number_input(r"Aantal vrijheidsgraden $\text{df}_1$:", min_value=1, value=5)
    df2    = st.number_input(r"Aantal vrijheidsgraden $\text{df}_2$:", min_value=1, value=5)
    method = st.selectbox("Visualisatiemethode:", ["Plot", "Kritiek gebied", "p-waarde"])

    alpha, toets = None, None
    if method != "Plot":
        alpha = st.number_input(r"Significantieniveau $\alpha$:", min_value=0.001, value=0.05)
        toets = st.number_input(r"Toetsingsgrootheid $f$:", value=2.0, min_value=0.0)

# ----------------------------------
# COMPUTATIONS
# ----------------------------------
x_max = f_dist.ppf(0.99, dfn=df1, dfd=df2)
x     = np.linspace(1e-6, x_max, 10_000)
y     = f_dist.pdf(x, df1, df2)

linkergrens = rechtergrens = p_waarde = None
inside_critical = False

if method != "Plot":
    linkergrens   = f_dist.ppf(alpha / 2,       dfn=df1, dfd=df2)
    rechtergrens  = f_dist.ppf(1 - alpha / 2,   dfn=df1, dfd=df2)
    p_value_left  = f_dist.cdf(toets,            dfn=df1, dfd=df2)
    p_value_right = 1 - f_dist.cdf(toets,        dfn=df1, dfd=df2)
    p_waarde      = min(p_value_left, p_value_right)
    inside_critical = (toets < linkergrens) or (toets > rechtergrens)

# ----------------------------------
# STAT CARDS
# ----------------------------------
if method == "Kritiek gebied":
    st.markdown(f"""
    <div class="stats-row-3">
      <div class="stat-card acceptatie">
        <span class="stat-label">Acceptatiegebied</span>
        <span class="stat-value">[{linkergrens:.4f}, {rechtergrens:.4f}]</span>
        <span class="stat-desc">Middelste {int(100 * (1 - alpha))}% van de verdeling</span>
      </div>
      <div class="stat-card kritiek">
        <span class="stat-label">Kritiek gebied</span>
        <span class="stat-value">[0, {linkergrens:.4f}) en ({rechtergrens:.4f}, &infin;)</span>
        <span class="stat-desc">Extreem grote of kleine variantieverhouding</span>
      </div>
      <div class="stat-card {"kritiek" if inside_critical else "acceptatie"}">
        <span class="stat-label">Toetsingsgrootheid</span>
        <span class="stat-value">f = {toets:.4f}</span>
        <span class="stat-desc">Ligt {"wel" if inside_critical else "niet"} in het kritieke gebied</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

elif method == "p-waarde":
    significant = p_waarde < alpha / 2
    st.markdown(f"""
    <div class="stats-row-3">
      <div class="stat-card bi">
        <span class="stat-label">Toetsingsgrootheid</span>
        <span class="stat-value">f = {toets:.4f}</span>
        <span class="stat-desc">Ligt {"wel" if significant else "niet"} in het kritieke gebied</span>
      </div>
      <div class="stat-card pvalue">
        <span class="stat-label">p-waarde</span>
        <span class="stat-value">{p_waarde:.4f}</span>
        <span class="stat-desc">min(<i>P(F &le; f), P(F &ge; f)</i>)</span>
      </div>
      <div class="stat-card kritiek">
        <span class="stat-label">Significantieniveau</span>
        <span class="stat-value">&alpha; = {alpha:.4f}</span>
        <span class="stat-desc">Vastgestelde kans op type-I fout</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------
# HELPERS
# ----------------------------------
def add_interval_bar(ax, x_max, linker, rechter, y):
    """Coloured acceptance / critical bar just below the x-axis."""

    segments = [
        (0,       linker,   CRITICAL_COLOR,   ""),
        (linker,  rechter,  ACCEPTABLE_COLOR, "Acceptatiegebied"),
        (rechter, x_max,    CRITICAL_COLOR,   "Kritiek gebied"),
    ]
    for l, r, color, label in segments:
        ax.plot([l, r], [bar_y, bar_y], color=color, linewidth=8,
                solid_capstyle="butt", clip_on=False)
        if label:
            ax.text((l + r) / 2, bar_y - 2.8 * tick_h, label,
                    ha="center", va="top", fontsize=ANNOTATION_FONT_SIZE,
                    color=color, fontfamily="JetBrains Mono")

    for xv in [0, linker, rechter, x_max]:
        ax.plot([xv, xv], [bar_y - tick_h, bar_y + tick_h],
                color=PLOT_FONT_COLOR, linewidth=1, clip_on=False)


# ----------------------------------
# FIGURE
# ----------------------------------
fig, ax = plt.subplots(figsize=(10, 5))

bar_y  = -0.055 * max(y)
tick_h = 0.018 * max(y)
ytext = bar_y - 2.8 * tick_h
plt.ylim(bottom=3*bar_y, top=1.1*max(y))

# Base curve — always drawn
ax.plot(x, y, color=H0_COLOR, linewidth=2.5,
        label=rf"$F(\mathrm{{df}}_1={df1},\;\mathrm{{df}}_2={df2})$")

if method == "Kritiek gebied":
    # Shade critical tails
    ax.fill_between(x, y, where=(x <= linkergrens),  color=CRITICAL_COLOR,   alpha=0.2)
    ax.fill_between(x, y, where=(x >= rechtergrens), color=CRITICAL_COLOR,   alpha=0.2)

    # Boundary lines
    for xv, color, lbl in [
        (linkergrens,  CRITICAL_COLOR,   rf"$f_{{\alpha/2}} = {linkergrens:.4f}$"),
        (rechtergrens, CRITICAL_COLOR,   rf"$f_{{1-\alpha/2}} = {rechtergrens:.4f}$"),
        (toets,        H0_COLOR,         rf"$f = {toets:.4f}$"),
    ]:
        ax.plot([xv, xv], [0, f_dist.pdf(xv, df1, df2)],
                color=color, linewidth=1.5, linestyle="--", label=lbl)
    
    # Add annotation for the test statistics
    ax.text(toets,  ytext, f"$f = {toets:.2f}$",
            ha="center", va="top", fontsize=ANNOTATION_FONT_SIZE,
            color=H0_COLOR, fontfamily="JetBrains Mono")

    add_interval_bar(ax, x_max, linkergrens, rechtergrens, y)

elif method == "p-waarde":
    # Shade the tail corresponding to the p-value
    if p_value_left < p_value_right:
        ax.fill_between(x, y, where=(x <= toets), color=BETA_COLOR,     alpha=0.25,
                        label=rf"p-waarde $= {p_waarde:.4f}$")
    else:
        ax.fill_between(x, y, where=(x >= toets), color=BETA_COLOR,     alpha=0.25,
                        label=rf"p-waarde $= {p_waarde:.4f}$")

    # Shade both critical tails
    ax.fill_between(x, y, where=(x <= linkergrens),  color=CRITICAL_COLOR, alpha=0.25,
                    label=rf"Kritiek gebied $(\alpha={alpha})$")
    ax.fill_between(x, y, where=(x >= rechtergrens), color=CRITICAL_COLOR, alpha=0.25)

    # Boundary lines
    ax.plot([toets, toets], [0, f_dist.pdf(toets, df1, df2)],
            color=H0_COLOR,      linewidth=1.5, linestyle=":",
            label=rf"$f = {toets:.4f}$")
    ax.plot([linkergrens,  linkergrens],  [0, f_dist.pdf(linkergrens,  df1, df2)],
            color=CRITICAL_COLOR, linewidth=1.5, linestyle="--",
            label=rf"$f_{{\alpha/2}} = {linkergrens:.4f}$")
    ax.plot([rechtergrens, rechtergrens], [0, f_dist.pdf(rechtergrens, df1, df2)],
            color=CRITICAL_COLOR, linewidth=1.5, linestyle="--",
            label=rf"$f_{{1-\alpha/2}} = {rechtergrens:.4f}$")
    
    # Add annotation for the test statistics
    ax.text(toets,  ytext, f"$f = {toets:.2f}$",
            ha="center", va="top", fontsize=ANNOTATION_FONT_SIZE,
            color=H0_COLOR, fontfamily="JetBrains Mono")


# Title
if method == "Plot":
    apply_dark_style(
        fig=fig, ax=ax,
        title=rf"Kansdichtheidsfunctie — $F(\mathrm{{df}}_1={df1},\;\mathrm{{df}}_2={df2})$",
        xlabel=r"$x$",
        ylabel=r"Kansdichtheid $f(x)$"
    )
else:
    apply_dark_style(fig=fig, ax=ax, xlabel=r"$x$", ylabel=r"Kansdichtheid $f(x)$")
    ax.text(0.5, 1.02,
            rf"$f = {toets:.4f}$ ligt in het ",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=TITLE_FONT_SIZE, color=PLOT_FONT_COLOR,
            fontfamily="JetBrains Mono")
    ax.text(0.5, 1.02,
            " kritieke gebied" if inside_critical else " acceptatiegebied",
            transform=ax.transAxes, ha="left", va="bottom",
            fontsize=TITLE_FONT_SIZE,
            color=CRITICAL_COLOR if inside_critical else ACCEPTABLE_COLOR,
            fontfamily="JetBrains Mono")

plt.tight_layout(pad=2.5)
st.pyplot(fig, use_container_width=True)
plt.close(fig)

# ----------------------------------
# EXPLANATION
# ----------------------------------
explanation_title = "📚 De F-verdeling"
explanation_markdown = r"""
## 💡 Intuïtie

De **$F$-verdeling** beschrijft de verhouding van twee onafhankelijke steekproefvarianties. Ze wordt
gebruikt bij de **toets voor gelijke varianties** van twee onafhankelijke normaal verdeelde populaties:

$$
    H_0: \sigma_1^2 = \sigma_2^2 \quad \text{versus} \quad H_1: \sigma_1^2 \neq \sigma_2^2
$$

De toetsingsgrootheid is:
$$
    F = \frac{S_1^2}{S_2^2}
$$

Onder $H_0$ volgt $F$ een $F(\text{df}_1, \text{df}_2)$-verdeling met $\text{df}_i = n_i - 1$.

- $F \approx 1$: varianties lijken op elkaar — consistent met $H_0$.
- $F$ ver van $1$: één steekproef is veel meer gespreid — bewijs tegen $H_0$.

## 📌 Eigenschappen

- Altijd positief ($F \geq 0$) en rechtsscheef.
- Verwachtingswaarde: $E[F] = \dfrac{\text{df}_2}{\text{df}_2 - 2}$ (voor $\text{df}_2 > 2$).
- De toets is **tweezijdig**: zowel een te hoge als een te lage $f$-waarde leidt tot verwerping.

## 🧪 Beslissingsregels

**Via het kritieke gebied** — verwerp $H_0$ als:
$$
    f < F_{\alpha/2;\,\text{df}_1,\,\text{df}_2}
    \quad\text{of}\quad
    f > F_{1-\alpha/2;\,\text{df}_1,\,\text{df}_2}
$$

**Via de p-waarde** — verwerp $H_0$ als:
$$
    p = \min\!\bigl(P(F \leq f),\; P(F \geq f)\bigr) < \alpha/2
$$

## 🔢 Rekenvoorbeeld

Twee sluipschutterteams ($n = m = 10$) schieten op een doelwit. De steekproefvarianties zijn
$s_A^2 \approx 3.33$ en $s_B^2 \approx 48.06$, dus:

$$
    f = \frac{s_A^2}{s_B^2} = \frac{3.33}{48.06} \approx 0.069
$$

Bij $\alpha = 0.05$ en $\text{df}_1 = \text{df}_2 = 9$: kritiek gebied $[0,\, 0.248) \cup (4.026,\, \infty)$.
Omdat $f \approx 0.069 < 0.248$ verwerpen we $H_0$ — de spreiding van de twee teams verschilt
significant.
"""

show_explanation(explanation_title, explanation_markdown)