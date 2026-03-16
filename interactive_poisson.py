import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import binom, poisson

from utils.explanation_utils import show_explanation
from utils.streamlit_utils import load_css, page_header
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

# ------------------------------
# PARAMETERS
# ------------------------------

page_header("📊 Connectie tussen de binomiale en Poissonverdeling", "Discrete kansverdelingen")

with st.sidebar:
    st.header("Parameters")

    lambda_input = st.number_input(label="$\\lambda$", min_value=0.1, value=1.0)
    n_input = st.number_input(label="Aantal Bernoulli-experimenten $n$", min_value=1, value=20)

# ------------------------------
# SAMPLING
# ------------------------------

# Limit maximum x-value to a reasonable value
k_max = max(n_input + 1, int(lambda_input + 4 * np.sqrt(lambda_input))) 

def draw_sample_binomial(n, lambda_val):
    x = np.arange(0, k_max)  # Mogelijke uitkomsten
    y = binom.pmf(x, n, lambda_val / n)  # Binomiale kansfunctie
    return x, y

def draw_sample_poisson(lambda_val):
    x = np.arange(0, k_max)  # Mogelijke uitkomsten
    y = poisson.pmf(x, lambda_val)  # Poisson-kansfunctie
    return x, y

# ------------------------------
# PLOTTING
# ------------------------------

x_binom, y_binom = draw_sample_binomial(n_input, lambda_input)
x_poisson, y_poisson = draw_sample_poisson(lambda_input)

subtitle1 = f"Binomiaal(n = {n_input}, p = &#955; / n = {lambda_input / n_input:.2f})"
subtitle2 = f"Poisson(&#955; = " + f"{lambda_input})"
fig = make_subplots(rows=1, cols=2, subplot_titles=(subtitle1, subtitle2) )

for annotation in fig['layout']['annotations']:
    annotation['font'] = dict(size=TITLE_FONT_SIZE)
    annotation['y'] += 0.1

# Voeg naalddiagrammen toe voor de binomiale verdeling en de Poissonverdeling
fig.add_trace(go.Scatter(x=x_binom, y=y_binom, mode='markers', marker=dict(color=H0_COLOR), showlegend=False), row=1, col=1)
fig.add_trace(go.Scatter(x=x_poisson, y=y_poisson, mode='markers', marker=dict(color=H1_COLOR), showlegend=False), row=1, col=2)

for xi, yi in zip(x_binom, y_binom):
    fig.add_trace(go.Scatter(
        x=[xi, xi],
        y=[0, yi],
        mode='lines',
        line=dict(color=H0_COLOR, width=2),
        showlegend=False
    ), row=1, col=1)

for xi, yi in zip(x_poisson, y_poisson):
    fig.add_trace(go.Scatter(
        x=[xi, xi],
        y=[0, yi],
        mode='lines',
        line=dict(color=H1_COLOR, width=2),
        showlegend=False
    ), row=1, col=2)

# Update the layout of the figure
fig.update_layout(
    font=dict(family=FONT_FAMILY, color=PLOT_FONT_COLOR),
    height=600
)

for (col, text) in [(1, "Aantal successen k"), (2, "Aantal gebeurtenissen k")]:
    # Update de titel van de y-assen
    fig.update_xaxes(
        title_text=text,
        title_font=dict(size=AXIS_FONT_SIZE),
        tickfont=dict(size=TICK_FONT_SIZE),
        row=1, col=col
    )

    # Update de titel van de y-assen
    fig.update_yaxes(
        title_text="Kansfunctie f(k)",
        title_font=dict(size=AXIS_FONT_SIZE),
        tickfont=dict(size=TICK_FONT_SIZE),
        row=1, col=col
    )

st.plotly_chart(fig, use_container_width=True, config=dict(displayModeBar=False))

explanation_title = "📚 Connectie tussen de binomiale en Poissonverdeling"
explanation_md=r"""
# 📚 Connectie tussen de binomiale en Poissonverdeling

## 📌 De binomiale verdeling in het kort

De **binomiale verdeling** beschrijft de kansvariabele $X$ die het aantal successen telt in een vast aantal onafhankelijke Bernoulli-experimenten (*$n$*).
Een Bernoulli-experiment is een kansexperiment met een uitkomstenruimte bestaande uit twee mogelijke uitkomsten (succes ($1$) of mislukking ($0$)).
De succeskans bij elk afzonderlijk Bernoulli-experiment is constant en gelijk aan (*$p$*). De kansfunctie die de binomiale kansverdeling beschrijft is:

$$
    P(X = k) = \binom{n}{k} \cdot p^k \cdot (1 - p)^{n - k}
$$

waarbij:
- *$n$*: aantal onafhankelijke Bernoulli-experimenten   
- *$p$*: succeskans per Bernoulli-experiment  
- *$k$*: aantal successen  

---

## 📌 De Poissonverdeling in het kort

De **Poissonverdeling** beschrijft het aantal gebeurtenissen gedurende een vaste meeteenheid (vaak tijd of ruimte), wanneer deze gebeurtenissen:
- onafhankelijk van elkaar plaatsvinden,
- met een constante gemiddelde snelheid ($\lambda$ per meeteenheid) optreden.

De kansfunctie die de Poissonverdeling beschrijft is:

$$
    P(X = k) = \frac{\lambda^k \cdot e^{-\lambda}}{k!}
$$

waarbij:
- *$$\lambda$$*: gemiddeld aantal gebeurtenissen  
- *$k$*: aantal gebeurtenissen  

---

## 🔗 De connectie tussen binomiaal en Poisson

De **Poissonverdeling is een limietgeval van de binomiale verdeling**, onder de volgende voorwaarden:
- *$n$* is groot  
- *$p$* is klein  
- *$\lambda = n \cdot p$* is constant

In de limiet geldt dat de kansfunctie van de binomiale verdeling die van de Poissonverdeling benadert (dat wil zeggen, voor elke waarde van $k$ is de waarde van de kansfunctie bij benadering hetzelfde voor beide verdelingen): 

$$
    \text{Binomiaal}(n, \frac{\lambda}{n}) \longrightarrow \text{Poisson}(\lambda)
$$

**Voorbeeld:**  
Bij 10.000 producten en een kans van 0.0002 op een defect geldt dat
$$
    \lambda = n \cdot p = 10.000 \cdot 0.0002 = 2.
$$
Dan kan het aantal defecten bij benadering worden gemodelleerd met een Poissonverdeling met $\lambda = 2$.

---

## ✅ Waarom deze benadering nuttig is

- Wanneer het aantal experimenten $n$ groot wordt, zijn binomiaalco&euml;ffici&euml;nten $\binom{n}{k}$ heel lastig te berekenen.  
- Kansen uitrekenen met de Poissonverdeling is wiskundig eenvoudiger.  
- Veel praktische toepassingen voldoen aan de voorwaarden voor deze benadering.
"""

# Show the explanation in the Streamlit app
show_explanation(explanation_title, explanation_md)

