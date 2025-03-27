import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# Define a function to create a consistent figure style
def create_figure(figsize=(8, 5), title="Interactieve plot", xlabel="$x$", ylabel="$y$"):
    fig, ax = plt.subplots(figsize=figsize)
    sns.set_style("darkgrid")
    ax.set_title(title, fontsize=14, fontweight='bold', pad=10)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.grid(True, linestyle="--", linewidth=0.7, alpha=0.6) # light grid

    # Remove top and right spines for a cleaner look
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return fig, ax

# Define color scheme
colors = {
    "binomial": "blue",
    "poisson": "red",
    "normal": "green",
    "exponential": "purple"
}

# Generic sidebar function for interactive inputs
def add_sidebar(params):
    """
    Adds sliders dynamically based on input dictionary

    params: dict
        Keys: parameter names
        Values: Dict with 'min', 'max', 'value', 'step' values
    
    Returns: dict with updated values from sliders
    """
    with st.sidebar:
        st.header("Sliders voor parameters")
        values = {}
        for param, options in params.items():
            if isinstance(options['value'], int):
                # Integer slider
                values[param] = st.slider(
                    label=options['label'], min_value=options['min'],
                    max_value=options['max'], value=options['value'], step=options['step']
                )
            else:
                # Float slider
                values[param] = st.slider(
                    label=options['label'], min_value=options['min'],
                    max_value=options['max'], value=options['value'],
                    step=options['step'], format="%.3f"
                )
        return values
