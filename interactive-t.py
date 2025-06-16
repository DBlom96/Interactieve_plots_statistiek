import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import mplcyberpunk
from scipy.stats import norm, t
from utils.streamlit_utils import generate_streamlit_page
from utils.plot_style import cyberpunk_color_cycle

# Set Streamlit page layout
st.set_page_config(layout="wide")

def add_sidebar_t_distribution():
    """Adds sidebar sliders for t-distribution settings."""
    with st.sidebar:
        st.header("Sliders voor parameters")
        df = st.slider("Aantal vrijheidsgraden (df)", min_value=1, max_value=100, value=1, step=1)
    slider_dict = {"df": df}
    return slider_dict

def plot_t_distribution(axes, user_inputs):
    """Plots the standard normal and Student's t-distribution."""
    df = user_inputs["df"]
    alpha = 0.05
    confidence = 1-alpha
    confidence_percentage = int(100 * confidence)
    color_cycle = cyberpunk_color_cycle()

    normal_color = color_cycle[2] # "cyan"
    t_color = color_cycle[7] # "gold"

    # Define x values for plotting
    # x_min, x_max = -6 if df <= 2 else -4, 6 if df <= 2 else 4
    x = np.linspace(-4, 4, 1_000)

    # Compute probability density functions
    normal_pdf = norm.pdf(x, loc=0, scale=1)
    t_pdf = t.pdf(x, df=df)

    z_critical = norm.ppf(1-alpha/2)
    t_critical = t.ppf(1-alpha/2, df=df)
    print(z_critical, t_critical)

    # Plot distributions
    axes[0].plot(x, normal_pdf, label="Normale verdeling $N(0,1)$", color=normal_color, lw=2)
    axes[0].plot([-z_critical, -z_critical], [0, norm.pdf(-z_critical)], color=normal_color, linestyle='--')
    axes[0].plot([z_critical, z_critical], [0, norm.pdf(z_critical)], color=normal_color, linestyle='--')

    if df == 1:
        axes[0].plot(x, t_pdf, label=f"$t$-verdeling met 1 vrijheidsgraad", color=t_color, lw=2)
        plt.suptitle(f"Standaardnormale verdeling $N(0,1)$ versus de $t$-verdeling met 1 vrijheidsgraad")

    else:
        axes[0].plot(x, t_pdf, label=f"$t$-verdeling met $df={df}$ vrijheidsgraden", color=t_color, lw=2)
        plt.suptitle(f"Standaardnormale verdeling $N(0,1)$ versus de $t$-verdeling met {df} vrijheidsgraden")

        if df >= 3:
            axes[0].plot([-t_critical, -t_critical], [0, t.pdf(-t_critical, df=df)], color=t_color, linestyle='--')
            axes[0].plot([t_critical, t_critical], [0, t.pdf(t_critical,df=df)], color=t_color, linestyle='--')
    
    title_normal = f"{confidence_percentage}%-voorspellingsinterval voor $N(0,1)$:\t$[{-z_critical:.4f}, {z_critical:.4f}]$"
    title_t = f"{confidence_percentage}%-voorspellingsinterval voor $t(df={df})$:\t$[{-t_critical:.4f}, {t_critical:.4f}]$"
    plt.suptitle(f"{title_normal}\n{title_t}")
    plt.tight_layout(rect=[0,0,1,0.92])
    axes[0].legend()
    
    # Apply cyberpunk glow effect

# Generate plot using the generic function
slider_dict = add_sidebar_t_distribution()
page_header="Interactieve plot: Student's $t$-verdeling"
plot_title=f"Vergelijking tussen de standaardnormale verdeling $N(0,1)$ en de $t$-verdeling met df={slider_dict["df"]} vrijheidsgraden"
xlabel="$x$"
ylabel="Kansdichtheidsfunctie $f(x)$"
explanation_title = "# :book: Uitleg: Student's $t$-verdeling"
explanation_md = fr"""
### 📊 Uitleg: Vergelijking tussen de standaardnormale verdeling en de $t$-verdeling

De standaardnormale verdeling $N(0,1)$ is een theoretisch model met een vaste vorm: symmetrisch, klokvormig, en met gemiddelde 0 en standaardafwijking 1.

### 📌 De $t$-verdeling in het kort
De **$t$-verdeling** heeft dikkere staarten. Bij weinig vrijheidsgraden is deze breder; bij veel vrijheidsgraden lijkt hij steeds meer op $N(0,1)$.

- **Blauw** = kansdichtheidsfunctie van de standaardnormale verdeling $N(0,1)$
- **Goud** = kansdichtheidsfunctie van de $t$-verdeling met $df={slider_dict["df"]}$ {"vrijheidsgraad" if slider_dict["df"]==1 else "vrijheidsgraden"}
- Stippellijnen = grenzen van 95%-betrouwbaarheidsintervallen

🧠 *Gebruik de $t$-verdeling bij kleine steekproeven ($n < 30$) en een onbekende standaardafwijking $\sigma$ om een betrouwbaarheidsinterval te berekenen voor het gemiddelde $\mu$ van een normale verdeling).*
"""

# show_explanation("Uitleg: normale vs. t-verdeling", explanation_md)
generate_streamlit_page(
    slider_dict,
    plot_t_distribution,
    page_header=page_header,
    plot_title=plot_title,
    figsize=(10,5),
    xlabel=xlabel,
    ylabel=ylabel,
    explanation_md=(explanation_title, explanation_md),
    subplot_dims=(1,1))
