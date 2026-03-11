import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from scipy.stats import norm
from utils.streamlit_utils import generate_streamlit_page
from utils.plot_style import cyberpunk_color_cycle

# Paginalay-out instellen op breed
st.set_page_config(layout="wide")

# Title and explanation
# st.markdown("### Interactieve plot: type-I en type-II fouten")
# st.write("""
# Deze interactieve plot laat zien wat de type-I en type-II fouten zijn voor een hypothesetoets voor het populatiegemiddelde $\\mu$ met de drie toetstypes: tweezijdig, linkszijdig en rechtszijdig.
# Allereerst is de kansverdeling voor de toetsingsgrootheid $\\bar{X}$ onder de nulhypothese $\\bar{{X}} \sim N(\\mu_0; \\frac{{\sigma}}{{\sqrt{{n}}}}$ getekend in cyaanblauw.
# Gegeven de keuze voor het significantieniveau $\\alpha$, wordt het **acceptatiegebied** bepaald met behulp van het $(1-\\alpha)$-voorspellingsinterval voor $\\bar{{x}}$ gegeven $\\mu=\\mu_0$ en $\\alpha$.
# Dit acceptatiegebied wordt gegeven door de lichtgroene horizontale lijn onder de grafiek.
# De overige mogelijke waardes voor $\\bar{{x}}$ geven het **kritieke gebied** aan en zijn weergegeven met de rode horizontale lijnen onder de grafiek.

# De type-I fout is de fout die we maken als $H_0$ in werkelijkheid waar is, maar we kiezen om $H_0$ te verwerpen. 
# Dit gebeurt als de waargenomen toetsingsgrootheid $\\bar{{x}}$ uit een van de staarten van de cyaanblauwe verdeling komt (een extreme waarde).
# Merk op dat we de grootte van deze fout kiezen met onze keuze voor het significantieniveau $\\alpha$.
         
# Het doel van een hypothesetoets zit hem in het beperken van de type-II fout: de fout die we maken wanneer de alternatieve hypothese $\\bar{{X}} \sim N(\\mu_1; \\frac{{\sigma}}{{\sqrt{{n}}}})$ in werkelijkheid waar is, maar we toch besluiten om $H_0$ te accepteren.
# Deze fout $\\beta$ wordt in de plot weergegeven door het gearceerde gebied onder de verdeling van de alternatieve hypothese (goudgele verdeling).
# De **kracht** of het **onderscheidingsvermogen** is de kans $1 - \\beta$, oftewel de kans dat als $H_1$ in werkelijkheid waar is we inderdaad de nulhypothese $H_0$ verwerpen.
                 
# Merk het volgende op:
# - De type-I fout is gekozen met de keuze van $\\alpha$.
# - De volgende zaken hebben invloed op de type-II fout:
#     - als $\\mu_0$ en $\\mu_1$ dichter bij elkaar liggen, wordt de type-II fout groter $\\beta$ ($H_0$ en $H_1$ moeilijker te onderscheiden!).
#     - als de standaardafwijking $\\sigma$ groter wordt, wordt de type-II fout $\\beta$ ook groter.
#     - als de steekproefgrootte $n$ groter wordt, wordt de type-II fout $\\beta$ kleiner.
#     - als het significantieniveau $\\alpha$ (en daarmee dus de type-I fout) groter gekozen wordt, dan wordt de type-II fout $\\beta$ kleiner."""
# )

def add_sidebar_hypothesis_testing():
    with st.sidebar:
        st.header("Sliders voor parameters")

        # Streamlit widgets for user input
        test_type = st.selectbox("Toetstype", ['tweezijdig', 'linkszijdig', 'rechtszijdig'])
        mu_0 = st.number_input("Gemiddelde $\\mu_0$ onder $H_0$:", value=0.0)
        sigma = st.number_input("Standaardafwijking ($\\sigma$)", min_value=0.0, value=1.0)

        if test_type == "tweezijdig":
            minmu, maxmu = mu_0 - sigma, mu_0 + sigma
        elif test_type == "rechtszijdig":
            minmu, maxmu = mu_0, mu_0 + sigma
        else:
            minmu, maxmu = mu_0 - sigma, mu_0
        mu_1 = st.number_input("Gemiddelde $\\mu_1$ onder $H_1$", value=mu_0+1) # min_value=minmu, max_value=maxmu, value=mu_0+1 if test_type == "tweezijdig" else value, step=1)
        alpha = st.number_input("Significantieniveau ($\\alpha$)", min_value=0.001, max_value=0.2, value=0.05)
        sample_size = st.number_input("Steekproefgrootte ($n$):", min_value=1, value=30)

        slider_dict = {
            "test_type": test_type, 
            "mu_0": mu_0,
            "mu_1": mu_1,
            "sigma": sigma,
            "alpha": alpha,
            "sample_size": sample_size
        }
    return slider_dict

