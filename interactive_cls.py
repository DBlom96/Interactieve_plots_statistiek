import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from scipy.stats import norm, uniform, expon, binom, poisson
 
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
def plot_clt(dist, n_samples, sample_size, **params):
    sample_means = generate_sample_means(dist, n_samples, sample_size, **params)
   
    plt.figure(figsize=(8, 5))
    sns.histplot(sample_means, bins=30, kde=True, color='blue', label="Steekproefgemiddelden")
    plt.axvline(np.mean(sample_means), color='red', linestyle='dashed', label=f'Mean: {np.mean(sample_means):.2f}')
    plt.suptitle(f"Centrale limietstelling: gemiddelden van {dist} verdeelde kansvariabelen")
    plt.title(f'Steekproefgrootte = {sample_size}, aantal steekproeven = {n_samples}')
    plt.xlabel("Steekproefgemiddelde")
    plt.ylabel("Frequentie")

    # Adjust layout to avoid overlap
    plt.tight_layout(pad=3.0)
    st.pyplot(plt)

# Headers
st.sidebar.header("Sliders voor parameters")

# Streamlit widgets for user input
dist_selector = st.sidebar.selectbox("Kansverdeling:", ["normaal", "uniform", "exponentieel", "binomiaal", "Poisson"])
sample_size_slider = st.sidebar.slider("Steekproefgrootte:", min_value=1, max_value=500, step=1, value=30)
n_samples_slider = st.sidebar.slider("Aantal steekproeven:", min_value=1, max_value=100_000, step=10, value=1000)
 
# Specific sliders for each distribution
if dist_selector == "normaal":
    mu_slider = st.sidebar.slider("Gemiddelde $\\mu$:", min_value=-10.0, max_value=10.0, step=0.5, value=0.0)
    sigma_slider = st.sidebar.slider("Standaardafwijking $\\sigma$:", min_value=0.1, max_value=5.0, step=0.1, value=1.0)
    params = {"mu": mu_slider, "sigma": sigma_slider}
elif dist_selector == "uniform":
    a_slider = st.sidebar.slider("Ondergrens $a$:", min_value=-10.0, max_value=0.0, step=0.5, value=-5.0)
    b_slider = st.sidebar.slider("Bovengrens $b$:", min_value=0.0, max_value=10.0, step=0.5, value=5.0)
    params = {"a": a_slider, "b": b_slider}
elif dist_selector in ["Poisson", "exponentieel"]:
    lambda_slider = st.sidebar.slider("$\\lambda$:", min_value=0.1, max_value=5.0, step=0.1, value=1.0)
    params = {"lambda_": lambda_slider}
elif dist_selector == "binomiaal":
    n_slider = st.sidebar.slider("Aantal Bernoulli-experimenten $n$:", min_value=1, max_value=100, step=1, value=10)
    p_slider = st.sidebar.slider("Succeskans $p$:", min_value=0.0, max_value=1.0, step=0.01, value=0.5)
    params = {"n": n_slider, "p": p_slider}

# Plots the distribution's sample means using the chosen parameters
st.subheader("Interactieve plot: de centrale limietstelling")
plot_clt(dist_selector, n_samples_slider, sample_size_slider, **params)