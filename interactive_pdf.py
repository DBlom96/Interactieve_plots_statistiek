import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy.stats import norm, uniform, chi2, f
from scipy.integrate import quad

from utils.explanation_utils import show_explanation
from utils.streamlit_utils import load_css, page_header, apply_dark_style
from utils.constants import *

st.set_page_config(
    page_title="Van Discreet naar Continu: De Kansdichtheidsfunctie",
    initial_sidebar_state="expanded",
    layout="wide"
)

# ----------------------------------
# CSS
# ----------------------------------
load_css()

# ----------------------------------
# PARAMETERS
# ----------------------------------
page_header("📉 Verschil: discrete en continue kansvariabelen", "Statistiek · Kansdichtheid (PDF)")

with st.sidebar:
    st.header("Parameters")

    dist_type = st.selectbox(
        "Type verdeling:", 
        ["Normale verdeling", "Uniforme verdeling", "Chikwadraatverdeling", "F-verdeling", "Eigen functie (Custom)"]
    )
    
    # Dynamische parameters per verdeling
    if dist_type == "Normale verdeling":
        mu_val = st.number_input("Gemiddelde ($\mu$):", value=0.0, step=0.5)
        sigma_val = st.number_input("Standaardafwijking ($\sigma$):", min_value=0.1, value=1.0, step=0.1)
        domain_min, domain_max = mu_val - 4 * sigma_val, mu_val + 4 * sigma_val
    elif dist_type == "Uniforme verdeling":
        a_unif = st.number_input("Ondergrens ($a$):", value=0.0, step=0.5)
        b_unif = st.number_input("Bovengrens ($b$):", min_value=a_unif + 0.1, value=5.0, step=0.5)
        domain_min, domain_max = a_unif - 1.0, b_unif + 1.0
    elif dist_type == "Chi-kwadraatverdeling":
        df_chi = st.number_input("Vrijheidsgraden ($df$):", min_value=1, value=4, step=1)
        domain_min, domain_max = 0.0, float(df_chi + 4 * np.sqrt(2 * df_chi))
    elif dist_type == "F-verdeling":
        df1 = st.number_input("Vrijheidsgraden teller ($df_1$):", min_value=1, value=5, step=1)
        df2 = st.number_input("Vrijheidsgraden noemer ($df_2$):", min_value=1, value=10, step=1)
        domain_min, domain_max = 0.0, 5.0
    elif dist_type == "Eigen functie (Custom)":
        st.markdown("Vul een Python-expressie in voor $f(x)$ (gebruik `x` als variabele).")
        custom_expr = st.text_input("Formule $f(x)$:", value="np.maximum(0, 1 - np.abs(x))")
        domain_min = st.number_input("Domein ondergrens:", value=-1.0)
        domain_max = st.number_input("Domein bovengrens:", value=1.0)
    
    n_points = st.number_input("Aantal meetwaarden (steekproefgrootte $n$):", min_value=1, value=1_000)
    n_bins = st.number_input("Aantal bins in histogram:", min_value=1, value=int(np.sqrt(n_points)))
    
    st.markdown("---")
    st.subheader("Weergave & Interval")
    toggle_pdf = st.checkbox("Toon kansdichtheidsfunctie (PDF)", value=True)
    show_interval = st.checkbox("Toon kans als oppervlakte $P(a \\le X \\le b)$", value=True)
    
    default_a = max(domain_min, -2.0)
    default_b = min(domain_max, 2.0)
    
    a_val = st.number_input("Ondergrens $a$:", value=float(default_a), step=0.1)
    b_val = st.number_input("Bovengrens $b$:", value=float(default_b), step=0.1)
    
    if a_val > b_val:
        st.error("Let op: Ondergrens $a$ moet kleiner dan of gelijk zijn aan bovengrens $b$.")

# ----------------------------------
# DATA & FUNCTION EVALUATION
# ----------------------------------
np.random.seed(42)

if dist_type == "Normale verdeling":
    data = norm.rvs(loc=mu_val, scale=sigma_val, size=n_points)
    min_val, max_val = data.min() - 0.5, data.max() + 0.5
    x_curve = np.linspace(domain_min, domain_max, 300)
    bin_edges = np.linspace(min_val, max_val, n_bins + 1)
    bin_width = bin_edges[1] - bin_edges[0]
    curve_y = norm.pdf(x_curve, loc=mu_val, scale=sigma_val) # Echte dichtheid op rechteras
    def get_prob(a, b): return (norm.cdf(b, loc=mu_val, scale=sigma_val) - norm.cdf(a, loc=mu_val, scale=sigma_val))

