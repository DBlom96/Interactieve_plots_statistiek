import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import binom
from utils.explanation_utils import show_explanation

st.set_page_config(
    page_title="Visualisatie van de binomiale verdeling",
    initial_sidebar_state="expanded",
    layout="wide"
)

# ----------------------------------
# PARAMETERS
# ----------------------------------

st.title("📊 Interactieve plot: de binomiale verdeling")
with st.sidebar:
    st.header("Parameters")
    
    n_slider = st.number_input(label="Aantal Bernoulli-experimenten $n$", min_value=1, value=20)
    p_slider = st.slider(label="Succeskans $p$", min_value=0.0, max_value=1.0, value=0.5)

# ----------------------------------
# SAMPLING
# ----------------------------------

def draw_binomial_distribution(n, p):
    x = np.arange(0, n + 1)  # Mogelijke uitkomsten
    y = binom.pmf(x, n, p)  # Binomiale kansfunctie
    return x, y

# ----------------------------------
# PLOTTING
# ----------------------------------

x, y = draw_binomial_distribution(n_slider, p_slider)

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=x,
    y=y,
    mode='markers',
    marker=dict(color="cyan"),
    showlegend=False
))

for xi, yi in zip(x, y):
    fig.add_trace(go.Scatter(
        x=[xi, xi],
        y=[0, yi],
        mode='lines',
        line=dict(color='cyan',width=2),
        showlegend=False
    ))

fig.update_layout(
    title=dict(
        text=(f"Naalddiagram van de binomiale verdeling met n = {n_slider} en p = {p_slider}"),
        font=dict(size=40),
    ),
    xaxis=dict(
        title=dict(text="Uitkomst k", font=dict(size=30)),
        tickfont=dict(size=30)
    ),
    yaxis = dict(
        title=dict(text = "Kansfunctie P(X=k)", font=dict(size=30)),
        tickfont=dict(size=30)
    ),
    height=800,
)

st.plotly_chart(fig, use_container_width=True, config=dict(displayModeBar=False))

explanation_title = "📚 De binomiale verdeling"
explanation_markdown = """
    De **binomiale verdeling** is een discrete kansverdeling die het aantal successen telt in een reeks onafhankelijke Bernoulli-experimenten.
    Dit betekent dat elk experiment slechts twee mogelijke uitkomsten heeft: *succes* (1) of *mislukking* (0).
    Onafhankelijkheid betekent dat de uitkomst van het ene experiment geen invloed heeft op de kansverdeling van andere experimenten.

    ## 🔢 Kenmerken van de binomiale verdeling

    Een experiment volgt een binomiale verdeling als:
    - er **n** onafhankelijke experimenten worden uitgevoerd.
    - elk experiment heeft **twee uitkomsten**: succes (met kans *p*) of mislukking (met kans *1 - p*).
    - de kans op succes is **constant** voor alle experimenten.
    - de uitkomsten zijn **onafhankelijk** van elkaar.

    ## 📜 Formule van de binomiale kansfunctie
    De kans op **exact $k$ successen** in **$n$ pogingen** wordt berekend met:

    $$ 
        P(X=k) = \\binom{n}{k} \\cdot p^k \\cdot (1 - p)^{n - k}, 
    $$

    waarbij:
    - $n$ het **aantal experimenten** is.
    - $p$ de **kans op succes** per experiment is.
    - $k$ het **aantal successen** is.
    - $$ \\binom{n}{k} $$ de **binomiaalcoefficient** is, oftewel het aantal manieren om uit $n$ pogingen er $k \le n$ te kiezen die succesvol zijn:  
    $$ 
        \\binom{n}{k} = \\frac{n!}{k! \\cdot (n-k)!} 
    $$

    ## 📈 Verwachtingswaarde en standaardafwijking
    - **Verwachtingswaarde**:  
    $$ 
        E[X] = n \\cdot p 
    $$
    - **Standaardafwijking**:  
    $$
        \\sigma(X) = \\sqrt{n \\cdot p \\cdot (1 - p)} 
    $$

    ## 🎯 Voorbeeld: worpen met een eerlijke munt
    Stel dat we een eerlijke munt **10 keer** opgooien en de kans op "kop" is **50\%**. De binomiale verdeling beschrijft dan de kans op **exact 6 keer kop**:

    $$
        P(X=6) = \\binom{10}{6} \\cdot (0.5)^6 \\cdot (0.5)^4 \\approx 0.2051
    $$
"""

show_explanation(explanation_title, explanation_markdown)