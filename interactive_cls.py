import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from scipy.stats import norm, uniform, expon, binom, poisson
from plot_utils import generate_streamlit_page

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
    dist = user_inputs['dist']
    n_samples = user_inputs['n_samples']
    sample_size = user_inputs['sample_size']
    sample_means = generate_sample_means(**user_inputs)
   
    sns.histplot(sample_means, bins=30, kde=False, color='blue', label="Steekproefgemiddelden", ax=axes[0])
    plt.title(f'Steekproefgrootte = {sample_size}, aantal steekproeven = {n_samples}')
    plt.xlabel("Steekproefgemiddelde")
    plt.ylabel("Frequentie")


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

title="Interactieve plot: de centrale limietstelling"
xlabel="Steekproefgemiddelde $\\bar{x}$"
ylabel="Frequentie"

# Call generate_streamlit_page with the plot_binomiale_verdeling function
generate_streamlit_page(
    slider_dict, 
    plot_clt, 
    title=title, 
    xlabel=xlabel, 
    ylabel=ylabel,
    subplot_dims=(1, 1)  # Single plot (1x1)
)