elif dist_type == "Uniforme verdeling":
    data = uniform.rvs(loc=a_unif, scale=b_unif - a_unif, size=n_points)
    min_val, max_val = a_unif - 0.2, b_unif + 0.2
    x_curve = np.linspace(domain_min, domain_max, 300)
    bin_edges = np.linspace(min_val, max_val, n_bins + 1)
    bin_width = bin_edges[1] - bin_edges[0]
    curve_y = uniform.pdf(x_curve, loc=a_unif, scale=b_unif - a_unif)
    def get_prob(a, b): return (uniform.cdf(b, loc=a_unif, scale=b_unif - a_unif) - uniform.cdf(a, loc=a_unif, scale=b_unif - a_unif))

elif dist_type == "Chi-kwadraatverdeling":
    data = chi2.rvs(df=df_chi, size=n_points)
    min_val, max_val = 0.0, data.max() + 1.0
    x_curve = np.linspace(max(0.001, domain_min), domain_max, 300)
    bin_edges = np.linspace(min_val, max_val, n_bins + 1)
    bin_width = bin_edges[1] - bin_edges[0]
    curve_y = chi2.pdf(x_curve, df=df_chi)
    def get_prob(a, b): return (chi2.cdf(max(0, b), df=df_chi) - chi2.cdf(max(0, a), df=df_chi))

elif dist_type == "F-verdeling":
    data = f.rvs(df1=df1, df2=df2, size=n_points)
    min_val, max_val = 0.0, data.max() + 1.0
    x_curve = np.linspace(max(0.001, domain_min), domain_max, 300)
    bin_edges = np.linspace(min_val, max_val, n_bins + 1)
    bin_width = bin_edges[1] - bin_edges[0]
    curve_y = f.pdf(x_curve, df1=df1, df2=df2)
    def get_prob(a, b): return (f.cdf(max(0, b), df1=df1, df2=df2) - f.cdf(max(0, a), df1=df1, df2=df2))

else:  # Custom
    try:
        x_dummy = np.linspace(domain_min, domain_max, 500)
        y_dummy = eval(custom_expr, {"np": np, "x": x_dummy})
        y_dummy = np.maximum(0, y_dummy)
        
        integral_val, _ = quad(lambda val: max(0, eval(custom_expr, {"np": np, "x": val})), domain_min, domain_max)
        normalization_factor = integral_val if integral_val > 0 else 1.0

        probs = y_dummy / np.sum(y_dummy) if np.sum(y_dummy) > 0 else np.ones_like(y_dummy)/len(y_dummy)
        data = np.random.choice(x_dummy, size=n_points, p=probs)
        
        min_val, max_val = domain_min, domain_max
        x_curve = np.linspace(min_val, max_val, 300)
        bin_edges = np.linspace(min_val, max_val, n_bins + 1)
        bin_width = bin_edges[1] - bin_edges[0]
        
        curve_y = np.maximum(0, eval(custom_expr, {"np": np, "x": x_curve})) / normalization_factor
        
        def get_prob(a, b):
            clipped_a = max(domain_min, a)
            clipped_b = min(domain_max, b)
            if clipped_a >= clipped_b:
                return 0.0
            val, _ = quad(lambda v: max(0, eval(custom_expr, {"np": np, "x": v})) / normalization_factor, clipped_a, clipped_b)
            return val

    except Exception as e:
        st.error(f"Fout in de ingevoerde formule: {e}")
        data = np.zeros(n_points)
        x_curve = np.linspace(-1, 1, 300)
        bin_edges = np.linspace(-1, 1, n_bins + 1)
        bin_width = bin_edges[1] - bin_edges[0]
        curve_y = np.zeros(300)
        min_val, max_val = -1, 1
        def get_prob(a, b): return 0.0

# ----------------------------------
# COMPUTATIONS HISTOGRAM
# ----------------------------------
prob_interval = get_prob(a_val, b_val) if a_val <= b_val else 0.0

# ----------------------------------
# STAT CARDS
# ----------------------------------

