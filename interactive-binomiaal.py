import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from scipy.stats import binom
from utils.plot_utils import generate_streamlit_page

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
        n_slider = st.slider(label="Aantal Bernoulli-experimenten $n$", min_value=5, max_value=100, value=20, step=1)
        p_slider = st.slider(label="Succeskans $p$", min_value=0.1, max_value=0.99, value=0.5, step=0.01)
    
    slider_dict = {"n": n_slider, "p": p_slider}
    return slider_dict

slider_dict = add_sidebar_binomiale_verdeling()

# Generate the Streamlit page with the sidebar and plot
title="Interactieve plot: de binomiale verdeling"
xlabel="Aantal successen $k$"
ylabel="Kansfunctie $f(k)$"

# Call generate_streamlit_page with the plot_binomiale_verdeling function
generate_streamlit_page(
    slider_dict, 
    plot_binomiale_verdeling, 
    title=title, 
    xlabel=xlabel, 
    ylabel=ylabel,
    subplot_dims=(1, 1)  # Single plot (1x1)
)