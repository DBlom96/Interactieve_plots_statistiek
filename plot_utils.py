import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import mplcyberpunk

# Define a function to create a consistent figure style
def create_figure(figsize, title, xlabel, ylabel, subplot_dims):
    """
    Creates a figure with a flexible subplot layout
    
    Arguments:
        figsize (tuple): Figure size (width, height)
        title (str): Title of the plot.
        xlabel (str): Label for x-axis
        ylabel (str): Label for y-axis
        subplot_dims (tuple): Tuple (nrows, ncols) defining the subplot grid.

    Returns:
        fig, ax: The figure and axes (single Axes object or an array of Axes).
    """


    fig, axes = plt.subplots(*subplot_dims, figsize=figsize)
    fig.suptitle(title, fontsize=14, fontweight='bold')
    plt.style.use("cyberpunk")

    # Ensure axes is iterable (works for both single and multiple subplots)
    if isinstance(axes, np.ndarray):
        axes = axes.ravel()  # Flatten if it's a 2D array
    else:
        axes = [axes]  # Convert single Axes to a list

    # Apply formatting to all subplots
    for ax in axes:
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.grid(True, linestyle="--", linewidth=0.7, alpha=0.6)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    return fig, axes

def generate_streamlit_page(sliders, plot_function, figsize=(8, 5), title="Interactieve plot", xlabel="$x$", ylabel="$y$", subplot_dims=(1,1)):
    """
    Generates a Streamlit page with a dynamic sidebar and a main plot area.

    Args:
        sliders (dict): Sidebar sliders.
        plot_function (function): Function to generate the plots (receives `axes` and `user_inputs`).
        figsize (tuple): Width and height of the figure in the main plot area
        title (str): Title of the main plot.
        xlabel (str): Label for the x-axis.
        ylabel (str): Label for the y-axis.
        subplot_dims (tuple): Tuple (rows, cols) defining the subplot grid.
    """

    # Create figure and axes
    fig, axes = create_figure(figsize, title, xlabel, ylabel, subplot_dims=subplot_dims)

    # Call the provided plotting function
    plot_function(axes, sliders)

    mplcyberpunk.make_lines_glow()
    plt.tight_layout()
    st.pyplot(fig)
