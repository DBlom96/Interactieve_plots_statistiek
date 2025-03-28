import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import mplcyberpunk
from scipy.stats import norm, t
from plot_utils import cyberpunk_color_cycle, generate_streamlit_page

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

    
    axes[0].plot(x, t_pdf, label=f"$t$-verdeling $t(df={df})$", color=t_color, lw=2)
    if df >= 3:
        axes[0].plot([-t_critical, -t_critical], [0, t.pdf(-t_critical, df=df)], color=t_color, linestyle='--')
        axes[0].plot([t_critical, t_critical], [0, t.pdf(t_critical,df=df)], color=t_color, linestyle='--')

    # title and legend
    if df == 1:
        plt.suptitle(f"Vergelijking tussen de standaardnormale verdeling $N(0,1)$ en de $t$-verdeling met 1 vrijheidsgraad")
    else:
        plt.suptitle(f"Vergelijking tussen de standaardnormale verdeling $N(0,1)$ en de $t$-verdeling met {df} vrijheidsgraden")
    
    
    
    plt.title( \
        f"{1-alpha}-voorspellingsinterval voor $N(0,1)$:\t$[{-z_critical:.2f}, {z_critical:.2f}]$\n{1-alpha}-voorspellingsinterval voor $t(df={df})$:\t$[{-t_critical:.2f}, {t_critical:.2f}]$"
    )
    axes[0].legend()
    
    # Apply cyberpunk glow effect
    # mplcyberpunk.add_glow_effects()

# Generate plot using the generic function
slider_dict = add_sidebar_t_distribution()

title="Vergelijking tussen de standaardnormale verdeling $N(0,1)$ en de $t$-verdeling met df vrijheidsgraden"
xlabel="$x$"
ylabel="Kansdichtheid $f(x)$"
generate_streamlit_page(
    slider_dict,
    plot_t_distribution,
    title=title,
    xlabel=xlabel,
    ylabel=ylabel,
    subplot_dims=(1,1))
