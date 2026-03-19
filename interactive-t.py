import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy.stats import norm, t

from utils.explanation_utils import show_explanation
from utils.streamlit_utils import load_css, page_header, apply_dark_style
from utils.constants import *

st.set_page_config(
    page_title="Student's t-verdeling",
    initial_sidebar_state="expanded",
    layout="wide"
)

# ----------------------------------
# CSS
# ----------------------------------
load_css()

BG_COLOR = "#1a1f2e"

# ----------------------------------
# PARAMETERS
# ----------------------------------
page_header("📊 Student's t-verdeling", "Continue kansverdelingen")

with st.sidebar:
    st.header("Parameters")
    df    = st.number_input(r"Aantal vrijheidsgraden (df):", min_value=1, max_value=100, value=1, step=1)
    alpha = st.number_input(r"Significantieniveau $\alpha$:", min_value=1e-6, max_value=1.0, value=0.05)

# ----------------------------------
# COMPUTATIONS
# ----------------------------------
confidence = 1 - alpha
conf_pct   = int(100 * confidence)
x          = np.linspace(-4, 4, 1_000)
normal_pdf = norm.pdf(x)
t_pdf      = t.pdf(x, df=df)
z_crit     = norm.ppf(1 - alpha / 2)
t_crit     = t.ppf(1 - alpha / 2, df=df)

# Example computation (rekenvoorbeeld)
n_ex    = df + 1
t_score = 12 / (24 / np.sqrt(n_ex))
reject  = abs(t_score) > t_crit

# ----------------------------------
# STAT CARDS
# ----------------------------------
st.markdown(f"""
<div class="stats-row-3">
  <div class="stat-card bi">
    <span class="stat-label">Kritieke waarden N(0,1)</span>
    <span class="stat-value">&plusmn;{z_crit:.4f}</span>
    <span class="stat-desc">{conf_pct}%-betrouwbaarheidsinterval</span>
  </div>
  <div class="stat-card pi">
    <span class="stat-label">Kritieke waarden t(df={df})</span>
    <span class="stat-value">&plusmn;{t_crit:.4f}</span>
    <span class="stat-desc">{conf_pct}%-betrouwbaarheidsinterval</span>
  </div>
  <div class="stat-card beta">
    <span class="stat-label">Verschil kritieke waarden</span>
    <span class="stat-value">{t_crit - z_crit:.4f}</span>
    <span class="stat-desc"><i>t</i>-verdeling heeft bredere staarten</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------
# HELPERS
# ----------------------------------
def fill_tails(ax, x, y, crit, color):
    """Shade both tails beyond ±crit."""
    for mask in [x < -crit, x > crit]:
        ax.fill_between(x, y, where=mask, color=color, alpha=0.2)


def crit_vlines(ax, x, pdf_func, crit, color, df=None):
    """Draw dashed vertical lines at ±crit up to the PDF height."""
    for xv in [-crit, crit]:
        yv = pdf_func(xv) if df is None else pdf_func(xv, df)
        ax.plot([xv, xv], [0, yv], color=color, linewidth=1.5, linestyle="--")

# ----------------------------------
# FIGURE
# ----------------------------------
fig, ax = plt.subplots(figsize=(10, 5))

# Shaded tails
fill_tails(ax, x, normal_pdf, z_crit, H0_COLOR)
fill_tails(ax, x, t_pdf,      t_crit, H1_COLOR)

# Critical value lines
crit_vlines(ax, x, norm.pdf, z_crit, H0_COLOR)
if df >= 3:   # avoid very tall lines for low df
    crit_vlines(ax, x, t.pdf, t_crit, H1_COLOR, df=df)

# Curves
ax.plot(x, normal_pdf, color=H0_COLOR, linewidth=2.5,
        label=r"Normale verdeling $\mathcal{N}(0,1)$")
ax.plot(x, t_pdf,      color=H1_COLOR, linewidth=2.5,
        label=rf"$t$-verdeling $(\mathrm{{df}}={df})$")

apply_dark_style(
    fig=fig,
    ax=ax,
    title=rf"Kansdichtheidsfuncties - $\mathcal{{N}}(0,1)$ en $t(\mathrm{{df}}={df})$",
    xlabel=r"$x$",
    ylabel=r"Kansdichtheid $f(x)$"
)
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))


plt.tight_layout(pad=2.0)
st.pyplot(fig, width="stretch")
plt.close(fig)

# ----------------------------------
# EXPLANATION
# ----------------------------------
explanation_title = "📚 Student's t-verdeling"
explanation_markdown = rf"""
## 📌 Wat laat de grafiek zien?

De $t$-verdeling ontstaat wanneer je het gemiddelde van een steekproef wilt vergelijken met een
populatiegemiddelde, maar de **populatiestandaardafwijking $\sigma$ onbekend** is. Je schat $\sigma$
dan met de steekproefstandaardafwijking $s$, wat extra onzekerheid introduceert. Die onzekerheid
vertaalt zich naar **dikkere staarten**: extreme uitkomsten zijn waarschijnlijker dan onder de
standaardnormale verdeling.

Hoe kleiner $n$, hoe kleiner df $= n - 1$ en hoe dikker de staarten. Voor df $\geq 30$ is het
verschil met $\mathcal{{N}}(0,1)$ verwaarloosbaar klein.

## ❓ Wanneer gebruik je de $t$-verdeling?

| Situatie | Gebruik |
|---|---|
| $\sigma$ bekend | $\mathcal{{N}}(0,1)$ |
| $\sigma$ onbekend, $n \geq 30$ | Beide acceptabel |
| $\sigma$ onbekend, $n < 30$ | $t$-verdeling verplicht |
| Populatie niet normaal, $n < 30$ | Niet-parametrische toets |

## 🧮 Toetsingsgrootheid

Bij een $t$-toets ($H_0: \mu = \mu_0$ versus $H_1: \mu \neq \mu_0$) is de toetsingsgrootheid:

$$
    t = \frac{{\bar{{x}} - \mu_0}}{{s / \sqrt{{n}}}}
$$

We verwerpen $H_0$ als $|t| > t_{{\text{{crit}}}}$, waarbij:

$$
    t_{{\text{{crit}}}} = t_{{1 - \alpha/2,\; \text{{df}}={df}}} = {t_crit:.4f}
$$

## 🔢 Rekenvoorbeeld

$n = {n_ex}$ proefpersonen, toets of reactietijd verschilt van $\mu_0 = 300$ ms,
met $\bar{{x}} = 312$ ms en $s = 24$ ms.

$$
    t = \frac{{312 - 300}}{{24 / \sqrt{{{n_ex}}}}}
      = \frac{{12}}{{{24 / np.sqrt(n_ex):.4f}}}
      = {t_score:.4f}
$$

{"✅" if not reject else "❌"} $|t| = {abs(t_score):.4f}$
{"<" if not reject else ">"} $t_{{\text{{crit}}}} = {t_crit:.4f}$
$\;\Rightarrow\;$ $H_0$ **{"niet verwerpen" if not reject else "verwerpen"}**:
{"geen" if not reject else "wel een"} significant verschil gevonden.
"""

show_explanation(explanation_title, explanation_markdown)