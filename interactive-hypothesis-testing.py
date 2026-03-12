import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm
from matplotlib.colors import to_rgb
from utils.explanation_utils import show_explanation
from dataclasses import dataclass

# ----------------------------------
# PAGE CONFIG
# ----------------------------------

st.set_page_config(
    page_title="Visualisatie van hypothesetoetsen met de normale verdeling",
    initial_sidebar_state="expanded",
    layout="wide"
)

# ----------------------------------
# CSS
# ----------------------------------
with open("./styles/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ----------------------------------
# HELPERS
# ----------------------------------

def css_to_rgba(css_color, alpha=0.4):
    r,g,b = [int(c*255) for c in to_rgb(css_color)]
    return f"rgba({r},{g},{b},{alpha})"

@dataclass
class TestRegions:
    left: float | None
    right: float | None
    beta: float

# ----------------------------------
# STATISTICS
# ----------------------------------

@st.cache_data
def generate_distributions(mu0, mu1, sigma, n, points=600):
    sample_std = sigma / np.sqrt(n)

    center = (mu0 + mu1) / 2
    spread = abs(mu1 - mu0) + 4 * sample_std

    x = np.linspace(center - spread, center + spread, points)

    pdf0 = norm.pdf(x, mu0, sample_std)
    pdf1 = norm.pdf(x, mu1, sample_std)

    return x, pdf0, pdf1, sample_std

def compute_regions(test_type, mu0, mu1, sample_std, alpha):
    if test_type == "tweezijdig":
        z = norm.ppf(1 - alpha / 2)
        left = mu0 - z * sample_std
        right = mu0 + z * sample_std
        beta = norm.cdf(right, mu1, sample_std) - norm.cdf(left, mu1, sample_std)
    elif test_type == "rechtszijdig":
        z = norm.ppf(1 - alpha)
        left = None
        right = mu0 + z * sample_std
        beta = norm.cdf(right, mu1, sample_std)
    elif test_type == "linkszijdig":
        z = norm.ppf(1 - alpha)
        left = mu0 - z * sample_std
        right = None
        beta = 1 - norm.cdf(left, mu1, sample_std)
    return TestRegions(left, right, beta)

# ----------------------------------
# PLOTTING HELPERS
# ----------------------------------

def add_curve(fig, x, y, color, name, showlegend=True):
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="lines",
            line=dict(color=color),
            name=name,
            showlegend=showlegend
        )
    )

def add_shaded_region(fig, x, y, mask, color, name, showlegend=True):
    fig.add_trace(
        go.Scatter(
            x=x[mask],
            y=y[mask],
            fill="tozeroy",
            fillcolor=css_to_rgba(color, 0.25),
            line=dict(color="rgba(0,0,0,0)"),
            name=name,
            showlegend=showlegend
        )
    )

def add_region_bar(fig, x0, x1, y, color):
    fig.add_trace(
        go.Scatter(
            x=[x0, x1],
            y=[y, y],
            mode="lines",
            line=dict(color=color, width=10),
            showlegend=False
        )
    )

def add_text(fig, text, x, y, color):
    fig.add_annotation(
        x=x,
        y=y,
        text=text,
        showarrow=False,
        font=dict(size=25, color=color)
    )


# ----------------------------------
# PARAMETERS
# ----------------------------------

st.title("📊 Hypothesetoetsen voor het gemiddelde $\\mu$ van een normale verdeling")
with st.sidebar:
    st.header("Parameters")
    test_type = st.selectbox(
        label="Toetstype:",
        options=["tweezijdig", "linkszijdig", "rechtszijdig"]
    )

    mu0 = st.number_input(label="Gemiddelde $\\mu_0$ (nulhypothese):", value=0.0)
    sigma = st.number_input(label="Standaardafwijking ($\\sigma$):", min_value=1e-6, value=1.0)
    n = st.number_input(label="Steekproefgrootte ($n$):", min_value=1, value=30)
    alpha = st.number_input(label="Significantieniveau ($\\alpha$):", min_value=0.001, max_value=0.2, value=0.05)
    mu1 = st.slider("Gemiddelde $\\mu_1$ (alternatieve hypothese)", min_value=mu0 - 1, max_value=mu0 + 1)

# -------------------------------
# COMPUTATION
# -------------------------------

x, pdf0, pdf1, sample_std = generate_distributions(mu0, mu1, sigma, n)
regions = compute_regions(test_type, mu0, mu1, sample_std, alpha)
beta = regions.beta
power = 1 - beta

# -------------------------------
# STAT CARDS
# -------------------------------
 
