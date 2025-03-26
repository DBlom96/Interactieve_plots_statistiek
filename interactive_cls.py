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
    sns.histplot(sample_means, bins=30, kde=True, color='blue', label="Sample Means")
    plt.axvline(np.mean(sample_means), color='red', linestyle='dashed', label=f'Mean: {np.mean(sample_means):.2f}')
    plt.suptitle(f"Central Limit Theorem: Means of {dist} Distributed Variables")
    plt.title(f'Sample Size = {sample_size}, Number of Samples = {n_samples}')
    plt.xlabel("Sample Mean")
    plt.ylabel("Frequency")
    plt.legend()
    st.pyplot(plt)

# Streamlit widgets for user input
dist_selector = st.selectbox("Distribution:", ["normaal", "uniform", "exponentieel", "binomiaal", "Poisson"])
sample_size_slider = st.slider("Sample Size:", min_value=1, max_value=500, step=1, value=30)
n_samples_slider = st.slider("Number of Samples:", min_value=1, max_value=100_000, step=10, value=1000)
 
# Specific sliders for each distribution
mu_slider = st.slider("Mean $mu$:", min_value=-10, max_value=10, step=0.5, value=0)
sigma_slider = st.slider("Standard Deviation $sigma$:", min_value=0.1, max_value=5, step=0.1, value=1)
a_slider = st.slider("Uniform $a$:", min_value=-10, max_value=0, step=0.5, value=-5)
b_slider = st.slider("Uniform $b$:", min_value=0, max_value=10, step=0.5, value=5)
lambda_slider = st.slider("Exponential $\\lambda$:", min_value=0.1, max_value=5, step=0.1, value=1)
n_slider = st.slider("Binomial $n$:", min_value=1, max_value=100, step=1, value=10)
p_slider = st.slider("Binomial $p$:", min_value=0.0, max_value=1.0, step=0.01, value=0.5)

# Update plot based on user inputs
params = {
    "mu": mu_slider,
    "sigma": sigma_slider,
    "a": a_slider,
    "b": b_slider,
    "lambda_": lambda_slider,
    "n": n_slider,
    "p": p_slider
}

plot_clt(dist_selector, n_samples_slider, sample_size_slider, **params)