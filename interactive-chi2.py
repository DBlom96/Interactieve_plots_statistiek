import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from scipy.stats import chi2
from utils.plot_style import cyberpunk_color_cycle
from utils.streamlit_utils import generate_streamlit_page

st.set_page_config(layout="wide")
def add_sidebar_chi2():
    with st.sidebar:
        st.header("Instellingen voor chi-kwadraatverdeling")
        
        df = st.slider("Aantal vrijheidsgraden (df)", 1, 100, 5)
        methode = st.selectbox("Selecteer visualisatiemethode", [
            "Plot",
            "Hypothesetoets: kritiek gebied",
            "Hypothesetoets: p-waarde"
        ])

        slider_dict = {"df": df, "methode": methode}

        if methode != "Plot":
            alpha = st.slider("Significantieniveau $\\alpha$", min_value=0.001, max_value=0.2, value=0.05, step=0.005)
            toetsingsgrootheid = st.number_input("Toetsingsgrootheid $\\chi^2$", min_value=0.0, max_value=500.0, value=2.0, step=0.1)
            slider_dict["alpha"] = alpha
            slider_dict["toetsingsgrootheid"] = toetsingsgrootheid

    return slider_dict

# Function to plot the chi square distribution

def plot_chi2_distribution(axes, inputs):
    df = inputs["df"]
    methode = inputs["methode"]
    xmin, xmax = 0, max(10, df + 5 * np.sqrt(df))
    x = np.linspace(xmin, xmax, 1000)
    y = chi2.pdf(x, df)
    ymax = min(0.5, max(y)) 
    ytext = -0.2 * ymax  # Position for the horizontal line 
    ylines = 1/2 * ytext
    color_cycle = cyberpunk_color_cycle()
    
    acceptable_color = color_cycle[1] # "neongreen"
    fill_color = color_cycle[2] # "cyan"
    critical_color = color_cycle[6] # "tomato red"

    ax = axes[0]
    ax.plot(x, y, label=f"$\\chi^2(df={df})$")
    ax.set_xlim(0, xmax)
    ax.set_ylim(bottom=1.5*ytext, top=1.1*ymax)

    ax.set_xlabel("x")
    ax.set_ylabel("Kansdichtheid $f(x)$")
    plt.suptitle(f"Chi-kwadraatverdeling met df = {df} {"vrijheidsgraden" if df > 1 else "vrijheidsgraad"}.", fontsize=20)

    if methode != "Plot":
        alpha = inputs["alpha"]
        toetsingsgrootheid = inputs["toetsingsgrootheid"]
        grens = chi2.ppf(1 - alpha, df)
        p_waarde = 1 - chi2.cdf(toetsingsgrootheid, df=df)
        
        # ax.fill_between(x, y, where=(x < grens), color=acceptable_color, alpha=0.3)
        ax.fill_between(x, y, where=(x >= grens), color=critical_color, alpha=0.3, label=f"Kritiek gebied ($\\alpha={inputs['alpha']:.2f}$): $[{grens:.4f}, \\infty)$")
        ax.plot([toetsingsgrootheid, toetsingsgrootheid], [0, chi2.pdf(toetsingsgrootheid, df=df)], color=fill_color, linestyle="--")
        ax.plot([grens, grens], [0, chi2.pdf(grens, df=df)], color=critical_color, linestyle="--")
        ax.text(toetsingsgrootheid, ytext, "$\\chi^2$", color=fill_color, ha="center", va="center")
        ax.text(grens, ytext, "$g$", color=critical_color, ha="center", va="center")
        
        if methode == "Hypothesetoets: kritiek gebied":
            # Teken het kritieke gebied
            ax.hlines(ylines, 0, grens, color=acceptable_color, linewidth=5)
            ax.hlines(ylines, grens, xmax, color=critical_color, linewidth=5)
            ax.text((xmin + grens) / 2, ytext, 'Accepteer $H_0$', color=acceptable_color, fontsize=11, ha='center')
            ax.text((grens + xmax) / 2, ytext, 'Verwerp $H_0$', color=critical_color, fontsize=11, ha='center')

        elif methode == "Hypothesetoets: p-waarde":
            ax.fill_between(x, y, where=(x >= toetsingsgrootheid), color=fill_color, alpha=0.3, label=f"$p = {p_waarde:.4f}$")
    
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), ncol=1)

slider_dict = add_sidebar_chi2()

page_header="Interactieve plot: de chikwadraatverdeling"
plot_title=f"Plot van de chikwadraatverdeling met df={slider_dict["df"]} vrijheidsgraden."
explanation_title = "# :book: Uitleg: de chikwadraat-verdeling"
explanation_md = fr"""
### 📊 Uitleg: De $\chi^2$-verdeling

De **$\chi^2$-verdeling** (chikwadraatverdeling) is een verdeling die vooral wordt gebruikt bij toetsen over varianties, onafhankelijkheid tussen twee categorische variabelen en in goodness-of-fit tests.

### 📌 Eigenschappen van de $\chi^2$-verdeling:
- De verdeling is **niet symmetrisch** en altijd **positief**: $x \geq 0$
- De vorm hangt af van het aantal **vrijheidsgraden** $df$
  - Bij lage $df$ is de verdeling scheef naar rechts
  - Bij hoge $df$ benadert de chikwadraatverdeling een normale verdeling
- De verwachte waarde is gelijk aan $df$, en de variantie is $2 \cdot df$

🧪 *Typische toepassingen*:
- Toetsen of een waargenomen variantie afwijkt van een verwachte waarde
- Goodness-of-fit toets: komt een verdeling overeen met een verwachte verdeling?
- Onafhankelijkheidstoetsen in kruistabellen: zijn twee categorische variabelen onafhankelijk van elkaar of niet?

### 🎨 Visualisatie
- De curve toont de kansdichtheid van de $\chi^2$-verdeling bij $df = {slider_dict["df"]}$ {"vrijheidsgraad" if slider_dict["df"] == 1 else "vrijheidsgraden"}.
- **Gekleurde gebieden** representeren toetsingsgebieden of betrouwbaarheidsintervallen, afhankelijk van de gekozen methode
"""

generate_streamlit_page(
    slider_dict,
    plot_chi2_distribution,
    page_header=page_header,
    plot_title="Interactieve plot: de $\chi^2$-verdeling",
    xlabel="$x$",
    ylabel="Kansdichtheid $f(x)$",
    explanation_md=(explanation_title, explanation_md),
    subplot_dims=(1, 1)
)