st.markdown(f"""
<div class="stats-row" >
  <div class="stat-card alpha">
    <span class="stat-label">Type-I fout</span>
    <span class="stat-value">&alpha; = {alpha:.3f}</span>
    <span class="stat-desc">Kans op onterecht verwerpen van H₀</span>
    <span class="stat-desc">(rood gearceerd gebied)</span>
  </div>
  <div class="stat-card beta">
    <span class="stat-label">Type-II fout</span>
    <span class="stat-value">&beta; = {beta:.3f}</span>
    <span class="stat-desc">Kans op onterecht accepteren van H₀</span>
    <span class="stat-desc">(lichtblauw gearceerd gebied)</span>
  </div>
</div>
""", unsafe_allow_html=True)

# -------------------------------
# PLOTTING
# -------------------------------

H0_COLOR = "gold"
H1_COLOR = "magenta"
ACCEPTABLE_COLOR = "springgreen"
CRITICAL_COLOR = "tomato"
ALPHA_COLOR = CRITICAL_COLOR
BETA_COLOR = "cyan"

fig = go.Figure()

add_curve(fig, x, pdf0, H0_COLOR, r"Verdeling onder H<sub>0</sub>")
add_curve(fig, x, pdf1, H1_COLOR, r"Verdeling onder H<sub>1</sub>")

# mean lines

ymax = max(pdf0)

fig.add_trace(go.Scatter(
    x=[mu0, mu0],
    y=[0, ymax],
    mode="lines",
    line=dict(dash="dash", color=H0_COLOR),
    name="μ₀",
    showlegend=False
))

fig.add_trace(go.Scatter(
    x=[mu1, mu1],
    y=[0, ymax],
    mode="lines",
    line=dict(dash="dash", color=H1_COLOR),
    name="μ₁",
    showlegend=False
))

xmin, xmax = x[0], x[-1]
yline = -0.1 * ymax

# --------------------------------------------------
# SHADED REGIONS
# --------------------------------------------------

if test_type == "tweezijdig":

    left = regions.left
    right = regions.right

    mask_left = x < left
    mask_right = x > right
    mask_accept = (x >= left) & (x <= right)

    add_shaded_region(fig, x, pdf0, mask_left, ALPHA_COLOR, f"Type-I fout (&#945;={alpha:.3f})", False)
    add_shaded_region(fig, x, pdf0, mask_right, ALPHA_COLOR, "", False)

    add_shaded_region(fig, x, pdf1, mask_accept, BETA_COLOR, f"Type-II fout (&#946;={beta:.3f})", False)

    add_region_bar(fig, xmin, left, yline, CRITICAL_COLOR)
    add_region_bar(fig, left, right, yline, ACCEPTABLE_COLOR)
    add_region_bar(fig, right, xmax, yline, CRITICAL_COLOR)

    add_text(fig, "Kritiek gebied", (xmin + left) / 2, 1.5 * yline, CRITICAL_COLOR)
    add_text(fig, "Acceptatiegebied", (left + right) / 2, 1.5 * yline, ACCEPTABLE_COLOR)
    add_text(fig, "Kritiek gebied", (right + xmax) / 2, 1.5 * yline, CRITICAL_COLOR)


elif test_type == "rechtszijdig":

    right = regions.right

    mask_crit = x > right
    mask_accept = x <= right

    add_shaded_region(fig, x, pdf0, mask_crit, ALPHA_COLOR, f"Type-I fout (&#945;={alpha:.3f})", False)
    add_shaded_region(fig, x, pdf1, mask_accept, BETA_COLOR, f"Type-II fout (&#946;={beta:.3f})", False)

    add_region_bar(fig, xmin, right, yline, ACCEPTABLE_COLOR)
    add_region_bar(fig, right, xmax, yline, CRITICAL_COLOR)

    add_text(fig, "Acceptatiegebied", (xmin + right) / 2, 1.5 * yline, ACCEPTABLE_COLOR)
    add_text(fig, "Kritiek gebied", (right + xmax) / 2, 1.5 * yline, CRITICAL_COLOR)


else:  # linkszijdig

    left = regions.left

    mask_crit = x < left
    mask_accept = x >= left

    add_shaded_region(fig, x, pdf0, mask_crit, ALPHA_COLOR, f"Type-I fout (&#945;={alpha:.3f})", False)
    add_shaded_region(fig, x, pdf1, mask_accept, BETA_COLOR, f"Type-II fout (&#946;={beta:.3f})", False)

    add_region_bar(fig, xmin, left, yline, CRITICAL_COLOR)
    add_region_bar(fig, left, xmax, yline, ACCEPTABLE_COLOR)

    add_text(fig, "Kritiek gebied", (xmin + left) / 2, 1.5 * yline, CRITICAL_COLOR)
    add_text(fig, "Acceptatiegebied", (left + xmax) / 2, 1.5 * yline, ACCEPTABLE_COLOR)

