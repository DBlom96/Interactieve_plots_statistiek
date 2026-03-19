import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy.stats import chi2

from utils.explanation_utils import show_explanation
from utils.streamlit_utils import load_css, page_header, apply_dark_style
from utils.constants import *

st.set_page_config(
    page_title="Chikwadraatverdeling",
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
page_header("📊 Chikwadraatverdeling", "Continue kansverdelingen")

with st.sidebar:
    st.header("Parameters")
    df     = st.number_input(r"Vrijheidsgraden (df):", min_value=1, value=5)
    method = st.selectbox("Visualisatiemethode:", ["Plot", "Kritiek gebied", "p-waarde"])

    alpha, toets = None, None
    if method != "Plot":
        alpha = st.number_input(r"Significantieniveau $\alpha$:", min_value=0.001, value=0.05)
        toets = st.number_input(r"Toetsingsgrootheid $\chi^2$:", value=2.0, min_value=0.0)

# ----------------------------------
# COMPUTATIONS
# ----------------------------------
x_max = max(10, df + 5 * np.sqrt(df))
x     = np.linspace(0, x_max, 10_000)
y     = chi2.pdf(x, df)

grens, p_waarde = None, None
if method != "Plot":
    grens    = chi2.ppf(1 - alpha, df)
    p_waarde = 1 - chi2.cdf(toets, df=df)

vg_label = "vrijheidsgraad" if df == 1 else "vrijheidsgraden"

# ----------------------------------
# STAT CARDS
# ----------------------------------
if method == "Kritiek gebied":
    in_critical = toets > grens
    st.markdown(f"""
    <div class="stats-row-3">
      <div class="stat-card acceptatie">
        <span class="stat-label">Acceptatiegebied</span>
        <span class="stat-value">[0, {grens:.4f}]</span>
        <span class="stat-desc">Laagste {int(100 * (1 - alpha))}% van de verdeling</span>
      </div>
      <div class="stat-card kritiek">
        <span class="stat-label">Kritiek gebied</span>
        <span class="stat-value">({grens:.4f}, &infin;)</span>
        <span class="stat-desc">Top {int(100 * alpha)}% van de verdeling</span>
      </div>
      <div class="stat-card {"kritiek" if in_critical else "acceptatie"}">
        <span class="stat-label">Toetsingsgrootheid</span>
        <span class="stat-value">&chi;&sup2; = {toets:.4f}</span>
        <span class="stat-desc">Ligt {"wel" if in_critical else "niet"} in het kritieke gebied</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

elif method == "p-waarde":
    significant = p_waarde < alpha
    st.markdown(f"""
    <div class="stats-row-3">
      <div class="stat-card bi">
        <span class="stat-label">Toetsingsgrootheid</span>
        <span class="stat-value">&chi;&sup2; = {toets:.4f}</span>
        <span class="stat-desc">Ligt {"wel" if significant else "niet"} in het kritieke gebied</span>
      </div>
      <div class="stat-card pvalue">
        <span class="stat-label">p-waarde</span>
        <span class="stat-value">{p_waarde:.4f}</span>
        <span class="stat-desc">Kans op uitkomst &ge; &chi;&sup2; = {toets:.3f}</span>
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
def add_interval_bar(ax, x_max, grens, y):
    """Draw the coloured acceptance/critical bar below the x-axis."""
    

    ax.plot([0, grens],  [bar_y, bar_y], color=ACCEPTABLE_COLOR, linewidth=8,
            solid_capstyle="butt", clip_on=False)
    ax.plot([grens, x_max], [bar_y, bar_y], color=CRITICAL_COLOR, linewidth=8,
            solid_capstyle="butt", clip_on=False)

    # Tick marks at boundary
    for xv in [0, grens, x_max]:
        ax.plot([xv, xv], [bar_y - tick_h, bar_y + tick_h],
                color=PLOT_FONT_COLOR, linewidth=1, clip_on=False)

    # Labels
    ax.text((0 + grens) / 2, bar_y - 2.8 * tick_h, "Acceptatiegebied",
            ha="center", va="top", fontsize=ANNOTATION_FONT_SIZE,
            color=ACCEPTABLE_COLOR, fontfamily="JetBrains Mono")
    ax.text((grens + x_max) / 2, bar_y - 2.8 * tick_h, "Kritiek gebied",
            ha="center", va="top", fontsize=ANNOTATION_FONT_SIZE,
            color=CRITICAL_COLOR, fontfamily="JetBrains Mono")



# ----------------------------------
# FIGURE
# ----------------------------------
fig, ax = plt.subplots(figsize=(10, 5))

bar_y  = -0.055 * max(y)
tick_h = 0.018 * max(y)
ytext = bar_y - 2 * tick_h
plt.ylim(bottom=3*bar_y, top=1.1*max(y))

# Base curve — always drawn
ax.plot(x, y, color=H0_COLOR, linewidth=2.5,
        label=rf"$\chi^2(\mathrm{{df}}={df})$")

if method == "Kritiek gebied":
    # Shade acceptance and critical regions
    # ax.fill_between(x, y, where=(x <= grens), color=ACCEPTABLE_COLOR, alpha=0.15)
    ax.fill_between(x, y, where=(x >= grens), color=CRITICAL_SHADE_COLOR)

    # Critical value line
    ax.plot([grens, grens], [0, chi2.pdf(grens, df)],
            color=CRITICAL_COLOR, linewidth=1.5, linestyle="--",
            label=rf"$\chi^2_{{\mathrm{{crit}}}} = {grens:.4f}$")

    # Test statistic line
    ax.plot([toets, toets], [0, chi2.pdf(toets, df)],
            color=H0_COLOR, linewidth=1.5, linestyle=":",
            label=rf"$\chi^2 = {toets:.4f}$")
    ax.text(toets,  ytext, f"$\chi^2 = {toets:.2f}$",
            ha="center", va="top", fontsize=ANNOTATION_FONT_SIZE,
            color=H0_COLOR, fontfamily="JetBrains Mono")

    add_interval_bar(ax, x_max, grens, y)

elif method == "p-waarde":
    # Shade p-value region
    ax.fill_between(x, y, where=(x >= toets),  color=BETA_COLOR,     alpha=0.25,
                    label=rf"p-waarde $= {p_waarde:.4f}$")
    # Shade critical region on top
    ax.fill_between(x, y, where=(x >= grens),  color=CRITICAL_COLOR, alpha=0.25,
                    label=rf"Kritiek gebied $(\alpha={alpha})$")

    # Lines
    ax.plot([toets, toets], [0, chi2.pdf(toets, df)],
            color=H0_COLOR,      linewidth=1.5, linestyle=":",
            label=rf"$\chi^2 = {toets:.4f}$")
    ax.plot([grens, grens], [0, chi2.pdf(grens, df)],
            color=CRITICAL_COLOR, linewidth=1.5, linestyle="--",
            label=rf"$\chi^2_{{\mathrm{{crit}}}} = {grens:.4f}$")
    
    # Test statistic line
    ax.plot([toets, toets], [0, chi2.pdf(toets, df)],
            color=H0_COLOR, linewidth=1.5, linestyle=":",
            label=rf"$\chi^2 = {toets:.4f}$")
    ax.text(toets,  ytext, f"$\chi^2 = {toets:.2f}$",
            ha="center", va="top", fontsize=ANNOTATION_FONT_SIZE,
            color=H0_COLOR, fontfamily="JetBrains Mono")


# Title — two-color for method != "Plot"
if method == "Plot":
    apply_dark_style(
        fig=fig, ax=ax,
        title=rf"Kansdichtheidsfunctie — $\chi^2(\mathrm{{df}}={df})$",
        xlabel=r"$x$",
        ylabel=r"Kansdichtheid $f(x)$"
    )
else:
    apply_dark_style(
        fig=fig, ax=ax,
        xlabel=r"$x$",
        ylabel=r"Kansdichtheid $f(x)$"
    )
    in_critical = (toets > grens) if grens is not None else False
    ax.text(0.5, 1.02,
            rf"$\chi^2 = {toets:.4f}$ ligt in het ",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=TITLE_FONT_SIZE, color=PLOT_FONT_COLOR,
            fontfamily="JetBrains Mono")
    ax.text(0.5, 1.02,
            " kritieke gebied" if in_critical else " acceptatiegebied",
            transform=ax.transAxes, ha="left", va="bottom",
            fontsize=TITLE_FONT_SIZE,
            color=CRITICAL_COLOR if in_critical else ACCEPTABLE_COLOR,
            fontfamily="JetBrains Mono")

plt.tight_layout(pad=2.5)
st.pyplot(fig, use_container_width=True)
plt.close(fig)

# ----------------------------------
# EXPLANATION
# ----------------------------------
explanation_title = "📚 De chikwadraatverdeling"
explanation_markdown = rf"""
## 📌 Eigenschappen

De **$\chi^2$-verdeling** is een continue, altijd positieve ($\chi^2 \geq 0$) en niet-symmetrische
verdeling. De vorm hangt volledig af van het aantal **vrijheidsgraden** (df):
- Voor kleine df is de verdeling sterk scheef naar rechts.
- Voor grote df benadert ze een normale verdeling.
- Verwachtingswaarde: $E[X] = \text{{df}}$, variantie: $\text{{Var}}(X) = 2\,\text{{df}}$.

## 🧪 Toepassingen

- **Goodness-of-fit**: komen waargenomen frequenties overeen met een verwachte verdeling?
- **Onafhankelijkheidstoets**: zijn twee categorische variabelen onafhankelijk van elkaar?
- **Variantietoets**: wijkt een waargenomen variantie af van een verwachte waarde?

## 🎨 Visualisatiemethoden

- **Plot** — toont de kansdichtheidsfunctie van $\chi^2(\text{{df}}={df})$.
- **Kritiek gebied** — toont het acceptatiegebied en het kritieke gebied bij significantieniveau
  $\alpha$. De toetsingsgrootheid wordt gemarkeerd.
- **p-waarde** — arceer het oppervlak rechts van de toetsingsgrootheid; dat oppervlak is de
  p-waarde.
"""

show_explanation(explanation_title, explanation_markdown)