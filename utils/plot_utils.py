import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import mplcyberpunk
from utils.explanation_utils import show_explanation

plt.style.use("cyberpunk")

def cyberpunk_color_cycle():
    # Get the current color cycle from matplotlib after applying the cyberpunk style
    return [
        "#ff00ff",  # Magenta
        "#00ff00",  # Neon Green
        "#00ffff",  # Cyan
        "#ff4500",  # Orange-Red
        "#ff1493",  # Deep Pink
        "#7fff00",  # Chartreuse Green
        "#ff6347",  # Tomato Red
        "#ffd700",  # Gold
        "#ff69b4",  # Hot Pink
        "#ffff00"   # Yellow
    ]    

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

def generate_streamlit_page(sliders, plot_function, figsize=(8, 5), title="Interactieve plot", xlabel="$x$", ylabel="$y$", explanation_md="", subplot_dims=(1,1)):
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

    # Create explanation markdown
    show_explanation("Uitleg:", explanation_md)

    # Create figure and axes
    fig, axes = create_figure(figsize, title, xlabel, ylabel, subplot_dims=subplot_dims)

    # Call the provided plotting function
    plot_function(axes, sliders)

    mplcyberpunk.make_lines_glow()
    # plt.tight_layout()
    st.pyplot(fig)