# --------------------------------------------------
# LAYOUT
# --------------------------------------------------
if test_type == "tweezijdig":
    title_text = f"Tweezijdige toets (H<sub>0</sub>: &mu; = {mu0} versus H<sub>1</sub>: &mu; &#8800; {mu0})"
elif test_type == "linkszijdig":
    title_text = f"Linkszijdige toets (H<sub>0</sub>: &mu; &#8805; {mu0} versus H<sub>1</sub>: &mu; < {mu0})"
elif test_type == "rechtszijdig":
    title_text = f"Rechtszijdige toets (H<sub>0</sub>: &mu; &#8804; {mu0} versus H<sub>1</sub>: &mu; > {mu0})"
fig.update_layout(

    title=dict(
        text=title_text,
        font=dict(size=35),
    ),

    xaxis=dict(
        title=dict(text="x", font=dict(size=25)),
        tickfont=dict(size=25)
    ),

    yaxis=dict(
        title=dict(text="Kansdichtheidsfunctie", font=dict(size=25)),
        tickfont=dict(size=25)
    ),

    legend=dict(font=dict(size=30), xanchor="right", yanchor="top"),

    height=750
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config=dict(displayModeBar=False)
)

explanation_title = "📚 Uitleg: hypothesetoetsen"
explanation_md=r"""
# 📊 Interactieve Streamlit Webapp: Hypothesetoetsing

Deze interactieve webapp toont de werking van **hypothesetoetsen voor het populatiegemiddelde** $\mu$, inclusief visualisatie van:

-  Type-I fout ($\alpha$): gegeven dat $H_0$ waar is, de kans dat $H_0$ toch wordt verworpen (vals negatief)
-  Type-II fout ($\beta$): gegeven dat $H_0$ niet waar is, de kans dat $H_0$ toch wordt geaccepteerd (vals positief)
-  Onderscheidend vermogen van een toets ($1 - \beta$): gegeven dat $H_0$ niet waar is, de kans dat daadwerkelijk $H_0$ ook wordt verworpen (true negative) 
-  Acceptatie- en kritieke gebieden (respectievelijk groene en rode intervals onder de grafiek)

## ⚙️ Functionaliteiten

Met de webapp kun je onderstaande parameters instellen via een **sidebar**:

-  **Toetstype:** tweezijdig, linkszijdig of rechtszijdig (dit geeft het teken "≠", "$<$" of "$>$" aan in de alternatieve hypothese).
-  **Nulhypothese-gemiddelde** $\mu_0$
-  **Alternatieve hypothese** $\mu_1$
-  **Standaardafwijking** $\sigma$
-  **Significantieniveau** $\alpha$
-  **Steekproefgrootte** $n$

## 🧠 Uitleg: hypothesetoetsing

### 📌 Wat laat de grafiek zien?

- De **cyaanblauwe kromme** is de kansverdeling onder $H_0$, d.w.z. $\bar{X} \sim N(\mu_0, \frac{\sigma}{\sqrt{n}})$.
- De **goudgele kromme** stelt de kansverdeling onder de alternatieve hypothese $H_1$ voor (voor een gegeven $\mu_1 \neq \mu_0$).
- Het **lichtgroene interval** onder de grafiek toont het **acceptatiegebied**.
- Het **rode interval** (links- en rechtszijdige toetsen) vormt of de **rode intervallen** (tweezijdige toets) vormen het **kritieke gebied**.
- Het **rood gearceerde oppervlak** geeft de kans op een **type-I fout** ($\alpha$) weer.
- Het **lichtpaars gearceerde oppervlak** geeft de kans op een **type-II fout** ($\beta$) weer.

### 🧮 Invloeden op het onderscheidend vermogen

- Hoe kleiner de afstand tussen $\mu_0$ en $\mu_1$, hoe kleiner het onderscheidend vermogen $1 - \beta$
- Hoe groter de standaardafwijking $\sigma$, hoe kleiner het onderscheidend vermogen $1 - \beta$
- Hoe groter de steekproefgrootte $n$, hoe groter het onderscheidend vermogen $1 - \beta$
- Hoe groter het significantieniveau $\alpha$, hoe groter het onderscheidend vermogen $1 - \beta$ (oftewel hoe kleiner de kans op een type-II fout ($\beta$))
"""

# Call show_explanation with the plot_hypothesis_testing function
show_explanation(explanation_title, explanation_md)


