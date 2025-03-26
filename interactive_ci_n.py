import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from scipy.stats import norm

# Paginalay-out instellen op breed
st.set_page_config(layout="wide")

# Titel en uitleg
st.markdown("### Betrouwbaarheidsinterval voor het populatiegemiddelde ($\\mu$)")
# st.write("""
# Deze app berekent het **betrouwbaarheidsinterval** voor het populatiegemiddelde $\\mu$
# gegeven een steekproefgemiddelde $\\bar{x}$, standaardafwijking $\\sigma$, en steekproefgrootte $n$.
# Daarnaast toont het de twee grensgevallen waarin $\\bar{x}$ net binnen het voorspellingsinterval ligt.
# """)

# **Zijbalk voor gebruikersinvoer**
with st.sidebar:
    st.header("Sliders voor parameters")
    
    # Schuifbalken voor parameters
    sigma = st.slider("Standaardafwijking ($\\sigma$)", min_value=0.1, max_value=20.0, value=8.0, step=0.1)
    xbar = st.slider("Steekproefgemiddelde ($\\bar{x}$)", min_value=60.0, max_value=90.0, value=73.48, step=0.01)
    n = st.slider("Steekproefgrootte ($n$)", min_value=1, max_value=100, value=1, step=1)
    alpha = st.slider("Significantieniveau ($\\alpha$)", min_value=0.01, max_value=0.1, value=0.05, step=0.01)
    # shift = st.slider("Verschuiving", min_value=-1.0*alpha/2, max_value=1.0*alpha/2, value=0.0, step=0.005)

# Berekeningen
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
x_range = np.linspace(mu_lower - 4 * sigma, mu_upper + 4 * sigma, 1000)
y_lower = norm.pdf(x_range, loc=mu_lower, scale=sample_std)
y_upper = norm.pdf(x_range, loc=mu_upper, scale=sample_std)

# **Leeg de plotruimte voordat een nieuwe wordt weergegeven**
plot_placeholder = st.empty()

# **Plot de verdelingen**
fig, ax = plt.subplots(figsize=(10, 5))
yval = -0.1 * max(y_lower)
epsilon = 0.3 * yval

# **Markeer het steekproefgemiddelde**
ax.scatter(xbar, 0, marker="x", color="red", label=f"$\\bar{{x}}: {xbar}$")

# **Normale verdeling voor de onderste grens**
ax.plot(x_range, y_lower, color="blue")
ax.plot([mu_lower, mu_lower], [0, norm.pdf(mu_lower, mu_lower, sample_std)], color="blue", linestyle="--")
ax.plot([mu_lower, mu_lower], [yval+epsilon, yval-epsilon], color="black", linestyle="-")
ax.plot([], [], ' ', label=f"Linkergrens: {mu_lower:.4f}")
ax.fill_between(x_range, 0, y_lower, where=((x_range>=mu_lower+z_critical_left*sample_std)&(x_range<=mu_lower+z_critical_right*sample_std)), color='blue', alpha=0.3)

# **Normale verdeling voor de bovenste grens**
ax.plot(x_range, y_upper, color="green")
ax.plot([mu_upper, mu_upper], [0, norm.pdf(mu_upper, mu_upper, sample_std)], color="green", linestyle="--")
ax.plot([mu_upper, mu_upper], [yval+epsilon, yval-epsilon], color="black", linestyle="-")
ax.plot([], [], ' ', label=f"Rechtergrens: {mu_upper:.4f}")
ax.fill_between(x_range, 0, y_upper, where=((x_range>=mu_upper+z_critical_left*sample_std)&(x_range<=mu_upper+z_critical_right*sample_std)), color='green', alpha=0.3)

# draw horizontal line indicating the confidence interval
ax.plot([mu_lower, mu_upper], [yval, yval], lw=1, color="black")
ax.plot([], [], ' ', label=f"Intervalbreedte: {(mu_upper-mu_lower):.4f}")

# Labels en opmaak
ax.set_title(f"{int(100*(1-alpha))}%-betrouwbaarheidsinterval voor $\\mu$")
ax.set_xlabel("Populatiegemiddelde ($\\mu$)")
ax.set_ylabel("Kansdichtheid")
ax.legend()

# **Toon de plot in de gereserveerde ruimte**
plt.tight_layout(pad=1)  # Adjust padding between subplots and edges
plot_placeholder.pyplot(fig)