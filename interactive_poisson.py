import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy.stats import binom, poisson

from utils.explanation_utils import show_explanation
from utils.streamlit_utils import load_css, page_header, apply_dark_style, stem_plot, get_highlighted, add_cdf_markers
from utils.constants import *

st.set_page_config(
    page_title="De Poissonverdeling",
    initial_sidebar_state="expanded",
    layout="wide"
)

load_css()

# ----------------------------------
# MODE SELECTION
# ----------------------------------
page_header("📊 Poissonverdeling", "Discrete kansverdeling")

with st.sidebar:
    st.header("Parameters")

    mode = st.selectbox(
        label="Modus", 
        options=["Poissonverdeling", "Vergelijking Binomiaal & Poisson"]
    )

    st.divider()

    if mode == "Poissonverdeling":
        lambda_val = st.number_input(r"$\lambda$:", min_value=0.1, value=3.0, step=0.5)

        st.divider()
        st.header("Kansberekening")
        show_mode = st.selectbox(
            "Highlight kansen:",
            ["Geen", r"P(X ≤ b)", r"P(X ≥ a)", r"P(a ≤ X ≤ b)"]
        )

        k_max_sidebar = int(lambda_val + 4 * np.sqrt(lambda_val)) + 1

        lo_val, hi_val, prob = None, None, None

        if show_mode == r"P(X ≤ b)":
            hi_val = st.number_input(r"$b$:", min_value=0, max_value=k_max_sidebar,
                                     value=int(lambda_val))
            prob   = poisson.cdf(hi_val, lambda_val)

        elif show_mode == r"P(X ≥ a)":
            lo_val = st.number_input(r"$a$:", min_value=0, max_value=k_max_sidebar,
                                     value=int(lambda_val))
            prob   = 1 - poisson.cdf(lo_val - 1, lambda_val)

        elif show_mode == r"P(a ≤ X ≤ b)":
            lo_val = st.number_input(r"$a$:", min_value=0, max_value=k_max_sidebar,
                                     value=max(0, int(lambda_val) - 2))
            hi_val = st.number_input(r"$b$:", min_value=0, max_value=k_max_sidebar,
                                     value=int(lambda_val) + 2)
            if lo_val <= hi_val:
                prob = poisson.cdf(hi_val, lambda_val) - poisson.cdf(lo_val - 1, lambda_val)
            else:
                st.warning(r"$a$ moet kleiner zijn dan of gelijk zijn aan $b$.")

        st.divider()
        view_mode = st.selectbox(
            label="Weergave:",
            options=["Kansfunctie", "CDF", "Kansfunctie + CDF"]
        )
    else:
        lambda_input = st.number_input(r"$\lambda$:", min_value=0.1, value=1.0, step=0.5)
        n_input      = st.number_input(r"Aantal Bernoulli-experimenten $n$:", min_value=1, value=20)


# ----------------------------------
# # COMPUTATIONS
# ----------------------------------
if mode == "Poissonverdeling":
    k     = np.arange(0, k_max_sidebar + 1)
    pmf_y = poisson.pmf(k, lambda_val)
    cdf_y = pmf_y.cumsum()
    sigma_val = np.sqrt(lambda_val)
else:
    p_input = lambda_input / n_input
    k_max   = max(n_input + 1, int(lambda_input + 4 * np.sqrt(lambda_input)))
    k       = np.arange(0, k_max)
    y_binom   = binom.pmf(k, n_input, p_input)
    y_poisson = poisson.pmf(k, lambda_input)

