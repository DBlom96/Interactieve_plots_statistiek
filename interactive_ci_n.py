import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import mplcyberpunk
from scipy.stats import norm
from utils.streamlit_utils import generate_streamlit_page

# Paginalay-out instellen op breed
st.set_page_config(layout="wide")

def plot_confidence_interval_given_sample_size(axes, user_inputs):
    """
    Plot het betrouwbaarheidsinterval voor een populatiegemiddelde op basis van opgegeven parameters.

    Args:
        axes: matplotlib-axes object.
        user_inputs: Dictionary met 'sigma', 'sample_mean', 'n' en 'alpha'.
    """
    sigma = user_inputs["sigma"]
    xbar = user_inputs["sample_mean"]
    n = user_inputs["n"]
    alpha = user_inputs["alpha"]

    if n <= 0:
        st.error("De steekproefgrootte moet groter zijn dan 0.")
        return

    sample_std = sigma / np.sqrt(n)
    shift = 0
    z_critical_left = max(-4, norm.ppf(alpha / 2 + shift))
    z_critical_right = min(4, norm.ppf(1 - alpha / 2 + shift))

    ci_left = xbar + z_critical_left * sample_std
    ci_right = xbar + z_critical_right * sample_std

    mu_lower = ci_left
    mu_upper = ci_right

    # Constante instellingen
    X_LIM_MIN = mu_lower - 4 * sample_std
    X_LIM_MAX = mu_upper + 4 * sample_std
    x_range = np.linspace(X_LIM_MIN, X_LIM_MAX, 1000)
    y_lower = norm.pdf(x_range, loc=mu_lower, scale=sample_std)
    y_upper = norm.pdf(x_range, loc=mu_upper, scale=sample_std)

    yval = -0.1 * max(y_lower)
    epsilon = 0.3 * yval

    # Titel instellen
    suptitle = f"Berekening van een {(1-alpha):.0%}-betrouwbaarheidsinterval voor het populatiegemiddelde ($\\mu$), gegeven $\\sigma={sigma}$ en $n={n}$."
    title = f"Interval van {mu_lower:.2f} tot {mu_upper:.2f} met breedte {(mu_upper - mu_lower):.2f}"
    
    st.subheader(suptitle)
    
    st.write("""In deze interactieve plot wordt het betrouwbaarheidsinterval bepaald voor de populatiegemiddelde $\\mu$ van een normale verdeling met bekende standaardafwijking $\\sigma$.
            Hierbij wordt gekeken voor welke mogelijke waardes voor $\\mu$ het waargenomen steekproefgemiddelde binnen het voorspellingsinterval valt.
            De paarse normale verdeling correspondeert met de laagst mogelijke waarde van $\\mu$ waarvoor $\\bar{x}$ in het voorspellingsinterval ligt.
            de groene normale verdeling correspondeert met de hoogst mogelijke waarde van $\\mu$ waarvoor $\\bar{x}$ in het voorspellingsinterval ligt.
            """       
    )
    
    plt.suptitle(title)

    color_cycle = iter(["red", "blue", "green"])

    axes[0].set_xlim(X_LIM_MIN, X_LIM_MAX)
    axes[0].set_xlabel("Mogelijke waarden van het populatiegemiddelde ($\\mu$)")
    axes[0].set_ylabel("Waarschijnlijkheidsdichtheid van steekproefgemiddelden")

    axes[0].scatter(xbar, 0, marker="x", color="red", label=f"Gemeten steekproefgemiddelde $\\bar{{x}} = {xbar}$")

    for mu, y, label in [(mu_lower, y_lower, "Normale verdeling bij linkergrens"), (mu_upper, y_upper, "Normale verdeling bij rechtergrens")]:
        color = next(color_cycle)
        axes[0].plot(x_range, y, color=color)
        axes[0].plot([mu, mu], [0, norm.pdf(mu, mu, sample_std)], color=color, linestyle="--")
        axes[0].plot([mu, mu], [yval+epsilon, yval-epsilon], color=color)
        axes[0].fill_between(x_range, 0, y, where=((x_range >= mu + z_critical_left*sample_std) & (x_range <= mu + z_critical_right*sample_std)), color=color, alpha=0.3)
        axes[0].plot([], [], ' ', color=color, label=f"{label}: {mu:.4f}")

    # Teken het interval onderaan
    color = next(color_cycle)
    axes[0].plot([mu_lower, mu_upper], [yval, yval], color=color, lw=1)
    axes[0].plot([], [], ' ', color=color, label=f"Breedte betrouwbaarheidsinterval: {(mu_upper - mu_lower):.4f}")

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
