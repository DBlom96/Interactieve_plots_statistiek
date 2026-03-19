import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy.stats import uniform

from utils.explanation_utils import show_explanation
from utils.streamlit_utils import load_css, page_header, apply_dark_style
from utils.constants import *

st.set_page_config(
    page_title="Uniforme verdeling",
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
page_header("📊 Uniforme verdeling", "Continue kansverdeling")

with st.sidebar:
    st.header("Parameters")
    a_param = st.number_input(r"Ondergrens $a$:", value=0.0, step=0.5)
    b_param = st.number_input(r"Bovengrens $b$:", value=1.0, step=0.5)

    if a_param >= b_param:
        st.error(r"$a$ moet kleiner zijn dan $b$.")
        st.stop()

    st.divider()
    st.header("Kansberekening")
    show_mode = st.selectbox(
        "Arceer gebied:",
        [r"Geen", r"P(X ≤ b)", r"P(X ≥ a)", r"P(a ≤ X ≤ b)"]
    )

    lo_val, hi_val, prob = None, None, None

    if show_mode == r"P(X ≤ b)":
        hi_val = st.number_input(r"$b$:", value=float(round((a_param + b_param) / 2, 2)), step=0.1)
        prob   = uniform.cdf(hi_val, loc=a_param, scale=b_param - a_param)

    elif show_mode == r"P(X ≥ a)":
        lo_val = st.number_input(r"$a$:", value=float(round((a_param + b_param) / 2, 2)), step=0.1)
        prob   = 1 - uniform.cdf(lo_val, loc=a_param, scale=b_param - a_param)

    elif show_mode == r"P(a ≤ X ≤ b)":
        lo_val = st.number_input(r"$a$:", value=float(round(a_param + (b_param - a_param) / 3, 2)), step=0.1)
        hi_val = st.number_input(r"$b$:", value=float(round(a_param + 2 * (b_param - a_param) / 3, 2)), step=0.1)
        if lo_val < hi_val:
            prob = uniform.cdf(hi_val, loc=a_param, scale=b_param - a_param) \
                 - uniform.cdf(lo_val, loc=a_param, scale=b_param - a_param)
        else:
            st.warning(r"$a$ moet kleiner zijn dan $b$.")

    st.divider()
    view_mode = st.selectbox(label="Weergave:", options=["PDF", "CDF", "PDF + CDF"])

# ----------------------------------
# COMPUTATIONS
# ----------------------------------
mu_val    = (a_param + b_param) / 2
sigma_val = (b_param - a_param) / np.sqrt(12)
padding   = (b_param - a_param) * 0.35

x     = np.linspace(a_param - padding, b_param + padding, 1000)
pdf_y = uniform.pdf(x, loc=a_param, scale=b_param - a_param)
cdf_y = uniform.cdf(x, loc=a_param, scale=b_param - a_param)

# ----------------------------------
# STAT CARDS
# ----------------------------------
prob_label = f"<i>{show_mode}</i>" if show_mode != "Geen" else "Geen gebied geselecteerd"
st.markdown(f"""
<div class="stats-row-4">
  <div class="stat-card alpha">
    <span class="stat-label">Gemiddelde {to_lowercase(MEAN_HTML)}</span>
    <span class="stat-value">{mu_val:.2f}</span>
    <span class="stat-desc">Centrum van de verdeling</span>
  </div>
  <div class="stat-card beta">
    <span class="stat-label">Standaardafwijking {to_lowercase(STD_HTML)}</span>
    <span class="stat-value">{sigma_val:.4f}</span>
    <span class="stat-desc">({to_lowercase(UNIF_WIDTH_HTML)}) / &radic; 12</span>
  </div>
  <div class="stat-card power">
    <span class="stat-label">Breedte {to_lowercase(UNIF_WIDTH_HTML)}</span>
    <span class="stat-value">{b_param - a_param:.2f}</span>
    <span class="stat-desc">Lengte van het interval</span>
  </div>
  <div class="stat-card bi">
    <span class="stat-label">Kans</span>
    <span class="stat-value">{f"{prob:.4f}" if prob is not None else "&mdash;"}</span>
    <span class="stat-desc">{prob_label}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------
# HELPERS
# ----------------------------------
def add_shading(ax, x, a, b, mode, lo, hi, prob):
    """Fill the selected probability region on a PDF axes."""
    scale = b - a
    height = 1.0 / scale  # constant PDF height

    if mode == r"P(X ≤ b)" and hi is not None:
        xf = x[(x >= a) & (x <= hi)]
        ax.fill_between(xf, uniform.pdf(xf, loc=a, scale=scale),
                        color=FILL_COLOR, alpha=0.5,
                        label=rf"$P(X \leq {hi:.2f}) = {prob:.4f}$")
        ax.plot([hi, hi], [0, height], color=H0_COLOR, linewidth=1.4, linestyle=":")

    elif mode == r"P(X ≥ a)" and lo is not None:
        xf = x[(x >= lo) & (x <= b)]
        ax.fill_between(xf, uniform.pdf(xf, loc=a, scale=scale),
                        color=FILL_COLOR, alpha=0.5,
                        label=rf"$P(X \geq {lo:.2f}) = {prob:.4f}$")
        ax.plot([lo, lo], [0, height], color=H0_COLOR, linewidth=1.4, linestyle=":")

    elif mode == r"P(a ≤ X ≤ b)" and lo is not None and hi is not None and lo < hi:
        xf = x[(x >= lo) & (x <= hi)]
        ax.fill_between(xf, uniform.pdf(xf, loc=a, scale=scale),
                        color=FILL_COLOR, alpha=0.5,
                        label=rf"$P({lo:.2f} \leq X \leq {hi:.2f}) = {prob:.4f}$")
        ax.plot([lo, lo], [0, height], color=H0_COLOR, linewidth=1.4, linestyle=":")
        ax.plot([hi, hi], [0, height], color=H0_COLOR, linewidth=1.4, linestyle=":")


def add_cdf_markers(ax, x, a, b, mode, lo, hi):
    """Mark the queried CDF value(s) with a dot and dashed drop-lines."""
    scale = b - a
    points = []
    if mode == r"P(X ≤ b)" and hi is not None:
        points = [(hi, uniform.cdf(hi, loc=a, scale=scale))]
    elif mode == r"P(X ≥ a)" and lo is not None:
        points = [(lo, uniform.cdf(lo, loc=a, scale=scale))]
    elif mode == r"P(a ≤ X ≤ b)" and lo is not None and hi is not None:
        points = [
            (lo, uniform.cdf(lo, loc=a, scale=scale)),
            (hi, uniform.cdf(hi, loc=a, scale=scale)),
        ]

    for xv, yv in points:
        ax.plot([xv, xv], [0, yv], color=H0_COLOR, linewidth=1.2, linestyle=":")
        ax.plot([x[0], xv], [yv, yv], color=H0_COLOR, linewidth=1.2, linestyle=":")
        ax.scatter([xv], [yv], color=H0_COLOR, s=55, zorder=5)


def styled_legend(ax):
    ax.legend(
        fontsize=TICK_FONT_SIZE,
        facecolor=BG_COLOR,
        edgecolor=BG_COLOR,
        labelcolor=PLOT_FONT_COLOR,
        framealpha=0.85
    )

# ----------------------------------
# FIGURE
# ----------------------------------
show_pdf = view_mode in ("PDF", "PDF + CDF")
show_cdf = view_mode in ("CDF", "PDF + CDF")

nrows = 2 if view_mode == "PDF + CDF" else 1
fig, axes = plt.subplots(nrows, 1, figsize=(10, 5 * nrows))
fig.patch.set_facecolor(BG_COLOR)

if nrows == 1:
    axes = [axes]

ax_pdf = axes[0] if show_pdf else None
ax_cdf = axes[1] if view_mode == "PDF + CDF" else (axes[0] if show_cdf else None)

# --- PDF axes ---
if show_pdf:
    ax_pdf.plot(x, pdf_y, color=H0_COLOR, linewidth=2.5,
                label=rf"$f(x)$ — Uniform$(a={a_param},\, b={b_param})$")
    ax_pdf.plot([mu_val, mu_val], [0, uniform.pdf(mu_val, loc=a_param, scale=b_param - a_param)], color=H0_COLOR, linewidth=1.0, linestyle="--", alpha=0.5)
    add_shading(ax_pdf, x, a_param, b_param, show_mode, lo_val, hi_val, prob)
    apply_dark_style(
        fig=fig,
        ax=ax_pdf,
        title=rf"Kansdichtheidsfunctie — Uniform$(a={a_param},\; b={b_param})$",
        xlabel=r"$x$",
        ylabel=r"Kansdichtheid $f(x)$"
    )

# --- CDF axes ---
if show_cdf:
    ymean = uniform.cdf(mu_val, loc=a_param, scale=b_param-a_param)
    ax_cdf.plot(x, cdf_y, color=H1_COLOR, linewidth=2.5, label=r"$F(x) = P(X \leq x)$")
    ax_cdf.plot([mu_val, mu_val, x[0]], [0, ymean, ymean], color=H1_COLOR, linewidth=1.0, linestyle="--", alpha=0.5)
    add_cdf_markers(ax_cdf, x, a_param, b_param, show_mode, lo_val, hi_val)
    apply_dark_style(
        fig=fig,
        ax=ax_cdf,
        title=rf"Cumulatieve verdelingsfunctie — Uniform$(a={a_param},\; b={b_param})$",
        xlabel=r"$x$",
        ylabel=r"Cumulatieve kans $F(x)$"
    )
    ax_cdf.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))

plt.tight_layout(pad=2.0)
st.pyplot(fig, width="stretch")
plt.close(fig)

# ----------------------------------
# EXPLANATION
# ----------------------------------
explanation_title = "📚 De uniforme verdeling"
explanation_markdown = r"""
## 📜 Wat is de uniforme verdeling?

De **uniforme verdeling** is de eenvoudigste continue kansverdeling. Ze beschrijft een kansvariabele
$X$ die met gelijke kans elke waarde aanneemt in het interval $[a, b]$. Buiten dit interval is de
kans nul.

De kansdichtheidsfunctie is:
$$
    f(x) =
    \begin{cases}
        \dfrac{1}{b - a} & \text{als } a \leq x \leq b \\[6pt]
        0 & \text{anders}
    \end{cases}
$$

## 🔢 Eigenschappen

- **Verwachtingswaarde**: $E[X] = \dfrac{a + b}{2}$
- **Variantie**: $\text{Var}(X) = \dfrac{(b-a)^2}{12}$
- **Standaardafwijking**: $\sigma = \dfrac{b - a}{\sqrt{12}}$
- Het totale oppervlak onder de curve is altijd gelijk aan **1**.

## 📐 Kansberekening

Omdat de PDF constant is, vereenvoudigt elke kansberekening tot een verhouding van lengtes:
$$
    P(c \leq X \leq d) = \frac{d - c}{b - a}, \quad a \leq c \leq d \leq b
$$

## 📈 Cumulatieve verdelingsfunctie (CDF)

$$
    F(x) =
    \begin{cases}
        0 & \text{als } x < a \\[4pt]
        \dfrac{x - a}{b - a} & \text{als } a \leq x \leq b \\[6pt]
        1 & \text{als } x > b
    \end{cases}
$$

## 🎯 Probeer het zelf!
- Pas $a$ en $b$ aan om het interval te verschuiven of te verbreden.
- Merk op dat de PDF-hoogte $1/(b-a)$ altijd zodanig is dat het totale oppervlak gelijk blijft aan 1.
- Selecteer een gebied in de zijbalk om de bijbehorende kans te berekenen en te visualiseren.
- Schakel naar **PDF + CDF** om beide grafieken tegelijk te zien.
"""

show_explanation(explanation_title, explanation_markdown)