# ----------------------------------
# STAT CARDS
# ----------------------------------
if mode == "Poissonverdeling":
    prob_label = f"<i>{show_mode}</i>" if show_mode != "Geen" else "Geen gebied geselecteerd"
    st.markdown(f"""
        <div class="stats-row-3">
            <div class="stat-card alpha">
                <span class="stat-label">Verwachtingswaarde</span>
                <span class="stat-value">{lambda_val:.4f}</span>
                <span class="stat-desc">{to_lowercase(LAMBDA_HTML)}</span>
            </div>
            <div class="stat-card beta">
                <span class="stat-label">Variantie</span>
                <span class="stat-value">{lambda_val:.4f}</span>
                <span class="stat-desc">{to_lowercase(LAMBDA_HTML)}</span>
            </div>
            <div class="stat-card power">
                <span class="stat-label">Kans</span>
                <span class="stat-value">{f"{prob:.4f}" if prob is not None else "&mdash;"}</span>
                <span class="stat-desc">{prob_label}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(f"""
        <div class="stats-row-4">
            <div class="stat-card alpha">
                <span class="stat-label">Succeskans {to_lowercase(P_HTML)} = {to_lowercase(LAMBDA_HTML)} / {to_lowercase(N_HTML)}</span></span>
                <span class="stat-value">{p_input:.4f}</span>
                <span class="stat-desc">Klein getal (zeldzame gebeurtenis)</span>
            </div>
            <div class="stat-card beta">
                <span class="stat-label">Verwachtingswaarde binom</span>
                <span class="stat-value">{n_input * p_input:.2f}</span>
                <span class="stat-desc">{to_lowercase(N_HTML)} &middot; {to_lowercase(P_HTML)} = {to_lowercase(LAMBDA_HTML)}</span>
            </div>
            <div class="stat-card power">
                <span class="stat-label">Verwachtingswaarde Poisson</span>
                <span class="stat-value">{lambda_input:.2f}</span>
                <span class="stat-desc">{to_lowercase(LAMBDA_HTML)}</span>
            </div>
            <div class="stat-card bi">
                <span class="stat-label">Max. afwijking</span>
                <span class="stat-value">{np.max(np.abs(y_binom - y_poisson)):.4f}</span>
                <span class="stat-desc">max|<i>P</i><sub>binom</sub> &minus; <i>P</i><sub>Poisson</sub>|</span>
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )

# ----------------------------------
# PLOTTING FUNCTIONS
# ----------------------------------
if mode == "Poissonverdeling":
    def get_highlighted(mode, lo, hi, k):
        if mode == r"P(X ≤ b)" and hi is not None:
            return set(k[k <= hi])
        elif mode == r"P(X ≥ a)" and lo is not None:
            return set(k[k >= lo])
        elif mode == r"P(a ≤ X ≤ b)" and lo is not None and hi is not None and lo <= hi:
            return set(k[(k >= lo) & (k <= hi)])
        return None

    highlighted = get_highlighted(show_mode, lo_val, hi_val, k)

    prob_label_latex = {
        r"P(X ≤ b)":     rf"$P(X \leq {hi_val}) = {prob:.4f}$" if prob is not None else "",
        r"P(X ≥ a)":     rf"$P(X \geq {lo_val}) = {prob:.4f}$" if prob is not None else "",
        r"P(a ≤ X ≤ b)": rf"$P({lo_val} \leq X \leq {hi_val}) = {prob:.4f}$" if prob is not None else "",
    }.get(show_mode, "")

    show_pmf = view_mode in ("Kansfunctie", "Kansfunctie + CDF")
    show_cdf = view_mode in ("CDF", "Kansfunctie + CDF")

    nrows = 2 if view_mode == "Kansfunctie + CDF" else 1
    fig, axes = plt.subplots(nrows, 1, figsize=(10, 5 * nrows))
    if nrows == 1:
        axes = [axes]

    ax_pmf = axes[0] if show_pmf else None
    ax_cdf = axes[1] if view_mode == "Kansfunctie + CDF" else (axes[0] if show_cdf else None)

    if show_pmf:
        stem_plot(ax_pmf, k, pmf_y, color=H0_COLOR,
                  highlighted=highlighted, highlight_color=INTERVAL_COLOR)
        if prob_label_latex:
            ax_pmf.plot([], [], color=FILL_COLOR, linewidth=3, label=prob_label_latex)
        apply_dark_style(
            fig=fig, ax=ax_pmf,
            title=rf"Kansfunctie — Poisson$(\lambda={lambda_val})$",
            xlabel=r"Aantal gebeurtenissen $k$",
            ylabel=r"Kansfunctie $P(X = k)$",
        )
        ax_pmf.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        ax_pmf.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))

    if show_cdf:
        for j in k[:-1]:
            ax_cdf.plot([j, j+1], [cdf_y[j], cdf_y[j]], color=H1_COLOR, linestyle='-', linewidth=2.5)
        ax_cdf.step(k, cdf_y, where="post", color=H1_COLOR, linestyle=':', linewidth=2.5)
        ax_cdf.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        ax_cdf.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
        apply_dark_style(
            fig=fig, ax=ax_cdf,
            title=rf"Cumulatieve kansfunctie — Poisson$(\lambda={lambda_val})$",
            xlabel=r"Aantal gebeurtenissen $k$",
            ylabel=r"Cumulatieve kans $P(X \leq k)$",
        )