# Function to plot confidence intervals
def plot_hypothesis_testing(axes, user_inputs):
    test_type, mu_0, mu_1, sigma, alpha, sample_size = user_inputs.values()
    color_cycle = cyberpunk_color_cycle()
    sample_std = sigma / np.sqrt(sample_size)

    maxmu = max(mu_0, mu_1)
    minmu = min(mu_0, mu_1)
    x = np.linspace(minmu - 4 * sample_std, maxmu + 4 * sample_std, 1_000)

    opacity = 0.2
    acceptable_color = color_cycle[1] # "neongreen"
    critical_color = color_cycle[6] # "tomato red"

    H0_color = color_cycle[2] # "cyan"
    H1_color = color_cycle[7] # "gold"
    
    # Kansdichtheidsfuncties onder H0 en H1
    pdf_H0 = norm.pdf(x, mu_0, sample_std)
    pdf_H1 = norm.pdf(x, mu_1, sample_std)

    # Draw horizontal lines indicating the regions
    xmin, xmax = x[0], x[-1]
    ymax = max(pdf_H0)
    ytext = -0.2 * ymax  # Position for the horizontal line 
    ymu = 1/4 * ytext
    ylines = 1/2 * ytext

    axes[0].set_ylim(bottom=1.5*ytext, top=1.1*ymax)
    axes[0].set_xlabel('Toetsingsgrootheid ($\\overline{x}$)')
    axes[0].set_ylabel('Kansdichtheidsfunctie $f(\\overline{x})$')
    
    # Plot instellen
    axes[0].plot(x, pdf_H0, color=H0_color, alpha=0.7, label="Kansverdeling van $\\overline{X}$ onder $H_0$")
    axes[0].plot([mu_0, mu_0], [0, norm.pdf(mu_0, mu_0, sample_std)], color=H0_color, linestyle='--')
    axes[0].text(mu_0, ymu, "$\\mu_0$", color=H0_color, ha="center", va="center")

    axes[0].plot(x, pdf_H1, color=H1_color, alpha=0.7, label="Kansverdeling van $\\overline{X}$ onder $H_1$")
    axes[0].plot([mu_1, mu_1], [0, norm.pdf(mu_1, mu_1, sample_std)], color=H1_color, linestyle='--')
    axes[0].text(mu_1, ymu, "$\\mu_1$", color=H1_color, ha="center", va="center")
    
    

    if test_type == "tweezijdig":
        # Kritieke waarde onder H0 (voor tweezijdige toets)
        z_alpha = norm.ppf(1 - alpha / 2)
        critical_value_left = mu_0 - z_alpha * sample_std
        critical_value_right = mu_0 + z_alpha * sample_std
        axes[0].fill_between(x, 0, pdf_H0, where=((x < critical_value_left) | (x > critical_value_right)), color=critical_color, alpha=opacity, label=f'Type I fout ($\\alpha$): {alpha:.3f}')
        
        # Bereken de type II fout en arceer de bijbehorende oppervlakte
        beta = norm.cdf(critical_value_right, loc=mu_1, scale=sample_std) - norm.cdf(critical_value_left, loc=mu_1, scale=sample_std)
        axes[0].fill_between(x, 0, pdf_H1, where=((x < critical_value_right) & (x > critical_value_left)), color=H1_color, alpha=opacity, label=f'Type II fout ($\\beta$): {beta:.3f}')
        
        # Teken de grenzen van het kritieke gebied
        axes[0].plot([critical_value_left, critical_value_left], [0, norm.pdf(critical_value_left, mu_0, sample_std)], color=critical_color, linestyle='-')#, label='Kritieke grens links')
        axes[0].plot([critical_value_right, critical_value_right], [0, norm.pdf(critical_value_right, mu_0, sample_std)], color=critical_color, linestyle='-')#, label='Kritieke grens rechts')

        # Teken het acceptatiegebied
        axes[0].hlines(ylines, critical_value_left, critical_value_right, color=acceptable_color, linewidth=5)
        axes[0].text((critical_value_left + critical_value_right) / 2, ytext, 'Accepteer $H_0$', color=acceptable_color, fontsize=11, ha='center')

        # Teken het kritieke gebied
        axes[0].hlines(ylines, xmin, critical_value_left, color=critical_color, linewidth=5, label=f"Kritiek gebied: $(-\\infty; {critical_value_left:.2f}]$ en $[{critical_value_right:.2f}; \\infty)$")
        axes[0].hlines(ylines, critical_value_right, xmax, color=critical_color, linewidth=5)
        axes[0].text((critical_value_left + xmin) / 2, ytext, 'Verwerp $H_0$', color=critical_color, fontsize=11, ha='center')
        axes[0].text((critical_value_right + xmax) / 2, ytext, 'Verwerp $H_0$', color=critical_color, fontsize=11, ha='center')
        
        plt.suptitle(f'Tweezijdige hypothesetoets: $H_0$: $\\mu={mu_0}$ vs. $H_1$: $\\mu \\neq {mu_0}$')
        
    elif test_type == "rechtszijdig":
        z_alpha = norm.ppf(1 - alpha)
        critical_value_right = mu_0 + z_alpha * sample_std
        axes[0].fill_between(x, 0, pdf_H0, where=(x > critical_value_right), color=critical_color, alpha=opacity, label=f'Type I fout ($\\alpha$): {alpha:.3f}')

        # Bereken de type II fout en arceer de bijbehorende oppervlakte
        beta = norm.cdf(critical_value_right, loc=mu_1, scale=sample_std)
        axes[0].fill_between(x, 0, pdf_H1, where=(x < critical_value_right), color=H1_color, alpha=opacity, label=f'Type II fout ($\\beta$): {beta:.3f}')

        # Teken de grens van het kritieke gebied
        axes[0].plot([critical_value_right, critical_value_right], [0, norm.pdf(critical_value_right, mu_0, sample_std)], color=critical_color, linestyle='-')#, label='Kritieke grens rechts')

        # Teken het acceptatiegebied
        axes[0].hlines(ylines, xmin, critical_value_right, color=acceptable_color, linewidth=5)
        axes[0].text((xmin + critical_value_right) / 2, ytext, 'Accepteer $H_0$', color=acceptable_color, fontsize=11, ha='center')

        # Teken het kritieke gebied
        axes[0].hlines(ylines, critical_value_right, xmax, color=critical_color, linewidth=5, label=f"Kritiek gebied: $[{critical_value_right:.2f}; \\infty)$")
        axes[0].text((critical_value_right + xmax) / 2, ytext, 'Verwerp $H_0$', color=critical_color, fontsize=11, ha='center')
               
        plt.suptitle(f'Rechtszijdige hypothesetoets: $H_0$: $\\mu\\leq{mu_0}$ vs. $H_1$: $\\mu > {mu_0}$')
        
    else: # linkszijdig
        z_alpha = norm.ppf(alpha)
        critical_value_left = mu_0 + z_alpha * sample_std
        axes[0].fill_between(x, 0, pdf_H0, where=(x < critical_value_left), color=critical_color, alpha=opacity, label=f'Type I fout ($\\alpha$): {alpha:.3f}')
        
        # Bereken de type II fout en arceer de bijbehorende oppervlakte
        beta = norm.cdf(critical_value_left, loc=mu_1, scale=sample_std)
        axes[0].fill_between(x, 0, pdf_H1, where=(x > critical_value_left), color=H1_color, alpha=opacity, label=f'Type II fout ($\\beta$): {beta:.3f}')

        # Teken de grens van het kritieke gebied
        axes[0].plot([critical_value_left, critical_value_left], [0, norm.pdf(critical_value_left, mu_0, sample_std)], color=critical_color, linestyle='-')#, label='Kritieke grens rechts')

        # Teken het acceptatiegebied
        axes[0].hlines(ylines, critical_value_left, xmax, color=acceptable_color, linewidth=5)
        axes[0].text((critical_value_left + xmax) / 2, ytext, 'Accepteer $H_0$', color=acceptable_color, fontsize=11, ha='center')

        # Teken het kritieke gebied
        axes[0].hlines(ylines, xmin, critical_value_left, color=critical_color, linewidth=5, label=f"Kritiek gebied: $(-\\infty; {critical_value_left:.2f}]$")
        axes[0].text((xmin + critical_value_left) / 2, ytext, 'Verwerp $H_0$', color=critical_color, fontsize=11, ha='center')
        
        plt.suptitle(f'Linkszijdige hypothesetoets: $H_0$: $\\mu\\geq{mu_0}$ vs. $H_1$: $\\mu < {mu_0}$')

    axes[0].legend(loc='center left', bbox_to_anchor=(1, 0.5), ncol=1)
