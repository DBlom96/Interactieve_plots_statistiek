import streamlit as st
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy.stats import norm

from utils.explanation_utils import show_explanation
from utils.streamlit_utils import load_css, page_header, apply_dark_style
from utils.constants import *

st.set_page_config(
    page_title="Normale verdeling",
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
page_header("📈 Normale verdeling", "Continue kansverdeling")

with st.sidebar:
    st.header("Parameters")
    mu_val    = st.number_input(r"Gemiddelde $\mu$:", value=0.0, step=0.5)
    sigma_val = st.number_input(r"Standaardafwijking $\sigma$:", min_value=0.1, value=1.0, step=0.1)

    st.divider()
    st.header("Kansberekening")
    show_mode = st.selectbox(
        "Arceer gebied:",
        [r"Geen", r"P(X ≤ b)", r"P(X ≥ a)", r"P(a ≤ X ≤ b)", r"Grenswaarde zoeken"]
    )

    a_val, b_val, prob = None, None, None

    if show_mode == r"P(X ≤ b)":
        b_val = st.number_input(r"$b$:", value=float(round(mu_val + sigma_val, 2)), step=0.1)
        prob  = norm.cdf(b_val, loc=mu_val, scale=sigma_val)

    elif show_mode == r"P(X ≥ a)":
        a_val = st.number_input(r"$a$:", value=float(round(mu_val - sigma_val, 2)), step=0.1)
        prob  = 1 - norm.cdf(a_val, loc=mu_val, scale=sigma_val)

    elif show_mode == r"P(a ≤ X ≤ b)":
        a_val = st.number_input(r"$a$:", value=float(round(mu_val - sigma_val, 2)), step=0.1)
        b_val = st.number_input(r"$b$:", value=float(round(mu_val + sigma_val, 2)), step=0.1)
        if a_val < b_val:
            prob = norm.cdf(b_val, loc=mu_val, scale=sigma_val) - norm.cdf(a_val, loc=mu_val, scale=sigma_val)
        else:
            st.warning(r"$a$ moet kleiner zijn dan $b$.")
    elif show_mode == r"Grenswaarde zoeken":
        prob = st.number_input("Oppervlakte (Area):", min_value=0.01, max_value=0.99, value=0.95, step=0.01)
        tail = st.selectbox("Staart:", ["links", "rechts", "midden"])

        if tail == "links":
            bounds = [-math.inf, norm.ppf(prob, loc=mu_val, scale=sigma_val)]
            st.write(f"Grenswaarde: ${bounds[1]:.4f}$")
            # Tip: Arceer P(X <= x_val) in je plot

        elif tail == "rechts":
            bounds = [norm.ppf(1 - prob, loc=mu_val, scale=sigma_val), math.inf]
            st.write(f"Grenswaarde: ${bounds[0]:.4f}$")
            # Tip: Arceer P(X >= x_val) in je plot

        elif tail == "midden":
            bounds = [norm.ppf((1 - prob) / 2, loc=mu_val, scale=sigma_val), norm.ppf(1 - (1 - prob) / 2, loc=mu_val, scale=sigma_val)]
            st.write(f"Grenswaarden: $[{bounds[0]:.4f}, {bounds[1]:.4f}]$")

    st.divider()
    view_mode = st.selectbox(label="Weergave:", options=["PDF", "CDF", "PDF + CDF"])

# ----------------------------------
# COMPUTATIONS
# ----------------------------------
x_range = max(4 * sigma_val, 1.0)
x       = np.linspace(mu_val - x_range, mu_val + x_range, 500)
pdf_y   = norm.pdf(x, loc=mu_val, scale=sigma_val)
cdf_y   = norm.cdf(x, loc=mu_val, scale=sigma_val)

# ----------------------------------
# STAT CARDS
# ----------------------------------
prob_label = f"<i>{show_mode}</i>" if show_mode != "Geen" else "Geen gebied geselecteerd"

if show_mode != r"Grenswaarde zoeken":
    st.markdown(f"""
        <div class="stats-row-3">
            <div class="stat-card alpha">
                <span class="stat-label">Gemiddelde {to_lowercase(MEAN_HTML)}</span>
                <span class="stat-value">{mu_val:.4f}</span>
                <span class="stat-desc">Centrum van de verdeling</span>
            </div>
            <div class="stat-card beta">
                <span class="stat-label">Standaardafwijking {to_lowercase(STD_HTML)}</span>
                <span class="stat-value">{sigma_val:.4f}</span>
                <span class="stat-desc">Spreiding om het gemiddelde</span>
            </div>
            <div class="stat-card bi">
                <span class="stat-label">Kans</span>
                <span class="stat-value">{f"{prob:.4f}" if prob is not None else "&mdash;"}</span>
                <span class="stat-desc">{prob_label}</span>
            </div>
            
        </div>
    """, unsafe_allow_html=True)
else:
    grenswaarden = f"{bounds[1]:.4f}" if tail == "links" else f"{bounds[0]:.4f}" if tail == "rechts" else f"[{bounds[0]:.4f}, {bounds[1]:.4f}]" if tail == "midden" else "&mdash;"
    st.markdown(f"""
        <div class="stats-row-4">
            <div class="stat-card alpha">
                <span class="stat-label">Gemiddelde {to_lowercase(MEAN_HTML)}</span>
                <span class="stat-value">{mu_val:.4f}</span>
                <span class="stat-desc">Centrum van de verdeling</span>
            </div>
            <div class="stat-card beta">
                <span class="stat-label">Standaardafwijking {to_lowercase(STD_HTML)}</span>
                <span class="stat-value">{sigma_val:.4f}</span>
                <span class="stat-desc">Spreiding om het gemiddelde</span>
            </div>
            <div class="stat-card bi">
                <span class="stat-label">Kans</span>
                <span class="stat-value">{f"{prob:.4f}" if prob is not None else "&mdash;"}</span>
                <span class="stat-desc">{prob_label}</span>
            </div>
            <div class="stat-card acceptatie">
                <span class="stat-label">{"Grenswaarden" if tail == "midden" else "Grenswaarde"}</span>
                <span class="stat-value">{grenswaarden}</span>
                <span class="stat-desc">{"Grenswaarden" if tail == "midden" else "Grenswaarde"} met tail = {tail}</span>
            </div>
        """, unsafe_allow_html=True)

def add_shading(ax, x, mu, sigma, mode, a, b, prob):
    """Fill the selected probability region on a PDF axes."""
    if mode == r"P(X ≤ b)" and b is not None:
        xf = x[x <= b]
        ax.fill_between(xf, norm.pdf(xf, mu, sigma),
                        color=FILL_COLOR, label=rf"$P(X \leq {b:.2f}) = {prob:.4f}$")
        ax.plot([b, b], [0, norm.pdf(b, mu, sigma)], color=H0_COLOR, linewidth=1.4, linestyle=":")

    elif mode == r"P(X ≥ a)" and a is not None:
        xf = x[x >= a]
        ax.fill_between(xf, norm.pdf(xf, mu, sigma),
                        color=FILL_COLOR, label=rf"$P(X \geq {a:.2f}) = {prob:.4f}$")
        ax.plot([a, a], [0, norm.pdf(a, mu, sigma)], color=H0_COLOR, linewidth=1.4, linestyle=":")

    elif mode == r"P(a ≤ X ≤ b)" and a is not None and b is not None and a < b:
        xf = x[(x >= a) & (x <= b)]
        ax.fill_between(xf, norm.pdf(xf, mu, sigma),
                        color=FILL_COLOR, label=rf"$P({a:.2f} \leq X \leq {b:.2f}) = {prob:.4f}$")
        ax.plot([a, a], [0, norm.pdf(a, mu, sigma)], color=H0_COLOR, linewidth=1.4, linestyle=":")
        ax.plot([b, b], [0, norm.pdf(b, mu, sigma)], color=H0_COLOR, linewidth=1.4, linestyle=":")
    elif mode == r"Grenswaarde zoeken" and prob is not None:
        if tail == "links":
            x_val = norm.ppf(prob, loc=mu, scale=sigma)
            mask = x[x <= x_val]
            ax.fill_between(mask, norm.pdf(mask, mu, sigma), color=FILL_COLOR)
            ax.plot([x_val, x_val], [0, norm.pdf(x_val, mu, sigma)], color=H0_COLOR, linewidth=1.4, linestyle=":")
        elif tail == "rechts":
            x_val = norm.ppf(1 - prob, loc=mu, scale=sigma)
            mask = x[x >= x_val]
            ax.fill_between(mask, norm.pdf(mask, mu, sigma), color=FILL_COLOR)
            ax.plot([x_val, x_val], [0, norm.pdf(x_val, mu, sigma)], color=H0_COLOR, linewidth=1.4, linestyle=":")
        elif tail == "midden":
            lower = norm.ppf((1 - prob) / 2, loc=mu, scale=sigma)
            upper = norm.ppf(1 - (1 - prob) / 2, loc=mu, scale=sigma)
            mask = x[(x >= lower) & (x <= upper)]
            ax.fill_between(mask, norm.pdf(mask, mu, sigma), color=FILL_COLOR)

            ax.plot([lower, lower], [0, norm.pdf(lower, mu, sigma)], color=H0_COLOR, linewidth=1.4, linestyle=":")
            ax.plot([upper, upper], [0, norm.pdf(upper, mu, sigma)], color=H0_COLOR, linewidth=1.4, linestyle=":")


def add_cdf_markers(ax, mu, sigma, mode, a, b):
    """Mark the queried CDF value(s) with a dot and dashed drop-lines."""
    points = []
    if mode == r"P(X ≤ b)" and b is not None:
        points = [(b, norm.cdf(b, mu, sigma))]
    elif mode == r"P(X ≥ a)" and a is not None:
        points = [(a, norm.cdf(a, mu, sigma))]
    elif mode == r"P(a ≤ X ≤ b)" and a is not None and b is not None:
        points = [(a, norm.cdf(a, mu, sigma)), (b, norm.cdf(b, mu, sigma))]

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

if nrows == 1:
    axes = [axes]

ax_pdf = axes[0] if show_pdf else None
ax_cdf = axes[1] if view_mode == "PDF + CDF" else (axes[0] if show_cdf else None)

# --- PDF axes ---
if show_pdf:
    ax_pdf.plot(x, pdf_y, color=H0_COLOR, linewidth=2.5,
                label=rf"$f(x)$ — $\mathcal{{N}}(\mu={mu_val},\, \sigma={sigma_val})$")
    ax_pdf.plot([mu_val, mu_val], [0, norm.pdf(mu_val, mu_val, sigma_val)], color=H0_COLOR, linewidth=1.0, linestyle="--", alpha=0.5)
    add_shading(ax_pdf, x, mu_val, sigma_val, show_mode, a_val, b_val, prob)
    apply_dark_style(
        fig=fig,
        ax=ax_pdf,
        title=rf"Kansdichtheidsfunctie (PDF) — $\mathcal{{N}}(\mu = {mu_val},\; \sigma = {sigma_val})$",
        xlabel=r"$x$",
        ylabel=r"Kansdichtheid $f(x)$"
    )

# --- CDF axes ---
if show_cdf:
    ax_cdf.plot(x, cdf_y, color=H1_COLOR, linewidth=2.5, label=r"$F(x) = P(X \leq x)$")
    ax_cdf.plot([mu_val, mu_val, x[0]], [0, norm.cdf(mu_val, mu_val, sigma_val), norm.cdf(mu_val, mu_val, sigma_val)], color=H1_COLOR, linewidth=1.0, linestyle="--", alpha=0.5)
    add_cdf_markers(ax_cdf, mu_val, sigma_val, show_mode, a_val, b_val)
    apply_dark_style(
        fig=fig,
        ax=ax_cdf,
        title=rf"Cumulatieve verdelingsfunctie (CDF) — $\mathcal{{N}}(\mu = {mu_val},\; \sigma = {sigma_val})$",
        xlabel=r"$x$",
        ylabel=r"Cumulatieve kans $F(x)$"
    )
    ax_cdf.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))


