import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import mplcyberpunk
from scipy.stats import binom
from plot_utils import generate_streamlit_page

# Define parameters for the sidebar
sidebar_params = {
    "n": {"label": "Aantal Bernoulli-experimenten $n$", "min": 5, "max": 100, "value": 20, "step": 1},
    "p": {"label": "Succeskans $p$", "min": 0.01, "max": 0.99, "value": 0.5, "step": 0.01}
}

# Function to plot the binomial distribution
def plot_binomiale_verdeling(ax, user_inputs):
    n = user_inputs["n"]
    p = user_inputs["p"]

    x = np.arange(0, n + 1)  # Mogelijke uitkomsten
    binom_pmf = binom.pmf(x, n, p)  # Binomiale kansfunctie

    # Maak de plot
    ax.stem(x, binom_pmf, linefmt='-', markerfmt='o', basefmt=" ", label="Kansfunctie")
    ax.legend()

# Generate the Streamlit page with the sidebar and plot
title="Interactieve plot: de binomiale verdeling"
xlabel="Aantal successen $k$"
ylabel="Kansfunctie $f(k)$"

generate_streamlit_page(sidebar_params, plot_binomiale_verdeling, title=title, xlabel=xlabel, ylabel=ylabel)
