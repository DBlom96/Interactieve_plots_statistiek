import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy.stats import norm, uniform, expon, binom, poisson

from utils.explanation_utils import show_explanation
from utils.streamlit_utils import load_css, page_header, apply_dark_style
from utils.constants import *

st.set_page_config(
    page_title="De centrale limietstelling",
    initial_sidebar_state="expanded",
    layout="wide"
)

# ----------------------------------
# CSS
# ----------------------------------
load_css()

BG_COLOR = "#1a1f2e"

# ----------------------------------
# PARAMETERS
# ----------------------------------
page_header("📊 Centrale limietstelling", "Statistiek · Visualisatie")

with st.sidebar:
    st.header("Parameters")

    dist_selector = st.selectbox("Kansverdeling:", ["normale", "uniforme", "exponentiële", "binomiale", "Poisson"])
    sample_size   = st.number_input(r"Steekproefgrootte $n$:", min_value=1, value=30)
    n_samples     = st.number_input("Aantal steekproeven:", min_value=1, value=1_000)
    n_bins        = int(np.sqrt(n_samples))

    if dist_selector == "normale":
        mu_val      = st.number_input(r"Gemiddelde $\mu$:", value=0.0)
        sigma_val   = st.number_input(r"Standaardafwijking $\sigma$:", value=1.0)
        dist_params = {"mu": mu_val, "sigma": sigma_val}
        true_mu     = mu_val
        true_sigma  = sigma_val / np.sqrt(sample_size)
    elif dist_selector == "uniforme":
        a_val       = st.number_input(r"Ondergrens $a$:", value=-5.0)
        b_val       = st.number_input(r"Bovengrens $b$:", min_value=a_val + 0.1, value=5.0)
        dist_params = {"a": a_val, "b": b_val}
        true_mu     = (a_val + b_val) / 2
        true_sigma  = (b_val - a_val) / np.sqrt(12 * sample_size)
    elif dist_selector == "exponentiële":
        lam_val     = st.number_input(r"$\lambda$:", min_value=0.1, value=1.0)
        dist_params = {"lambda_": lam_val}
        true_mu     = 1 / lam_val
        true_sigma  = (1 / lam_val) / np.sqrt(sample_size)
    elif dist_selector == "Poisson":
        lam_val     = st.number_input(r"$\lambda$:", min_value=0.1, value=1.0)
        dist_params = {"lambda_": lam_val}
        true_mu     = lam_val
        true_sigma  = np.sqrt(lam_val / sample_size)
    elif dist_selector == "binomiale":
        n_binom     = st.number_input(r"Aantal Bernoulli-experimenten $n$:", min_value=1, value=20)
        p_binom     = st.slider(r"Succeskans $p$:", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
        dist_params = {"n": n_binom, "p": p_binom}
        true_mu     = n_binom * p_binom
        true_sigma  = np.sqrt(n_binom * p_binom * (1 - p_binom) / sample_size)
    
    toggle_normal_curve = st.selectbox("Teken normaalkromme", options=[True, False])

# ----------------------------------
# SAMPLING
# ----------------------------------
def draw_sample_means(dist, sample_size, n_samples, **params):
    if dist == "normale":
        data = norm.rvs(loc=params["mu"], scale=params["sigma"], size=(sample_size, n_samples))
    elif dist == "uniforme":
        data = uniform.rvs(loc=params["a"], scale=params["b"] - params["a"], size=(sample_size, n_samples))
    elif dist == "exponentiële":
        data = expon.rvs(scale=1 / params["lambda_"], size=(sample_size, n_samples))
    elif dist == "binomiale":
        data = binom.rvs(n=params["n"], p=params["p"], size=(sample_size, n_samples))
    elif dist == "Poisson":
        data = poisson.rvs(mu=params["lambda_"], size=(sample_size, n_samples))
    return data.mean(axis=0)

# ----------------------------------
# COMPUTATIONS
# ----------------------------------
all_means = draw_sample_means(dist_selector, sample_size, n_samples, **dist_params)

bin_edges   = np.linspace(all_means.min(), all_means.max(), n_bins + 1)
bin_width   = bin_edges[1] - bin_edges[0]
x_curve     = np.linspace(bin_edges[0], bin_edges[-1], 300)

if dist_selector in ["binomiale", "Poisson"]:
    curve_y     = norm.pdf(x_curve, loc=true_mu, scale=true_sigma) * n_samples / sample_size
else:
    curve_y     = norm.pdf(x_curve, loc=true_mu, scale=true_sigma) * n_samples * bin_width

# ----------------------------------
# STAT CARDS
# ----------------------------------
st.markdown(f"""
<div class="stats-row-2">
  <div class="stat-card alpha">
    <span class="stat-label">Gemiddelde van steekproefgemiddelden</span>
    <span class="stat-value">{all_means.mean():.4f}</span>
    <span class="stat-desc">Steeds dichter bij {to_lowercase(MEAN_HTML)} = {true_mu:.4f} (als <i>n &rightarrow; &#8734;</i>)</span>
  </div>
  <div class="stat-card beta">
    <span class="stat-label">Standaardafwijking van steekproefgemiddelden</span>
    <span class="stat-value">{all_means.std():.4f}</span>
    <span class="stat-desc">Steeds dichter bij {to_lowercase(STD_HTML)} / &radic;<i>n</i> = {true_sigma:.4f} (als <i>n &rightarrow; &#8734;</i>)</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------
# FIGURE
# ----------------------------------
fig, ax = plt.subplots(figsize=(10, 5))

# Histogram bars
ax.bar(
    (bin_edges[:-1] + bin_edges[1:]) / 2,
    np.histogram(all_means, bins=bin_edges)[0],
    width=bin_width * 0.92,
    color=HISTOGRAM_BAR_COLOR,
    alpha=0.75,
    label="Steekproefgemiddelden",
)

if toggle_normal_curve:
    # Theoretical normal overlay
    ax.plot(
        x_curve, curve_y,
        color=H0_COLOR, linewidth=2.5, linestyle="--",
        label=rf"$\mathcal{{N}}(\mu={true_mu:.2f},\; \sigma/\sqrt{{n}}={true_sigma:.3f})$",
    )

apply_dark_style(
    fig=fig,
    ax=ax,
    xlabel=r"Steekproefgemiddelde $\bar{x}$",
    ylabel="Frequentie",
)

# Custom set suptitle and title
suptitle=rf"Histogram van steekproefgemiddelden"
title=(
        rf" gebaseerd op {n_samples} steekproeven van $n={sample_size}$"
        rf" uit de {dist_selector} verdeling"
    )
fig.suptitle(suptitle, fontsize=TITLE_FONT_SIZE, fontfamily=FONT_FAMILY,
                     color=PLOT_FONT_COLOR)
ax.set_title(title, fontsize=AXIS_FONT_SIZE, fontfamily=FONT_FAMILY,
                     color=PLOT_FONT_COLOR, pad=-50)


plt.tight_layout(pad=2.0)
st.pyplot(fig, width='stretch')
plt.close(fig)

# ----------------------------------
# EXPLANATION
# ----------------------------------
explanation_title = "📊 De centrale limietstelling"
explanation_markdown = r"""
## 📜 Wat is de centrale limietstelling?

De **centrale limietstelling (CLS)** zegt dat, ongeacht de oorspronkelijke verdeling van een
kansvariabele, de gemiddelden van voldoende grote steekproeven altijd een **normale verdeling**
benaderen. Wiskundig:

$$
    \overline{X} = \frac{X_1 + X_2 + \ldots + X_n}{n}
    \;\xrightarrow{n \to \infty}\;
    \mathcal{N}\!\left(\mu,\; \frac{\sigma}{\sqrt{n}}\right)
$$

## 🔢 Hoe werkt het?

1. Kies een kansverdeling (normaal, uniform, exponentieel, binomiaal of Poisson).
2. Stel de **steekproefgrootte $n$** in: hoeveel trekkingen bevat elke steekproef?
3. Stel het **aantal steekproeven** in: hoe meer steekproeven, hoe gladder het histogram.
4. Stel de distributieparameters in en bekijk hoe het histogram verandert.

## 🔍 Wat kun je observeren?

- Bij $n = 1$ herken je de originele verdeling in het histogram.
- Bij kleine $n$ kan de verdeling van de steekproefgemiddelden er nog grillig uitzien.
- Naarmate $n$ toeneemt, lijkt het histogram steeds meer op een normale verdeling — ongeacht de
  begindistributie.

## 🧠 Waarom is de CLS zo belangrijk?

De CLS rechtvaardigt het gebruik van de normale verdeling in situaties waar de onderliggende
verdeling onbekend of niet-normaal is. Zonder de CLS zouden $n$-voudige integralen nodig zijn
om de exacte kansverdeling van $\overline{X}$ te bepalen.

## 🎯 Probeer het zelf!

Experimenteer met de parameters om de CLS in actie te zien!
"""

show_explanation(explanation_title, explanation_markdown)