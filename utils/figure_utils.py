import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from matplotlib.ticker import MaxNLocator
from typing import Tuple, List
from utils import show_explanation

def create_figure(
    figsize: Tuple[int, int],
    page_header: str,
    plot_title: str,
    xlabel: str,
    ylabel: str,
    subplot_dims: Tuple[int, int] = (1, 1)
) -> Tuple[plt.Figure, List[plt.Axes]]:
    """
    Maakt een matplotlib figuur en assen met consistente opmaak.

    Args:
        figsize: Grootte van de figuur (breedte, hoogte).
        title: Titel van de figuur.
        xlabel: X-as label.
        ylabel: Y-as label.
        subplot_dims: (rijen, kolommen) voor subplotindeling.

    Returns:
        fig: De figuur.
        axes: Een lijst van Axes objecten.
    """
    fig, axes = plt.subplots(*subplot_dims, figsize=figsize)
    st.header(page_header)#, fontsize=14, fontweight='bold')
    fig.suptitle(plot_title)

    if isinstance(axes, np.ndarray):
        axes = axes.ravel()
    else:
        axes = [axes]

    for ax in axes:
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.grid(True, linestyle="--", linewidth=0.7, alpha=0.6)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    return fig, axes
