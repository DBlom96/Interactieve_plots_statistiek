import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import binom, poisson
import streamlit as st
# from plot_utils import generate_streamlit_page
from utils import generate_streamlit_page

st.set_page_config(layout="wide")

# Function to plot Binomial and Poisson distributions
def plot_binomial_poisson(axes, user_inputs):
    lmbda = user_inputs["lmbda"]
    n = user_inputs["n"]
    p = lmbda / n  # Define p for Binomial
    
    k_values = np.arange(0, max(2 * lmbda, 20))  # Range of k-values for visualization
    xticklabels = np.arange(0, len(k_values), max(1, len(k_values) / 10))

    # Binomial probabilities
    binom_probs = binom.pmf(k_values, n, p)
    
    # Poisson probabilities
    poisson_probs = poisson.pmf(k_values, lmbda)
        
    # Plot the Binomial distribution
    axes[0].stem(k_values, binom_probs, linefmt='-', markerfmt='o', basefmt=' ')
    prob = lmbda / n
    if int(prob) == prob:  # If p is an integer
        axes[0].set_title(f"Binomiaal($n={n}$; $p=\\frac{{\\lambda}}{{n}} = {int((lmbda / n))}$)")
    else:  # If p is a float
        axes[0].set_title(f"Binomiaal($n={n}$; $p=\\frac{{\\lambda}}{{n}} \\approx {(lmbda / n):.4f}$)")
    axes[0].set_xlabel("$k$")
    axes[0].set_ylabel("Kansfunctie $f(k)$")
    axes[0].set_xticks(xticklabels)
    
    # Plot the Poisson distribution
    axes[1].stem(k_values, poisson_probs, linefmt='-', markerfmt='o', basefmt=' ')
    axes[1].set_title(f"Poisson($\\lambda={lmbda}$)")
    axes[1].set_xlabel("$k$")
    axes[1].set_ylabel("Kansfunctie $f(k)$")
    axes[1].set_xticks(xticklabels)

def add_sidebar_poisson_verdeling():
    with st.sidebar:
        st.header("Sliders voor parameters")

        # Specific sliders for each distribution
        lambda_slider = st.slider(label="$\\lambda$", min_value=1.0, max_value=20.0, value=1.0, step=0.1)
        n_slider = st.slider(label="Aantal Bernoulli-experimenten $n$", min_value=int(lambda_slider)+1, max_value=500, value=int(lambda_slider)+1, step=1)
    
    slider_dict = {"lmbda": lambda_slider, "n": n_slider}
    return slider_dict

slider_dict = add_sidebar_poisson_verdeling()

# Generate Streamlit page with sidebar and plot
title="Interactieve plot: connectie tussen de binomiale en Poissonverdeling"
xlabel="Aantal successen $k$", 
ylabel="Kansfunctie $f(k)$"

# Call generate_streamlit_page with the plot_binomial_poisson function
generate_streamlit_page(
    slider_dict,
    plot_binomial_poisson, 
    title=title, 
    xlabel=xlabel, 
    ylabel=ylabel, 
    subplot_dims=(1,2)  # Generate two subplots side by side
)

