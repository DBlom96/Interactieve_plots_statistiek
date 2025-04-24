import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from scipy.stats import norm
import mplcyberpunk
from utils.plot_utils import cyberpunk_color_cycle, generate_streamlit_page

# Setting up the page layout to wide
st.set_page_config(layout="wide")

# Title and explanation
st.markdown("### Betekenis van het concept 'betrouwbaarheid'")
st.write("""
Deze interactieve plot berekent voor een gegeven aantal steekproeven van trekking $x_1, x_2, \ldots, x_n$ uit een normale verdeling
met gegeven $\\mu$ en $\\sigma$ het **betrouwbaarheidsinterval** voor het populatiegemiddelde $\\mu$.
Op de $x$-as worden waardes gegeven die het steekproefgemiddelde kan aannemen, met een blauwe verticale lijn om de echte populatieparameter aan te geven.
Op de $y$-as zie je de index van de steekproef: $1, 2, \ldots,$ aantal_steekproeven.
De bolletjes geven het steekproefgemiddelde aan.
                  
Deze plot is bedoeld om te illustreren dat bij een gegeven betrouwbaarheidsniveau $\\alpha$,
de kans dat bij een volgende steekproef het betrouwbaarheidsinterval de echte populatieparameter $\\mu$ zou bevatten gelijk is aan $1-\\alpha$.  
""")
st.markdown("### Interactieve plot: conceptuele betekenis van betrouwbaarheid'")

# Sidebar function for getting user input
def add_sidebar_confidence_interval():
    with st.sidebar:
        st.header("Sliders voor parameters")
        mu = st.slider("Populatiegemiddelde ($\\mu$, eigenlijk onbekend!)", min_value=60, max_value=140, value=100, step=1)
        sigma = st.slider("Standaardafwijking $\\sigma$", min_value=10, max_value=20, value=15, step=1)
        sample_size = st.slider("Steekproefgrootte $n$", min_value=10, max_value=250, value=100, step=1)
        num_samples = st.slider("Aantal steekproeven", min_value=5, max_value=200, value=10, step=1)
        alpha = st.slider("Significantieniveau", min_value=0.01, max_value=0.10, value=0.05, step=0.01)
    slider_dict = {"mu": mu, "sigma": sigma, "sample_size": sample_size, "num_samples": num_samples, "alpha": alpha} 
    return slider_dict

# Function to plot confidence intervals
def plot_confidence_intervals(axes, user_inputs):
    mu, sigma, sample_size, num_samples, alpha = user_inputs.values()
    z_critical = norm.ppf(1 - alpha / 2)

    count_include_mu = 0
    color_cycle = cyberpunk_color_cycle()
    sample_std = sigma / np.sqrt(sample_size)
    margin_of_error = z_critical * sample_std
    
    for i in range(num_samples):
        sample = np.random.normal(mu, sigma, sample_size)
        sample_mean = np.mean(sample)
        
        ci_left, ci_right = sample_mean - margin_of_error, sample_mean + margin_of_error
        
        if ci_left <= mu <= ci_right:
            count_include_mu += 1
            color = color_cycle[1] # "neongreen"
        else:
            color = color_cycle[6] # "tomato red"

        axes[0].plot([ci_left, ci_right], [i, i], marker="|", color=color)
        if i == 0:
            axes[0].scatter(sample_mean, i, color=color, s=100, label="Steekproefgemiddelde")  # Sample mean marker
        else:
            axes[0].scatter(sample_mean, i, color=color, s=100)  # Sample mean marker
    axes[0].axvline(mu, color=color_cycle[2], linestyle="--")
    
    # Update suptitle and title
    axes[0].set_xlim(40, 160)
    axes[0].set_title(f"Aantal {int(100*(1-alpha))}%-betrouwbaarheidsintervallen dat $\\mu={mu}$ bevat: "
                 f"{count_include_mu} van de {num_samples} ({(count_include_mu / num_samples * 100):.2f}%)")
    axes[0].legend()

    # Reset the figsize
    plt.gcf().set_size_inches(12, 0.5 * num_samples)  # Resize the figure to the desired size

slider_dict = add_sidebar_confidence_interval()

# Generate the Streamlit page with the sidebar and plot
title=f""#Interactieve plot: conceptuele betekenis van betrouwbaarheid"
xlabel="$x$"
ylabel="Steekproefindex"

# Call generate_streamlit_page with the plot_binomiale_verdeling function
generate_streamlit_page(
    slider_dict, 
    plot_confidence_intervals, 
    title=title, 
    xlabel=xlabel, 
    ylabel=ylabel,
    subplot_dims=(1, 1)  # Single plot (1x1)
)