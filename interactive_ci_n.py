import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import mplcyberpunk
from scipy.stats import norm
from plot_utils import cyberpunk_color_cycle, generate_streamlit_page

# Paginalay-out instellen op breed
st.set_page_config(layout="wide")

# Titel en uitleg
# st.markdown("### Betrouwbaarheidsinterval voor het populatiegemiddelde ($\\mu$)")
# st.write("""
# Deze interactieve plot berekent het **betrouwbaarheidsinterval** voor het populatiegemiddelde $\\mu$
# gegeven een steekproefgemiddelde $\\bar{x}$, standaardafwijking $\\sigma$, en steekproefgrootte $n$.
# Daarnaast toont het de twee grensgevallen waarin $\\bar{x}$ net binnen het voorspellingsinterval ligt.
# """)

def plot_confidence_interval_given_sample_size(axes, user_inputs):
    sigma, xbar, n, alpha = user_inputs.values()

    shift = 0
    sample_std = sigma / np.sqrt(n)  # Standaardfout
    z_critical_left = max(-4, norm.ppf(alpha / 2 + shift))  # Kritieke linker Z-waarde
    z_critical_right = min(4, norm.ppf(1 - alpha / 2 + shift)) # Kritieke rechter Z-waarde

    # Grenzen van het betrouwbaarheidsinterval
    ci_left = xbar + z_critical_left * sample_std
    ci_right = xbar + z_critical_right * sample_std

    # Bepalen van de grensgevallen voor μ
    mu_lower = ci_left  # Kleinste μ waarbij x̄ net binnen het interval valt
    mu_upper = ci_right  # Grootste μ waarbij x̄ net binnen het interval valt

    # X-waarden genereren voor de normale verdelingen
    axes[0].set_xlim(30, 120)
    x_range = np.linspace(30, 120, 1_000) #mu_lower - 4 * sigma, mu_upper + 4 * sigma, 1000)
    y_lower = norm.pdf(x_range, loc=mu_lower, scale=sample_std)
    y_upper = norm.pdf(x_range, loc=mu_upper, scale=sample_std)

    yval = -0.1 * max(y_lower)
    epsilon = 0.3 * yval

    # Update suptitle and title
    suptitle=f"Interactieve plot: {(1-alpha)}-betrouwbaarheidsinterval voor $\\mu$ (voor bekende $\\sigma={sigma}$ en $n={n}$)"
    title=f"De breedte van het betrouwbaarheidsinterval [{mu_lower:.2f}; {mu_upper:.2f}] is gelijk aan {(mu_upper - mu_lower):.2f}"
    st.subheader(suptitle)
    plt.suptitle(title)

    # Get the current color cycle from matplotlib after applying the cyberpunk style   
    idx = 0
    color_cycle = cyberpunk_color_cycle()
    color = color_cycle[idx]
    
    axes[0].scatter(xbar, 0, marker="x", color="red", label=f"$\\bar{{x}}: {xbar}$")

    # **Normale verdeling voor de onderste grens**
    axes[0].plot(x_range, y_lower, color=color)
    axes[0].plot([mu_lower, mu_lower], [0, norm.pdf(mu_lower, mu_lower, sample_std)], color=color, linestyle="--")
    axes[0].plot([mu_lower, mu_lower], [yval+epsilon, yval-epsilon], color=color, linestyle="-")
    axes[0].plot([], [], ' ', color=color, label=f"Linkergrens: {mu_lower:.4f}")
    axes[0].fill_between(x_range, 0, y_lower, color=color, where=((x_range>=mu_lower+z_critical_left*sample_std)&(x_range<=mu_lower+z_critical_right*sample_std)), alpha=0.3)

    # **Normale verdeling voor de bovenste grens**
    idx += 1
    color = color_cycle[idx]
    axes[0].plot(x_range, y_upper, color=color)
    axes[0].plot([mu_upper, mu_upper], [0, norm.pdf(mu_upper, mu_upper, sample_std)], color=color, linestyle="--")
    axes[0].plot([mu_upper, mu_upper], [yval+epsilon, yval-epsilon], color=color, linestyle="-")
    axes[0].plot([], [], ' ', color=color, label=f"Rechtergrens: {mu_upper:.4f}")
    axes[0].fill_between(x_range, 0, y_upper, color=color, where=((x_range>=mu_upper+z_critical_left*sample_std)&(x_range<=mu_upper+z_critical_right*sample_std)), alpha=0.3)

    # draw horizontal line indicating the confidence interval
    idx += 1
    color = color_cycle[idx]
    axes[0].plot([mu_lower, mu_upper], [yval, yval], color=color, lw=1)
    axes[0].plot([], [], ' ', color=color, label=f"Intervalbreedte: {(mu_upper-mu_lower):.4f}")
    
    # axes[0].legend()

def add_sidebar_ci_n():
    with st.sidebar:
        st.header("Sliders voor parameters")
    
        # Schuifbalken voor parameters
        sigma = st.slider("Standaardafwijking ($\\sigma$)", min_value=1, max_value=20, value=8, step=1)
        xbar = st.slider("Steekproefgemiddelde ($\\bar{x}$)", min_value=60.0, max_value=90.0, value=73.48, step=0.01)
        n = st.slider("Steekproefgrootte ($n$)", min_value=1, max_value=100, value=30, step=1)
        alpha = st.slider("Significantieniveau ($\\alpha$)", min_value=0.01, max_value=0.1, value=0.05, step=0.01)

    slider_dict = {"sigma": sigma, "sample_mean": xbar, "n": n, "alpha": alpha}
    return slider_dict

slider_dict = add_sidebar_ci_n()

# Generate the Streamlit page with the sidebar and plot
title=f"Interactieve plot: betrouwbaarheidsinterval voor $\\mu$"
xlabel="Populatiegemiddelde ($\\mu$)"
ylabel="Kansdichtheid"

# Call generate_streamlit_page with the plot_binomiale_verdeling function
generate_streamlit_page(
    slider_dict, 
    plot_confidence_interval_given_sample_size, 
    title=title, 
    xlabel=xlabel, 
    ylabel=ylabel,
    subplot_dims=(1, 1)  # Single plot (1x1)
)