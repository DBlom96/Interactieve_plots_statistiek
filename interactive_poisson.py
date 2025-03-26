import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import binom, poisson
import streamlit as st
st.set_page_config(layout="wide")

# Function to plot Binomial and Poisson distributions
def plot_distributions(lmbda, n):
    p = lmbda / n  # Define p for Binomial
    k_values = np.arange(0, max(2 * lmbda, 20))  # Range of k-values for visualization
    
    # Binomial probabilities
    binom_probs = binom.pmf(k_values, n, p)
    
    # Poisson probabilities
    poisson_probs = poisson.pmf(k_values, lmbda)
    
    # Create the figure with two subplots
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Plot the Binomial distribution
    axes[0].stem(k_values, binom_probs, linefmt='b-', markerfmt='bo', basefmt=' ')
    prob = lmbda / n
    if int(prob) == prob:  # If p is an integer
        axes[0].set_title(f"Binomiaal($n={n}$; $p=\\frac{{\\lambda}}{{n}} = {int((lmbda / n))}$)")
    else:  # If p is a float
        axes[0].set_title(f"Binomiaal($n={n}$; $p=\\frac{{\\lambda}}{{n}} \\approx {(lmbda / n):.4f}$)")
    axes[0].set_xlabel("$k$")
    axes[0].set_ylabel("Kansfunctie $f(k)$")
    axes[0].set_xticks(k_values)  # Ensure only integer ticks
    
    # Plot the Poisson distribution
    axes[1].stem(k_values, poisson_probs, linefmt='b-', markerfmt='bo', basefmt=' ')
    axes[1].set_title(f"Poisson($\\lambda={lmbda}$)")
    axes[1].set_xlabel("$k$")
    axes[1].set_ylabel("Kansfunctie $f(k)$")
    axes[1].set_xticks(k_values)  # Ensure only integer ticks
    
    plt.tight_layout()
    st.empty()
    st.pyplot(fig)

# Add sliders for lmbda and n
lmbda = st.sidebar.slider("$\\lambda$", min_value=1.0, max_value=20.0, value=5.0, step=0.1)
n = st.sidebar.slider("Aantal Bernoulli-experimenten $n$:", min_value=5, max_value=500, value=50, step=1)

# Call the plot function
st.subheader("Interactieve plot: connectie tussen de binomiale en Poissonverdeling")
plot_distributions(lmbda, n)
