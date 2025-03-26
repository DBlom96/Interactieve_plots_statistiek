import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from scipy.stats import norm

# Paginalay-out instellen op breed
st.set_page_config(layout="wide")

# Titel en uitleg
st.title("Betrouwbaarheidsinterval voor het populatiegemiddelde ($\\mu$)")
st.write("""
Deze app berekent het **betrouwbaarheidsinterval** voor het populatiegemiddelde $\\mu$
gegeven een steekproefgemiddelde $\\bar{x}$, standaardafwijking $\\sigma$, en steekproefgrootte $n$.
Daarnaast toont het de twee grensgevallen waarin $\\bar{x}$ net binnen het voorspellingsinterval ligt.
""")

# **Zijbalk voor gebruikersinvoer**
with st.sidebar:
    st.header("Sliders voor parameters")
    
    # Schuifbalken voor parameters
    sigma = st.slider("Standaardafwijking ($\\sigma$)", min_value=0.1, max_value=20.0, value=8.0, step=0.1)
    xbar = st.slider("Steekproefgemiddelde ($\\bar{x}$)", min_value=60.0, max_value=90.0, value=73.48, step=0.01)
    n = st.slider("Steekproefgrootte ($n$)", min_value=5, max_value=500, value=50, step=1)
    alpha = st.slider("Significantieniveau ($\\alpha$)", min_value=0.01, max_value=0.1, value=0.05, step=0.01)

# Berekeningen
sample_std = sigma / np.sqrt(n)  # Standaardfout
z_critical = norm.ppf(1 - alpha / 2)  # Kritieke Z-waarde

# Grenzen van het betrouwbaarheidsinterval
ci_left = xbar - z_critical * sample_std
ci_right = xbar + z_critical * sample_std

# Bepalen van de grensgevallen voor μ
mu_lower = ci_left  # Kleinste μ waarbij x̄ net binnen het interval valt
mu_upper = ci_right  # Grootste μ waarbij x̄ net binnen het interval valt

# X-waarden genereren voor de normale verdelingen
x_range = np.linspace(mu_lower - 4 * sample_std, mu_upper + 4 * sample_std, 1000)
y_lower = norm.pdf(x_range, loc=mu_lower, scale=sample_std)
y_upper = norm.pdf(x_range, loc=mu_upper, scale=sample_std)

# **Leeg de plotruimte voordat een nieuwe wordt weergegeven**
plot_placeholder = st.empty()

# **Plot de verdelingen**
fig, ax = plt.subplots(figsize=(10, 5))

# **Normale verdeling voor de onderste grens**
ax.plot(x_range, y_lower, color="blue")
ax.plot([mu_lower, mu_lower], [0, norm.pdf(mu_lower, mu_lower, sample_std)], color="blue", linestyle="--")
ax.fill_between(x_range, 0, y_lower, where=((x_range>=mu_lower-z_critical*sample_std)&(x_range<=mu_lower+z_critical*sample_std)), color='blue', alpha=0.3)

# **Normale verdeling voor de bovenste grens**
ax.plot(x_range, y_upper, color="green")
ax.plot([mu_upper, mu_upper], [0, norm.pdf(mu_upper, mu_upper, sample_std)], color="green", linestyle="--")
ax.fill_between(x_range, 0, y_upper, where=((x_range>=mu_upper-z_critical*sample_std)&(x_range<=mu_upper+z_critical*sample_std)), color='green', alpha=0.3)

# **Markeer het steekproefgemiddelde**
ax.scatter(xbar, 0, marker="x", color="red", label=f"$\\bar{{x}}={xbar}$")

# Labels en opmaak
ax.set_title(f"{int(100*(1-alpha))}%-betrouwbaarheidsinterval voor $\\mu$\nOndergrens: {mu_lower:.2f}, Bovengrens: {mu_upper:.2f}")
ax.set_xlabel("Populatiegemiddelde ($\\mu$)")
ax.set_ylabel("Kansdichtheid")
ax.legend()

# **Toon de plot in de gereserveerde ruimte**
plot_placeholder.pyplot(fig)

# Weergave van samenvattende statistieken onder de grafiek
st.markdown("### Samenvattende Statistieken")
st.write(f"📌 **Ondergrens betrouwbaarheidsinterval:** {ci_left:.4f}")
st.write(f"📌 **Bovengrens betrouwbaarheidsinterval:** {ci_right:.4f}")
st.write(f"📌 **Breedte van het betrouwbaarheidsinterval:** {(ci_right-ci_left):.4f}")