else:
    fig, (ax_binom, ax_poisson) = plt.subplots(1, 2, figsize=(14, 5), sharey=True)

    stem_plot(ax_binom, k, y_binom, H0_COLOR)
    apply_dark_style(
        fig=fig, ax=ax_binom,
        title=rf"Binomiaal$(n={n_input},\; p=\frac{{\lambda}}{{n}}={p_input:.4f})$",
        xlabel=r"Aantal successen $k$",
        ylabel=r"Kansfunctie $P(X = k)$",
    )

    stem_plot(ax_poisson, k, y_poisson, H1_COLOR)
    apply_dark_style(
        fig=fig, ax=ax_poisson,
        title=rf"Poisson$(\lambda={lambda_input})$",
        xlabel=r"Aantal gebeurtenissen $k$",
        ylabel=r"Kansfunctie $P(X = k)$",
    )

    x_max = k_max - 1
    ax_binom.set_xlim(-0.5, x_max + 0.5)
    ax_poisson.set_xlim(-0.5, x_max + 0.5)
    ax_binom.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax_poisson.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))

plt.tight_layout(pad=2.0)
st.pyplot(fig, width="stretch")
plt.close(fig)


# ----------------------------------
# EXPLANATION
# ----------------------------------
if mode == "Poissonverdeling":
    show_explanation("📚 De Poissonverdeling", r"""
    ## 📜 Wat is de Poissonverdeling?

    De **Poissonverdeling** is een discrete kansverdeling die het aantal gebeurtenissen telt dat
    plaatsvindt in een vaste tijds- of ruimte-eenheid, waarbij gebeurtenissen onafhankelijk van
    elkaar optreden met een constante gemiddelde snelheid $\lambda$.

    ## 🔢 Kenmerken

    Een toevalsvariabele $X$ volgt een Poissonverdeling als:
    - gebeurtenissen onafhankelijk van elkaar plaatsvinden,
    - de gemiddelde snelheid $\lambda$ constant is,
    - twee gebeurtenissen niet precies op hetzelfde moment plaatsvinden.

    ## 📐 Kansfunctie

    $$
        P(X = k) = \frac{\lambda^k \cdot e^{-\lambda}}{k!}, \quad k = 0, 1, 2, \ldots
    $$

    ## 📈 Verwachtingswaarde en variantie

    $$
        E[X] = \lambda \qquad \text{Var}(X) = \lambda
    $$

    De verwachtingswaarde en variantie zijn beide gelijk aan $\lambda$ — een unieke eigenschap.

    ## 🎯 Voorbeeld

    Een callcenter ontvangt gemiddeld $\lambda = 3$ telefoontjes per minuut.
    De kans op exact 5 telefoontjes in één minuut:
    $$
        P(X = 5) = \frac{3^5 \cdot e^{-3}}{5!} \approx 0.1008.
    $$
    """)
else:
    show_explanation("📚 Connectie tussen de binomiale en Poissonverdeling", r"""
    ## 📌 De binomiale verdeling in het kort

    De **binomiale verdeling** beschrijft de kansvariabele $X$ die het aantal successen telt in een vast
    aantal onafhankelijke Bernoulli-experimenten ($n$). De succeskans bij elk afzonderlijk experiment is
    constant en gelijk aan $p$. De kansfunctie is:

    $$
        P(X = k) = \binom{n}{k} \cdot p^k \cdot (1 - p)^{n - k}
    $$

    ---

    ## 📌 De Poissonverdeling in het kort

    De **Poissonverdeling** beschrijft het aantal gebeurtenissen gedurende een vaste meeteenheid wanneer
    deze gebeurtenissen onafhankelijk van elkaar plaatsvinden met een constante gemiddelde snelheid
    $\lambda$. De kansfunctie is:

    $$
        P(X = k) = \frac{\lambda^k \cdot e^{-\lambda}}{k!}
    $$

    ---

    ## 🔗 De connectie

    De **Poissonverdeling is een limietgeval van de binomiale verdeling**, onder de volgende voorwaarden:
    - $n$ is groot
    - $p$ is klein
    - $\lambda = n \cdot p$ is constant

    In de limiet geldt:
    $$
        \text{Binomiaal}\!\left(n,\, \frac{\lambda}{n}\right) \longrightarrow \text{Poisson}(\lambda)
    $$

    **Voorbeeld:** bij $n = 10.000$ producten en kans $p = 0.0002$ op een defect geldt
    $\lambda = n \cdot p = 2$. Het aantal defecten kan dan worden benaderd met Poisson$(\lambda = 2)$.

    Controleer dit voor jezelf door te kijken wat er gebeurt voor een specifieke $\lambda$ als je het aantal Bernoulli-experimenten $n$ verhoogt.

    ---

    ## ✅ Waarom deze benadering nuttig is

    - Voor grote $n$ zijn binomiaalcoëfficiënten $\binom{n}{k}$ lastig te berekenen.
    - Kansen uitrekenen met de Poissonverdeling is wiskundig eenvoudiger.
    - Veel praktische toepassingen voldoen aan de voorwaarden voor deze benadering.
    """)