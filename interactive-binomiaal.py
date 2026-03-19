import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy.stats import binom

from utils.explanation_utils import show_explanation
from utils.streamlit_utils import load_css, page_header, apply_dark_style, stem_plot, get_highlighted, add_cdf_markers
from utils.constants import *

st.set_page_config(
    page_title="Binomiale verdeling",
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
page_header("📊 Binomiale verdeling", "Discrete kansverdeling")

with st.sidebar:
    st.header("Parameters")
    n_val = st.number_input(r"Aantal Bernoulli-experimenten $n$:", min_value=1, value=20)
    p_val = st.slider(r"Succeskans $p$:", min_value=0.0, max_value=1.0, value=0.5, step=0.01)

    st.divider()
    st.header("Kansberekening")
    show_mode = st.selectbox(
        "Highlight kansen:",
        [r"Geen", r"P(X ≤ b)", r"P(X ≥ a)", r"P(a ≤ X ≤ b)"]
    )

    lo_val, hi_val, prob = None, None, None

    if show_mode == r"P(X ≤ b)":
        hi_val = st.number_input(r"$b$:", min_value=0, max_value=n_val, value=min(n_val, int(n_val * p_val)))
        prob   = binom.cdf(hi_val, n_val, p_val)

    elif show_mode == r"P(X ≥ a)":
        lo_val = st.number_input(r"$a$:", min_value=0, max_value=n_val, value=max(0, int(n_val * p_val)))
        prob   = 1 - binom.cdf(lo_val - 1, n_val, p_val)

    elif show_mode == r"P(a ≤ X ≤ b)":
        lo_val = st.number_input(r"$a$:", min_value=0, max_value=n_val, value=max(0, int(n_val * p_val) - 2))
        hi_val = st.number_input(r"$b$:", min_value=0, max_value=n_val, value=min(n_val, int(n_val * p_val) + 2))
        if lo_val <= hi_val:
            prob = binom.cdf(hi_val, n_val, p_val) - binom.cdf(lo_val - 1, n_val, p_val)
        else:
            st.warning(r"$a$ moet kleiner zijn dan of gelijk zijn aan $b$.")

    st.divider()
    view_mode = st.radio("Weergave:", ["Kansfunctie", "CDF", "Kansfunctie + CDF"])

# ----------------------------------
# COMPUTATIONS
# ----------------------------------
k     = np.arange(0, n_val + 1)
pmf_y = binom.pmf(k, n_val, p_val)
cdf_y = binom.cdf(k, n_val, p_val)

mu_val    = n_val * p_val
sigma_val = np.sqrt(n_val * p_val * (1 - p_val))

# ----------------------------------
# STAT CARDS
# ----------------------------------
prob_label = f"<i>{show_mode}</i>" if show_mode != "Geen" else "Geen gebied geselecteerd"
st.markdown(f"""
<div class="stats-row-3">
  <div class="stat-card alpha">
    <span class="stat-label">Verwachtingswaarde</span>
    <span class="stat-value">{mu_val:.2f}</span>
    <span class="stat-desc">{to_lowercase(N_HTML)} &middot; {to_lowercase(P_HTML)}</span>
  </div>
  <div class="stat-card beta">
    <span class="stat-label">Variantie</span>
    <span class="stat-value">{sigma_val**2:.4f}</span>
    <span class="stat-desc">{to_lowercase(N_HTML)} &middot; {to_lowercase(P_HTML)} &middot; (1 &minus; {to_lowercase(P_HTML)})</span>
  </div>
  <div class="stat-card power">
    <span class="stat-label">Kans</span>
    <span class="stat-value">{f"{prob:.4f}" if prob is not None else "&mdash;"}</span>
    <span class="stat-desc">{prob_label}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------
# HELPERS
# ----------------------------------


# ----------------------------------
# FIGURE
# ----------------------------------
show_pmf = view_mode in ("Kansfunctie", "Kansfunctie + CDF")
show_cdf = view_mode in ("CDF", "Kansfunctie + CDF")

highlighted = get_highlighted(show_mode, lo_val, hi_val, k)
prob_label_latex = {
    r"P(X ≤ b)":     rf"$P(X \leq {hi_val}) = {prob:.4f}$" if prob is not None else "",
    r"P(X ≥ a)":     rf"$P(X \geq {lo_val}) = {prob:.4f}$" if prob is not None else "",
    r"P(a ≤ X ≤ b)": rf"$P({lo_val} \leq X \leq {hi_val}) = {prob:.4f}$" if prob is not None else "",
}.get(show_mode, "")

nrows = 2 if view_mode == "Kansfunctie + CDF" else 1
fig, axes = plt.subplots(nrows, 1, figsize=(10, 5 * nrows))

if nrows == 1:
    axes = [axes]

ax_pmf = axes[0] if show_pmf else None
ax_cdf = axes[1] if view_mode == "Kansfunctie + CDF" else (axes[0] if show_cdf else None)

# --- PMF axes ---
if show_pmf:
    stem_plot(ax_pmf, k, pmf_y, color=H0_COLOR,
              highlighted=highlighted, highlight_color=INTERVAL_COLOR)
    if prob_label_latex:
        ax_pmf.plot([], [], color=FILL_COLOR, linewidth=3, label=prob_label_latex)
    apply_dark_style(
        fig=fig,
        ax=ax_pmf,
        title=rf"Kansfunctie — Binomiaal$(n={n_val},\; p={p_val})$",
        xlabel=r"Aantal successen $k$",
        ylabel=r"Kansfunctie $P(X = k)$"
    )
    ax_pmf.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax_pmf.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))

# --- CDF axes ---
if show_cdf:
    # Draw as step function
    ax_cdf.step(k, cdf_y, where="post", color=H1_COLOR, linestyle=':', linewidth=2.5,
                label=r"$F(k) = P(X \leq k)$")
    for j in k[:-1]:
        ax_cdf.plot([j, j+1], [cdf_y[j], cdf_y[j]], color=H1_COLOR, linestyle='-', linewidth=2.5,
                label=r"$F(k) = P(X \leq k)$")

    add_cdf_markers(ax_cdf, k, cdf_y, show_mode, lo_val, hi_val)

    ax_cdf.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax_cdf.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
    apply_dark_style(
        fig=fig,
        ax=ax_cdf,
        title=rf"Cumulatieve kansfunctie — Binomiaal$(n={n_val},\; p={p_val})$",
        xlabel=r"Aantal successen ($k$)",
        ylabel=r"Cumulatieve kans $P(X \leq k)$"
    )

plt.tight_layout(pad=2.0)
st.pyplot(fig, use_container_width=True)
plt.close(fig)

# ----------------------------------
# EXPLANATION
# ----------------------------------
explanation_title = "📚 De binomiale verdeling"
explanation_markdown = r"""
## 📜 Wat is de binomiale verdeling?

De **binomiale verdeling** is een discrete kansverdeling die het aantal successen telt in een reeks
onafhankelijke Bernoulli-experimenten. Elk experiment heeft precies twee mogelijke uitkomsten:
*succes* (1) of *mislukking* (0), met een constante succeskans $p$.

## 🔢 Kenmerken

Een experiment volgt een binomiale verdeling als:
- er $n$ onafhankelijke experimenten worden uitgevoerd,
- elk experiment heeft succeskans $p$ (constant),
- de uitkomsten zijn onafhankelijk van elkaar.

## 📐 Kansfunctie

$$
    P(X = k) = \binom{n}{k} \cdot p^k \cdot (1 - p)^{n - k}
$$

waarbij $\binom{n}{k} = \dfrac{n!}{k!\,(n-k)!}$ de binomiaalcoëfficiënt is.

## 📈 Verwachtingswaarde en standaardafwijking

$$
    E[X] = n \cdot p \qquad \sigma(X) = \sqrt{n \cdot p \cdot (1 - p)}
$$

## 🎯 Voorbeeld

Een eerlijke munt 10 keer opgooien ($n = 10$, $p = 0.5$). De kans op exact 6 keer kop:
$$
    P(X = 6) = \binom{10}{6} \cdot (0.5)^6 \cdot (0.5)^4 \approx 0.2051
$$
"""

show_explanation(explanation_title, explanation_markdown)