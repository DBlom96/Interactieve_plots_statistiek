import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from scipy.stats import norm
st.set_page_config(layout="wide")

# Streamlit App Title
st.subheader("Betekenis van het concept 'betrouwbaarheid'")

# User Inputs via Streamlit Sliders
# **Zijbalk voor gebruikersinvoer**
with st.sidebar:
    st.header("Sliders voor parameters")
    mu = st.slider("Populatiegemiddelde ($\\mu$, eigenlijk onbekend!)", min_value=-10, max_value=10, value=0, step=1)
    sigma = st.slider("Standaardafwijking $\\sigma$", min_value=1, max_value=10, value=1, step=1)
    sample_size = st.slider("Steekproefgrootte $n$", min_value=1, max_value=1_000, value=1, step=1)
    num_samples = st.slider("Aantal steekproeven", min_value=5, max_value=500, value=10, step=1)

# Fixed parameters
alpha = 0.05
z_critical = norm.ppf(1 - alpha / 2)  # Z-score for 95% confidence interval

# Function to plot confidence intervals
def plot_intervals(mu, sigma, sample_size, num_samples):
    fig, ax = plt.subplots(figsize=(12, 8))
    count_include_mu = 0

    for i in range(num_samples):
        sample = np.random.normal(mu, sigma, sample_size)
        sample_mean = np.mean(sample)
        sample_std = sigma / np.sqrt(sample_size)
        margin_of_error = z_critical * sample_std
        ci_left, ci_right = sample_mean - margin_of_error, sample_mean + margin_of_error
        
        if ci_left <= mu <= ci_right:
            count_include_mu += 1
            color = "green"
        else:
            color = "red"

        ax.plot([ci_left, ci_right], [i, i], marker="|", color=color)
        ax.scatter(sample_mean, i, color=color)  # Sample mean marker

    ax.axvline(mu, color="black", linestyle="--", label=f"$\\mu={mu}$ (onbekend!)")
    ax.set_title(f"Aantal {int(100*(1-alpha))}%-betrouwbaarheidsintervallen dat $\\mu$ bevat: "
                 f"{count_include_mu} van de {num_samples} ({(count_include_mu / num_samples * 100):.2f}%)")
    ax.set_xlabel("$x$")
    ax.set_ylabel("Steekproefindex")
    ax.legend()

    # Adjust layout to avoid overlap
    plt.tight_layout()
    st.empty()    
    st.pyplot(fig)  # Display the plot in Streamlit

# Generate and display the plot
plot_intervals(mu, sigma, sample_size, num_samples)
