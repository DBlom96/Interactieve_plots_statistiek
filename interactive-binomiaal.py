import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from scipy.stats import binom
from utils.streamlit_utils import generate_streamlit_page

st.set_page_config(layout="wide")

# Function to plot the binomial distribution
def plot_binomiale_verdeling(axes, user_inputs):
    n = user_inputs["n"]
    p = user_inputs["p"]

    x = np.arange(0, n + 1)  # Mogelijke uitkomsten
    binom_pmf = binom.pmf(x, n, p)  # Binomiale kansfunctie

    # Maak de plot
    axes[0].stem(x, binom_pmf, linefmt='-', markerfmt='o', basefmt=" ")

def add_sidebar_binomiale_verdeling():
    with st.sidebar:
        st.header("Sliders voor parameters")
        
        # Specific sliders for each distribution
        n_slider = st.slider(label="Aantal Bernoulli-experimenten $n$", min_value=1, max_value=100, value=20, step=1)
        p_slider = st.slider(label="Succeskans $p$", min_value=0.01, max_value=0.99, value=0.5, step=0.01)
    
    slider_dict = {"n": n_slider, "p": p_slider}
    return slider_dict

slider_dict = add_sidebar_binomiale_verdeling()

# Generate the Streamlit page with the sidebar and plot
page_header="📊 Interactieve plot: de binomiale verdeling"
plot_title = f"Naalddiagram van de binomiale verdeling met $n = {slider_dict["n"]}$ en $p = {slider_dict["p"]}$"
xlabel="Aantal successen $k$"
ylabel="Kansfunctie $f(k)$"
explanation_title = "# :book: Uitleg: binomiale verdeling"
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
        P(X=k) = \\binom{n}{k} \cdot p^k \cdot (1 - p)^{n - k}, 
    $$

    waarbij:
    - $$ \\binom{n}{k} $$ de **binomiaalcoefficient** is, oftewel het aantal manieren om uit $n$ pogingen er $k \le n$ te kiezen die succesvol zijn:  
    $$ 
        \\binom{n}{k} = \\frac{n!}{k! \cdot (n-k)!} 
    $$
    - $n$ het **aantal experimenten** is.
    - $p$ de **kans op succes** per experiment is.
    - $k$ het **aantal successen** is.

    ## 📈 Verwachtingswaarde en standaardafwijking
    - **Verwachtingswaarde**:  
    $$ 
        E[X] = n \cdot p 
    $$
    - **Standaardafwijking**:  
    $$
        \sigma(X) = \sqrt{n \cdot p \cdot (1 - p)} 
    $$

    ## 🎯 Voorbeeld: worpen met een eerlijke munt
    Stel dat we een eerlijke munt **10 keer** opgooien en de kans op "kop" is **50\%**. De binomiale verdeling beschrijft dan de kans op **exact 6 keer kop**:

    $$
        P(X=6) = \\binom{10}{6} \cdot (0.5)^6 \cdot (0.5)^4 \\approx 0,2051
    $$
"""

# Call generate_streamlit_page with the plot_binomiale_verdeling function
generate_streamlit_page(
    slider_dict, 
    plot_binomiale_verdeling, 
    page_header=page_header,
    plot_title=plot_title, 
    xlabel=xlabel, 
    ylabel=ylabel,
    explanation_md=(explanation_title, explanation_markdown),
    subplot_dims=(1, 1)  # Single plot (1x1)
)