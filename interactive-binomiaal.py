import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import mplcyberpunk
from scipy.stats import binom
from plot_utils import create_figure, add_sidebar, colors

# Define parameters for the sidebar
sidebar_params = {
    "n": {"label": "Aantal Bernoulli-experimenten $n$", "min": 5, "max": 100, "value": 20, "step": 1},
    "p": {"label": "Succeskans $p$", "min": 0.01, "max": 0.99, "value": 0.5, "step": 0.01}
}

# Get user-selected values from the sidebar
user_inputs = add_sidebar(sidebar_params)
print(user_inputs)
n = user_inputs["n"]
p = user_inputs["p"]

# Streamlit App Titel
st.subheader("Binomiale verdeling")

# Functie om de binomiale verdeling te plotten
def plot_binomiale_verdeling(n, p):
    x = np.arange(0, n + 1)  # Mogelijke uitkomsten
    binom_pmf = binom.pmf(x, n, p)  # Binomiale kansfunctie

    # Maak de plot
    fig, ax = create_figure(figsize=(10, 6), 
                            title=f'Binomiale verdeling met parameters $n={n}$ en $p={p:.2f}$',
                            xlabel='Aantal successen $k$',
                            ylabel='Kansfunctie $f(k)$'
                        )
    ax.stem(x, binom_pmf, linefmt='-', markerfmt='o', basefmt=" ")

    # legenda
    ax.legend()

    # Plot weergeven in Streamlit
    st.empty()
    mplcyberpunk.make_lines_glow()
    plt.tight_layout()
    st.pyplot(fig)

# Genereer de plot met de geselecteerde waarden
plot_binomiale_verdeling(n, p)