slider_dict = add_sidebar_hypothesis_testing()

page_header="Interactieve plot: hypothesetoetsen"
plot_title=f"Hypothesetoets voor het gemiddelde $\\mu$"
xlabel="Steekproefgemiddelde $\\overline{x}$", 
ylabel="Kansdichtheidsfunctie $f(k)$"
explanation_title = "# :book: Uitleg: hypothesetoetsen"
explanation_md=r"""
# 📊 Interactieve Streamlit Webapp: Hypothesetoetsing

Deze interactieve webapp toont de werking van **hypothesetoetsen voor het populatiegemiddelde** $\mu$, inclusief visualisatie van:

-  Type-I fout ($\alpha$)
-  Type-II fout ($\beta$)
-  Acceptatie- en kritieke gebieden

## ⚙️ Functionaliteiten

Met de webapp kun je onderstaande parameters instellen via een **sidebar**:

-  **Toetstype:** tweezijdig, linkszijdig of rechtszijdig (dit geeft het teken "\neq", "<" of ">" aan in de alternatieve hypothese).
-  **Nulhypothese-gemiddelde** $\mu_0$
-  **Alternatieve hypothese** $\mu_1$
-  **Standaardafwijking** $\sigma$
-  **Significantieniveau** $\alpha$
-  **Steekproefgrootte** $n$

## 🧠 Uitleg: hypothesetoetsing

### 📌 Wat laat de grafiek zien?

- De **cyaanblauwe kromme** is de kansverdeling onder $H_0$, d.w.z. $\bar{X} \sim N(\mu_0, \frac{\sigma}{\sqrt{n}})$.
- Het **lichtgroene interval** onder de grafiek toont het **acceptatiegebied**.
- De **rode intervallen** tonen het **kritieke gebied**, afhankelijk van de gekozen toets.
- De **goudgele kromme** stelt de kansverdeling onder de alternatieve hypothese $H_1$ voor.
- Het **rood gearceerde oppervlak** geeft de kans op een **type-I fout** ($\alpha$) weer.
- Het ** geel gearceerde oppervlak** geeft de kans op een **type-II fout** ($\beta$) weer.

### 🧩 Interpretatie

-  **Type-I fout ($\alpha$):** de kans dat we $H_0$ onterecht verwerpen.
-  **Type-II fout ($\beta$):** de kans dat we $H_0$ niet verwerpen terwijl $H_1$ waar is.
- ✅ **Onderscheidend vermogen van de toets:** $1 - \beta$

### 🧮 Invloeden op het onderscheidend vermogen

- Kleinere afstand tussen $\mu_0$ en $\mu_1$ $\rightarrow$ lager onderscheidend vermogen $1 - \beta$
- Grotere standaardafwijking $\sigma$ $\rightarrow$ lager onderscheidend vermogen $1 - \beta$
- Grotere steekproefgrootte $n$ $\rightarrow$ hoger onderscheidend vermogen $1 - \beta$
- Grotere $\alpha$ $\rightarrow$ hoger onderscheidend vermogen $1 - \beta$ (omdat we de kans op een type-I fout verhogen, en daardoor de kans op een type-II fout $\beta$ verlagen)
"""

# Call generate_streamlit_page with the plot_binomiale_verdeling function
generate_streamlit_page(
    sliders=slider_dict,
    plot_function=plot_hypothesis_testing, 
    page_header=page_header,
    plot_title=plot_title, 
    xlabel=xlabel, 
    ylabel=ylabel,
    explanation_md=(explanation_title, explanation_md), 
    subplot_dims=(1, 1)  # Single plot (1x1)
)
