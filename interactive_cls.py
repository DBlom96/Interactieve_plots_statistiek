import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from scipy.stats import norm, uniform, expon, binom, poisson
from utils.streamlit_utils import generate_streamlit_page

st.set_page_config(layout="wide")

# Function to generate sample means
def generate_sample_means(dist, n_samples, sample_size, **params):
    if dist == "normaal":
        samples = norm.rvs(loc=params["mu"], scale=params["sigma"], size=(sample_size, n_samples))
    elif dist == "uniform":
        samples = uniform.rvs(loc=params["a"], scale=params["b"] - params["a"], size=(sample_size, n_samples))
    elif dist == "exponentieel":
        samples = expon.rvs(scale=1/params["lambda_"], size=(sample_size, n_samples))
    elif dist == "binomiaal":
        samples = binom.rvs(n=params["n"], p=params["p"], size=(sample_size, n_samples))
    elif dist == "Poisson":
        samples = poisson.rvs(mu=params["lambda_"], size=(sample_size, n_samples))
    else:
        raise ValueError("Onbekende verdeling")
    return samples.mean(axis=0)  # Sample means
 
# Function to plot the graph
def plot_clt(axes, user_inputs):
    sample_means = generate_sample_means(**user_inputs)
    num_bins = 50#int(np.sqrt(n_samples))

    sns.histplot(sample_means, bins=num_bins, kde=False, label="Steekproefgemiddelden", ax=axes[0])

def add_sidebar_clt():
    with st.sidebar:
        st.header("Sliders voor parameters")

        # Streamlit widgets for user input
        dist_selector = st.selectbox("Kansverdeling:", ["normaal", "uniform", "exponentieel", "binomiaal", "Poisson"])
        sample_size_slider = st.slider("Steekproefgrootte:", min_value=1, max_value=100, step=1, value=30)
        n_samples_slider = st.slider("Aantal steekproeven:", min_value=1, max_value=100_000, step=1, value=1000)

        slider_dict = {
            "dist": dist_selector, 
            "sample_size": sample_size_slider,
            "n_samples": n_samples_slider
        }

        # Specific sliders for each distribution
        if dist_selector == "normaal":
            mu_slider = st.slider("Gemiddelde $\\mu$:", min_value=-10.0, max_value=10.0, step=0.5, value=0.0)
            sigma_slider = st.slider("Standaardafwijking $\\sigma$:", min_value=0.1, max_value=5.0, step=0.1, value=1.0)
            slider_dict.update({"mu": mu_slider, "sigma": sigma_slider})
        elif dist_selector == "uniform":
            a_slider = st.slider("Ondergrens $a$:", min_value=-10.0, max_value=0.0, step=0.5, value=-5.0)
            b_slider = st.slider("Bovengrens $b$:", min_value=0.0, max_value=10.0, step=0.5, value=5.0)
            slider_dict.update({"a": a_slider, "b": b_slider})
        elif dist_selector in ["Poisson", "exponentieel"]:
            lambda_slider = st.slider("$\\lambda$:", min_value=0.1, max_value=5.0, step=0.1, value=1.0)
            slider_dict.update({"lambda_": lambda_slider})
        elif dist_selector == "binomiaal":
            n_slider = st.slider("Aantal Bernoulli-experimenten $n$:", min_value=1, max_value=100, step=1, value=10)
            p_slider = st.slider("Succeskans $p$:", min_value=0.0, max_value=1.0, step=0.01, value=0.5)
            slider_dict.update({"n": n_slider, "p": p_slider})
    return slider_dict

slider_dict = add_sidebar_clt()

page_header="📊 Interactieve plot: de centrale limietstelling"
if slider_dict["n_samples"] == 1:
    plot_title = f"Histogram voor steekproefgemiddelden van {slider_dict["sample_size"]} {slider_dict["dist"]} verdeelde kansvariabele (op basis van {slider_dict["n_samples"]} steekproeven)."
else:
    plot_title = f"Histogram voor steekproefgemiddelden van {slider_dict["sample_size"]} {slider_dict["dist"]} verdeelde kansvariabelen (op basis van {slider_dict["n_samples"]} steekproeven)."

xlabel="Steekproefgemiddelde $\\bar{x}$"
ylabel="Frequentie"

explanation_title = """# 📊 Interactieve plot: de centrale limietstelling"""
explanation_markdown = """
Deze interactieve visualisatie laat zien hoe de **centrale limietstelling** (CLS) werkt:
ongeacht de oorspronkelijke verdeling van een populatie, zullen de gemiddelden van voldoende grote steekproeven altijd een **normale verdeling** benaderen.

Stel dat we te maken hebben met een reeks onafhankelijke kansvariabelen $$X_1, X_2, \ldots, X_n$$ met dezelfde kansverdeling,
waarvoor geldt dat de verwachtingswaarde gelijk is aan $$\mu$$ en de standaardafwijking gelijk is aan $$\\sigma$$.

Volgens de **centrale limietstelling** geldt dat het steekproefgemiddelde
$$
    \\overline{X} = \\frac{X_1+X_2+\\ldots + X_n}{n}
$$
bij een voldoende grote waarde voor $$n$$ een normale verdeling benadert, namelijk bij benadering geldt
$$
    X \sim N(\\mu; \\frac{\\sigma}{n}).
$$

## 🔢 Hoe werkt het?
1. Kies een kansverdeling (*normaal, uniform, exponentieel, binomiaal of Poisson*).
2. Stel de **steekproefgrootte** in: Hoeveel waarnemingen bevat elke steekproef?
3. Pas het **aantal steekproeven** aan: Hoeveel steekproeven worden genomen?
4. Selecteer parameters die de verdeling specificeren (*bijv. mu en sigma voor normaal, lambda voor exponentieel*).
5. Bekijk de histogram van de steekproefgemiddelden: Hoe veranderen ze naarmate meer steekproeven worden toegevoegd?

## 🔍 Wat kun je observeren?
- Bij een kleine steekproefgrootte kan de verdeling van de steekproefgemiddelden er grillig uitzien.
- Naarmate de **steekproefgrootte** toeneemt, worden de steekproefgemiddelden steeds meer normaal verdeeld, ongeacht de oorspronkelijke verdeling.
- Dit is een krachtige eigenschap die in statistiek wordt gebruikt om inferenties te maken over populaties!

🎯 **Experimenteer** met de sliders en zie hoe de centrale limietstelling in actie werkt!
"""

# Call generate_streamlit_page with the plot_binomiale_verdeling function
generate_streamlit_page(
    sliders=slider_dict, 
    plot_function=plot_clt, 
    page_header=page_header,
    plot_title=plot_title, 
    xlabel=xlabel, 
    ylabel=ylabel,
    explanation_md=(explanation_title, explanation_markdown),
    subplot_dims=(1, 1)  # Single plot (1x1)
)