kans_interval = f"$P({a_val:.2f} \\leq X \\leq {b_val:.2f})$"
st.markdown(f"""
<div class="stats-row-2">
  <div class="stat-card alpha">
    <span class="stat-label"><i>P</i>(<i>X=x</i><sub>0</sub>):</span>
    <span class="stat-value">0.0000</span>
    <span class="stat-desc">Elke losse uitkomst heeft een oneindig kleine waarschijnlijkheid bij een continue variabele.</span>
  </div>
  <div class="stat-card beta">
    <span class="stat-label"><i>P</i>({a_val:.2f}&le;<i>X</i>&le;{b_val:.2f})</span>
    <span class="stat-value">{prob_interval:.4f}</span>
    <span class="stat-desc">Groene oppervlakte onder de kansdichtheidsfunctie (de integraal).</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------
# FIGURE (Dubbele as: Links = Frequentie, Rechts = Dichtheid)
# ----------------------------------
fig, ax1 = plt.subplots(figsize=(10, 5))

# Linker as: Histogram (Frequentie)
counts, edges = np.histogram(data, bins=bin_edges)
ax1.bar(
    (edges[:-1] + edges[1:]) / 2,
    counts,
    width=bin_width * 0.92,
    color=HISTOGRAM_BAR_COLOR,
    alpha=0.6,
    label=f"Histogram (Frequentie, $n={n_points}$)",
)
ax1.set_ylabel("Frequentie", color=PLOT_FONT_COLOR)
ax1.tick_params(axis='y', labelcolor=PLOT_FONT_COLOR)

# Rechter as: Kansdichtheidsfunctie (PDF)
ax2 = ax1.twinx()
if toggle_pdf:
    ax2.plot(
        x_curve, curve_y,
        color=H0_COLOR, linewidth=2.5, linestyle="-",
        label=r"Kansdichtheidsfunctie $f(x)$ (Dichtheid)",
    )

    # Highlight interval op de rechter as / PDF
    if show_interval and (a_val <= b_val):
        ix = np.where((x_curve >= a_val) & (x_curve <= b_val))
        if len(ix[0]) > 0:
            ax2.fill_between(
                x_curve[ix], 0, curve_y[ix],
                color="#3bf63b", alpha=0.4,
                label=f"Oppervlakte = Kans tussen {a_val} en {b_val}"
            )

ax2.set_ylabel("Kansdichtheid $f(x)$ = $\\frac{{Frequentie}}{{binbreedte}}$", color=PLOT_FONT_COLOR)
ax2.set_ylim(bottom=0.0)
ax2.tick_params(axis='y', labelcolor=PLOT_FONT_COLOR)
ax2.grid(False) # Voorkom dubbele roosterlijnen

apply_dark_style(
    fig=fig,
    ax=ax1,
    xlabel=r"Continue kansvariabele $X$",
    ylabel="",
)

suptitle = f"Van histogram (frequenties) naar een kansdichtheidsfunctie ({dist_type})"
title = f"Kans op waarde tussen {a_val} en {b_val}: {get_prob(a_val,b_val):.4f} | Huidige binbreedte: {bin_width:.2f}"
fig.suptitle(suptitle, fontsize=TITLE_FONT_SIZE, fontfamily=FONT_FAMILY, color=PLOT_FONT_COLOR)
ax1.set_title(title, fontsize=AXIS_FONT_SIZE, fontfamily=FONT_FAMILY, color=PLOT_FONT_COLOR, pad=-30)

# Combineer legenda's van beide assen
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
# ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper right", frameon=True)

plt.tight_layout(pad=2.0)
st.pyplot(fig, use_container_width=False)
plt.close(fig)

# ----------------------------------
# EXPLANATION
# ----------------------------------
explanation_title = "📉 Achtergrond: waarom $P(X=x)=0$ niet hetzelfde is als 'onmogelijk'?"
explanation_markdown = r"""
## 🧠 Het intuïtie-probleem

Wanneer we fysieke grootheden meten, werken we met **continue variabelen**. 
Als je meet op oneindig veel decimalen, is de kans dat iemand *exact* een specifieke waarde aanneemt gelijk aan **nul**. 

## 📐 Van frequenties naar dichtheden
We kunnen een kansdichtheidsfunctie bekijken door eerst een grote steekproef uit de kansverdeling te nemen, en daarvan een histogram te maken.

1. **Linkeras (frequentie):** dit laat het *absolute aantal* waarnemingen in de steekproef zien per bin (histogram). Dit hangt af van je steekproefgrootte $n$.
2. **Rechteras (dichtheid):** Dit is de theoretische kansdichtheid. De waarde op deze as is *geen* kans, maar een dichtheid (waardes kunnen groter dan 1 zijn). 
3. **De koppeling tussen beide assen:** door beide assen te combineren zie je direct dat het histogram (geteld in aantal) bij een grote steekproef nadert aan de theoretische dichtheid (frequentie per eenheid van binbreedte).

## 🧮 Kansen uitrekenen met behulp van een integraal

Omdat de kans op elk *los* punt nul is, berekenen we kansen altijd over een *interval* $[a, b]$. 
De kans is exact de **oppervlakte** onder de kromme op dat interval:
$$P(a \le X \le b) = \int_{a}^{b} f(x) \, dx$$
"""

show_explanation(explanation_title, explanation_markdown)