axes[-1].set_xlabel(r"$x$", fontsize=13, color=PLOT_FONT_COLOR)

plt.tight_layout(pad=2.0)
st.pyplot(fig, width="stretch")
plt.close(fig)

# ----------------------------------
# EXPLANATION
# ----------------------------------
explanation_title = "📚 De normale verdeling"
explanation_markdown = r"""
## 📜 Wat is de normale verdeling?

De **normale verdeling** (ook wel Gaussiaanse verdeling of belkromme) is de meest gebruikte continue
kansverdeling in de statistiek. Ze is volledig bepaald door twee parameters: 
- het **gemiddelde** $\mu$
- de **standaardafwijking** $\sigma$.

De kansdichtheidsfunctie is:
$$
    f(x) = \frac{1}{\sigma\sqrt{2\pi}} \, e^{-\frac{1}{2}\left(\frac{x-\mu}{\sigma}\right)^2}
$$

## 🔢 Eigenschappen

- **Symmetrie**: de verdeling is symmetrisch rond $\mu$.
- **Verwachtingswaarde**: $E(X) = \mu$
- **Variantie**: $\text{Var}(X) = \sigma^2$
- Het totale oppervlak onder de curve is altijd gelijk aan **1**.

## 📐 De 68-95-99.7 regel

Een handige vuistregel voor de normale verdeling:
- $68\%$ van de normale verdeling ligt binnen één standaardafwijking van het gemiddelde $\mu$: 
$$
    P(\mu - \sigma \leq X \leq \mu + \sigma) \approx 0.68.
$$
- $95\%$ van de normale verdeling ligt binnen twee standaardafwijkingen van het gemiddelde $\mu$: 
$$
    P(\mu - 2\sigma \leq X \leq \mu + 2\sigma) \approx 0.95.
$$
- $99.7\%$ van de normale verdeling ligt binnen drie standaardafwijkingen van het gemiddelde $\mu$: 
$$
    P(\mu - 3\sigma \leq X \leq \mu + 3\sigma) \approx 0.997.
$$

## 📈 Cumulatieve verdelingsfunctie (CDF)

De CDF geeft de kans dat $X$ hoogstens een bepaalde waarde $x$ aanneemt:
$$
    F(x) = P(X \leq x) = \int_{-\infty}^{x} f(t) \, dt
$$

Dit is direct bruikbaar voor kansberekeningen: $P(a \leq X \leq b) = F(b) - F(a)$.

## 🎯 Probeer het zelf!
- Pas $\mu$ aan om de verdeling te verschuiven.
- Pas $\sigma$ aan: een kleine $\sigma$ geeft een smalle, hoge piek; een grote $\sigma$ een brede, vlakke curve.
- Selecteer een gebied in de zijbalk om de bijbehorende kans te berekenen en te visualiseren.
- Schakel naar **PDF + CDF** om beide grafieken tegelijk te zien.
"""

show_explanation(explanation_title, explanation_markdown)