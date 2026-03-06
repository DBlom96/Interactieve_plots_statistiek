import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import mplcyberpunk
from scipy.stats import norm
from utils.streamlit_utils import generate_streamlit_page

# Paginalay-out instellen op breed
st.set_page_config(layout="wide")

def plot_confidence_interval_given_sample_size(axes, user_inputs):
    sigma = user_inputs["sigma"]
    xbar = user_inputs["sample_mean"]
    n = user_inputs["n"]
    alpha = user_inputs["alpha"]

    mu_true = xbar  # treat slider mean as population mean for simulation

    if "intervals" not in st.session_state:
        st.session_state.intervals = []

    sample_std = sigma / np.sqrt(n)
    z = norm.ppf(1 - alpha/2)

    # Button to generate a new sample
    if st.button("Add new sample"):
        sample_mean = np.random.normal(mu_true, sample_std)

        ci_left = sample_mean - z * sample_std
        ci_right = sample_mean + z * sample_std

        contains_mu = ci_left <= mu_true <= ci_right

        st.session_state.intervals.append(
            (sample_mean, ci_left, ci_right, contains_mu)
        )

    intervals = st.session_state.intervals

    axes[0].clear()

    axes[0].set_xlabel("Population mean μ")
    axes[0].set_ylabel("Samples")
    axes[0].set_title(f"{(1-alpha):.0%} Confidence intervals")

    axes[0].axvline(mu_true, color="yellow", linestyle="--", label="True μ")

    for i, (mean, left, right, contains) in enumerate(intervals):

        color = "lime" if contains else "red"

        axes[0].plot([left, right], [i, i], color=color, lw=3)
        axes[0].scatter(mean, i, color="white", edgecolor="black", zorder=3)

    axes[0].set_ylim(-1, len(intervals)+1)

    axes[0].legend()

def add_sidebar_ci_n():
    """
    Voeg sliders toe aan de Streamlit-sidebar voor parameters van het betrouwbaarheidsinterval.
    """
    with st.sidebar:
        st.header("Parameters instellen")
        st.write("""
        Pas de onderstaande parameters aan om te zien hoe het betrouwbaarheidsinterval verandert.
        De grafiek toont de normale verdelingen bij de grenzen van het interval.
        """)
        sigma = st.slider("Standaardafwijking ($\\sigma$)", min_value=1, max_value=20, value=8, step=1)
        xbar = st.slider("Steekproefgemiddelde ($\\bar{x}$)", min_value=60.0, max_value=90.0, value=73.48, step=0.01)
        n = st.slider("Steekproefgrootte ($n$)", min_value=1, max_value=100, value=30, step=1)
        alpha = st.slider("Significantieniveau ($\\alpha$)", min_value=0.01, max_value=0.1, value=0.05, step=0.01)

    return {"sigma": sigma, "sample_mean": xbar, "n": n, "alpha": alpha}

# Streamlit pagina genereren
slider_dict = add_sidebar_ci_n()

generate_streamlit_page(
    slider_dict,
    plot_confidence_interval_given_sample_size,
    title="Interactieve plot: betrouwbaarheidsinterval voor $\\mu$",
    xlabel="Mogelijke waarden van het populatiegemiddelde ($\\mu$)",
    ylabel="Kansdichtheid van steekproefgemiddelden",
    subplot_dims=(1, 1)
)