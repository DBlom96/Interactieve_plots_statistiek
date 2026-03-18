import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import binom, poisson

from utils.explanation_utils import show_explanation
from utils.streamlit_utils import load_css, page_header, apply_dark_style, stem_plot
from utils.constants import *

st.set_page_config(
    page_title="Connectie tussen de binomiale en Poissonverdeling",
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
page_header("📊 Binomiaal & Poisson", "Discrete kansverdelingen")

with st.sidebar:
    st.header("Parameters")
    lambda_input = st.number_input(r"$\lambda$:", min_value=0.1, value=1.0, step=0.5)
    n_input      = st.number_input(r"Aantal Bernoulli-experimenten $n$:", min_value=1, value=20)

# ----------------------------------
# COMPUTATIONS
# ----------------------------------
p_input = lambda_input / n_input
k_max   = max(n_input + 1, int(lambda_input + 4 * np.sqrt(lambda_input)))
k       = np.arange(0, k_max)

y_binom   = binom.pmf(k, n_input, p_input)
y_poisson = poisson.pmf(k, lambda_input)

# ----------------------------------
# STAT CARDS
# ----------------------------------
st.markdown(f"""
<div class="stats-row-4">
  <div class="stat-card alpha">
    <span class="stat-label">Succeskans <span style="text-transform: lowercase"><i>p</i> = &lambda; / n</span></span>
    <span class="stat-value">{p_input:.4f}</span>
    <span class="stat-desc">Klein getal (zeldzame gebeurtenis)</span>
  </div>
  <div class="stat-card beta">
    <span class="stat-label">Verwachtingswaarde binomiaal</span>
    <span class="stat-value">{n_input * p_input:.2f}</span>
    <span class="stat-desc"><i>n</i> &middot; <i>p</i> = &lambda;</span>
  </div>
  <div class="stat-card power">
    <span class="stat-label">Verwachtingswaarde Poisson</span>
    <span class="stat-value">{lambda_input:.2f}</span>
    <span class="stat-desc">&lambda;</span>
  </div>
  <div class="stat-card bi">
    <span class="stat-label">Max. afwijking</span>
    <span class="stat-value">{np.max(np.abs(y_binom - y_poisson)):.4f}</span>
    <span class="stat-desc">max|P<sub>binom</sub> &minus; P<sub>Poisson</sub>|</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------
# FIGURE
# ----------------------------------
fig, (ax_binom, ax_poisson) = plt.subplots(1, 2, figsize=(14, 5))

# --- Binomial ---
stem_plot(ax_binom, k, y_binom, H0_COLOR)
apply_dark_style(
    fig=fig,
    ax=ax_binom,
    title=rf"Binomiaal$(n={n_input},\; p={p_input:.4f})$",
    xlabel=r"Aantal successen $k$",
    ylabel=r"Kansfunctie $P(X = k)$"
)

# --- Poisson ---
stem_plot(ax_poisson, k, y_poisson, H1_COLOR)
apply_dark_style(
    fig=fig,
    ax=ax_poisson,
    title=rf"Poisson$(\lambda={lambda_input})$",
    xlabel=r"Aantal gebeurtenissen $k$",
    ylabel=r"Kansfunctie $P(X = k)$"
)

# Shared x-axis range
x_max = k_max - 1
ax_binom.set_xlim(-0.5, x_max + 0.5)
ax_poisson.set_xlim(-0.5, x_max + 0.5)

plt.tight_layout(pad=2.0)
st.pyplot(fig, use_container_width=True)
plt.close(fig)

# ----------------------------------
# EXPLANATION
# ----------------------------------
explanation_title = "📚 Connectie tussen de binomiale en Poissonverdeling"
explanation_markdown = r"""
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
"""

show_explanation(explanation_title, explanation_markdown)