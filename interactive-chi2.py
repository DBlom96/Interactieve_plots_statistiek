import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from scipy.stats import chi2
from plot_utils import cyberpunk_color_cycle, generate_streamlit_page

st.set_page_config(layout="wide")

def add_sidebar_chi2():
    with st.sidebar:
        st.header("Sliders voor parameters")
        
        # Specific sliders for each distribution
        df = st.slider(label="Aantal vrijheidsgraden (df)", min_value=1, max_value=100, value=5)
        method = st.selectbox("Selecteer method voor grenzen", ["Absoluut", "Percentiel"])
        x_max = max(10, df + 5 * np.sqrt(df))

        if method == "Absoluut":
            # Grenzen zijn absolute getallen
            links = st.number_input(label="Linkergrens $g_{{L}}$", format="%.3f", min_value=0.0, max_value=float(x_max), value=0.5*df, step=0.01)
            rechts = st.number_input(label="Rechtergrens $g_{{R}}$", format="%.3f", min_value=links, max_value=float(x_max), value=2.5*df)
        else:
            p_min = st.number_input("Linkergrens (percentiel)", format="%.3f", min_value=0.0, max_value=1.0, value=0.025, step=0.005)
            p_max = st.number_input("Rechtergrens (percentiel)", format="%.3f", min_value=p_min, max_value=1.0, value=0.975, step=0.005)
            links = chi2.ppf(p_min, df=df)
            rechts = chi2.ppf(p_max, df=df)

    slider_dict = {"df": df, "method": method, "links": links, "rechts": rechts}
    return slider_dict

# Function to plot the chi square distribution
def plot_chi2_distribution(axes, user_inputs):
    df, method, links, rechts = user_inputs.values()

    x_max = max(10, df + 5 * np.sqrt(df))
    x = np.linspace(0, x_max, 1_000)
    y = chi2.pdf(x, df=df)
    color_cycle = cyberpunk_color_cycle()
    fill_color = color_cycle[2] # neon green

    axes[0].plot(x, y, label=f"$\chi^2(df={df})$")
    axes[0].fill_between(x, y, where=(x>=links)&(x<=rechts), color=fill_color, alpha=0.3)
    axes[0].set_xlim(0, x_max)
    axes[0].set_title(f"Chi-kwadraatverdeling (met df$={df}$ vrijheidsgraden)")
    axes[0].set_xlabel("$x$")
    axes[0].set_ylabel("Kansdichtheid $f(x)$")

    ytext = -0.05 * axes[0].get_ylim()[1]
    axes[0].text(links, ytext, f"{links:.4f}", ha="center", va="center", fontsize=9, color=fill_color)
    axes[0].text(rechts, ytext, f"{rechts:.4f}", ha="center", va="center", fontsize=9, color=fill_color)
    axes[0].set_ylim(bottom=3*ytext)
    axes[0].legend()


if __name__ == "__main__":
    slider_dict = add_sidebar_chi2()

    # Generate the Streamlit page with the sidebar and plot
    title="Interactieve plot: de $\chi^2$-verdeling"
    xlabel="$x$"
    ylabel="Kansdichtheid $f(x)$"

    # Call generate_streamlit_page with the plot_binomiale_verdeling function
    generate_streamlit_page(
        slider_dict, 
        plot_chi2_distribution, 
        title=title, 
        xlabel=xlabel, 
        ylabel=ylabel,
        subplot_dims=(1, 1)  # Single plot (1x1)
    )