import streamlit as st
import numpy as np
import plotly.graph_objects as go

from scipy.stats import norm, uniform, expon, binom, poisson
from utils.explanation_utils import show_explanation
from utils.streamlit_utils import load_css, css_to_rgba, page_header

st.set_page_config(
    page_title="De centrale limietstelling",
    initial_sidebar_state="expanded",
    layout="wide"
)
# ----------------------------------
# CSS
# ----------------------------------
load_css()



# ----------------------------------
# HELPERS
# ----------------------------------

# --------------------------------------------------
# PARAMETERS
# --------------------------------------------------
page_header("📊 Centrale limietstelling", "Statistiek · Visualisatie")

with st.sidebar:
    st.header("Parameters")

    dist_selector = st.selectbox("Kansverdeling:", ["normale", "uniforme", 'exponenti&#235;le', "binomiale", "Poisson"])
    sample_size   = st.number_input("Steekproefgrootte $n$:", min_value=1, value=30)
    n_samples     = st.number_input("Aantal steekproeven:", min_value=1, value=1_000)
    n_bins        = int(np.sqrt(n_samples))

    if dist_selector == "normale":
        mu_val      = st.number_input("Gemiddelde $\\mu$:", value=0.0)
        sigma_val   = st.number_input("Standaardafwijking $\\sigma$:", value=1.0)
        dist_params = {"mu": mu_val, "sigma": sigma_val}
        true_mu     = mu_val
        true_sigma  = sigma_val / np.sqrt(sample_size)
    elif dist_selector == "uniforme":
        a_val       = st.number_input("Ondergrens $a$:", value=-5.0)
        b_val       = st.number_input("Bovengrens $b$:", min_value=a_val + 0.1, value=5.0)
        dist_params = {"a": a_val, "b": b_val}
        true_mu     = (a_val + b_val) / 2
        true_sigma  = (b_val - a_val) / np.sqrt(12 * sample_size)
    elif dist_selector == 'exponenti&#235;le':
        lam_val     = st.number_input("$\\lambda$:", min_value=0.1,value=1.0)
        dist_params = {"lambda_": lam_val}
        true_mu     = 1 / lam_val
        true_sigma  = (1 / lam_val) / np.sqrt(sample_size)
    elif dist_selector == "Poisson":
        lam_val     = st.number_input("$\\lambda$:", min_value=0.1,value=1.0)
        dist_params = {"lambda_": lam_val}
        true_mu     = lam_val
        true_sigma  = np.sqrt(lam_val / sample_size)
    elif dist_selector == "binomiale":
        n_binom     = st.number_input("Aantal Bernoulli-experimenten $n$:", min_value=1, value=20)
        p_binom     = st.slider("Succeskans $p$:", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
        dist_params = {"n": n_binom, "p": p_binom}
        true_mu     = n_binom * p_binom
        true_sigma  = np.sqrt(n_binom * p_binom * (1 - p_binom) / sample_size)

# --------------------------------------------------
# SAMPLING
# --------------------------------------------------

def draw_sample_means(dist, sample_size, n_samples, **params):
    if dist == "normale":
        data = norm.rvs(loc=params["mu"], scale=params["sigma"], size=(sample_size, n_samples))
    elif dist == "uniforme":
        data = uniform.rvs(loc=params["a"], scale=params["b"] - params["a"], size=(sample_size, n_samples))
    elif dist == 'exponenti&#235;le':
        data = expon.rvs(scale=1 / params["lambda_"], size=(sample_size, n_samples))
    elif dist == "binomiale":
        data = binom.rvs(n=params["n"], p=params["p"], size=(sample_size, n_samples))
    elif dist == "Poisson":
        data = poisson.rvs(mu=params["lambda_"], size=(sample_size, n_samples))
    return data.mean(axis=0)



# --------------------------------------------------
# COMPUTATIONS
# --------------------------------------------------

all_means = draw_sample_means(dist_selector, sample_size, n_samples, **dist_params)

bin_edges   = np.linspace(all_means.min(), all_means.max(), n_bins + 1)
bin_width   = bin_edges[1] - bin_edges[0]
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
counts, _   = np.histogram(all_means, bins=bin_edges)

x_curve = np.linspace(bin_edges[0], bin_edges[-1], 300)
curve_y = norm.pdf(x_curve, loc=true_mu, scale=true_sigma) * n_samples * bin_width

# -------------------------------
# STAT CARDS
# -------------------------------
 
st.markdown(f"""
<div class="stats-row-2" >
  <div class="stat-card alpha">
    <span class="stat-label">Gemiddelde</span>
    <span class="stat-value">{all_means.mean():.4f}</span>
    <span class="stat-desc">Steeds dichter bij 0 (als n &rightarrow; &#8734;) </span>
  </div>
  <div class="stat-card beta">
    <span class="stat-label">Standaardafwijking</span>
    <span class="stat-value">{all_means.std():.4f}</span>
    <span class="stat-desc">Steeds dichter bij &sigma; / &radic; n = {true_sigma:.4f} (als n &rightarrow; &#8734;)</span>
  </div>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# PLOT
# --------------------------------------------------

fig = go.Figure()

fig.add_trace(go.Bar(
    x=bin_centers,
    y=counts,
    width=bin_width * 0.95,
    marker=dict(color="steelblue", opacity=0.75),
    name="Steekproefgemiddelden",
))

obs = "observatie" if sample_size == 1 else "observaties"
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="JetBrains Mono, monospace", color="#f1faee"),
    title=dict(
        text=f"Histogram van steekproefgemiddelden<br><sup>(gebaseerd op {n_samples} steekproeven van {sample_size} observaties uit de {dist_selector} verdeling)</sup>",
        font=dict(size=30, family="JetBrains Mono, monospace", color="#f1faee"),
    ),
    xaxis=dict(
        title=dict(text=r"Steekproefgemiddelde", font=dict(size=25)),
        tickfont=dict(size=20)
    ),
    yaxis = dict(
        title=dict(text = "Frequentie", font=dict(size=25)),
        tickfont=dict(size=20)
    ),
    legend=dict(x=0.75, y=0.95),
    height=500
)

# --------------------------------------------------
# RENDER
# --------------------------------------------------
st.plotly_chart(fig, use_container_width=True, config=dict(displayModeBar=False))

explanation_title = """📊 Interactieve plot: de centrale limietstelling"""
explanation_markdown = """

## 📜 Wat is de centrale limietstelling?
De **centrale limietstelling (CLS)** is een fundamenteel statistisch principe.
Het zegt dat, ongeacht de oorspronkelijke verdeling van een kansvariabele in een populatie, de gemiddelden van voldoende grote steekproeven altijd een **normale verdeling** benaderen.

Met andere woorden: zelfs als je begint met een chaotische of scheve verdeling, dan nog zal het **steekproefgemiddelde** uiteindelijk een belkromme vormen wanneer de steekproefgrootte groot genoeg is.
Wiskundig opgeschreven geldt volgens de **centrale limietstelling** dat het steekproefgemiddelde
$$
    \\overline{X} = \\frac{X_1+X_2+\\ldots + X_n}{n}
$$
bij een voldoende grote waarde voor $$n$$ een normale verdeling benadert, oftewel
$$
    \\overline{X} \sim N(\\mu; \\frac{\\sigma}{\\sqrt{n}}).
$$
Merk op dat $\\overline{X}$ een kansvariabele is, aangezien we niet van te voren al weten hoe de steekproef er precies uit gaat zien. 
Vandaar dat we spreken over kansverdelingen van steekproefgemiddelden.

## 🔢 Hoe werkt het?
1. Kies een kansverdeling (*normale, uniforme, exponenti&#235;le, binomiale of Poisson*).
2. Stel de **steekproefgrootte $n$** in: hoeveel trekkingen uit de gekozen kansverdeling bevat elke steekproef?
3. Pas het **aantal steekproeven** aan: hoeveel steekproeven moeten worden genomen om de histogram mee te cre\"eren?
4. Selecteer waardes voor de parameters, afhankelijk van de gekozen kansverdeling (*bijv. mu en sigma voor normaal, lambda voor exponentieel*).
5. Bekijk het histogram dat we krijgen door voor het gegeven 'Aantal steekproeven' van grootte $n$ het gemiddelde te bepalen.
Hoe verandert de kansverdeling van de steekproefgemiddelden naarmate er meer steekproeven worden toegevoegd?

## 🔍 Wat kun je observeren?
- Bij een groter aantal steekproeven is de simulatie iets trager, maar laat het wel het principe van de centrale limietstelling het best illustreren.
- Bij een steekproefgrootte $n = 1$ en een groot aantal steekproeven, zou je de originele kansverdeling moeten kunnen herkennen in de histogram die wordt geïllustreerd.
- Bij kleine steekproefgroottes kan de verdeling van de steekproefgemiddelden er nog grillig uitzien.
- Naarmate de **steekproefgrootte** $n$ toeneemt, zie je dat de histogram van steekproefgemiddelden steeds meer op een normale verdeling gaat lijken. Het maakt niet uit met welke oorspronkelijke verdeling je bent begonnen!

## 🧠 Waarom is de centrale limietstelling zo belangrijk?
De centrale limietstelling is een krachtige eigenschap die in statistiek wordt gebruikt om voorspellingen te maken over de eigenschappen van de gehele populatie! Daarnaast is van veel verschijnselen in de echte wereld die je als kansvariabele kunt modelleren niet bekend wat de onderliggende kansverdeling is. 
Deze stelling biedt ons handvatten om hier toch zinnige statistische voorspellingen mee te kunnen maken. 
In het geval dat de onderliggende kansverdeling wel bekend is, dan zijn zeer complexe berekeningen nodig om de exacte kansverdeling van het steekproefgemiddelde te bepalen ($n$-voudige integralen!).

## 🎯 Probeer het zelf!
Experimenteer zelf met de **parameters** om te ontdekken hoe de centrale limietstelling in actie werkt!
"""

show_explanation(explanation_title, explanation_markdown)