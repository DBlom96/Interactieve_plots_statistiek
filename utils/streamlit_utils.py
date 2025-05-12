import streamlit as st
import mplcyberpunk
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from typing import Callable, Dict, Any, Tuple

from utils.explanation_utils import show_explanation  # Blijft zoals u het had
from utils.figure_utils import create_figure
from utils.plot_style import set_plot_style

def generate_streamlit_page(
    sliders: Dict[str, Any],
    plot_function: Callable[[Any, Dict[str, Any]], None],
    figsize: Tuple[int, int] = (8, 5),
    page_header: str = "Interactieve plot",
    plot_title: str = "Interactieve plot",
    xlabel: str = "$x$",
    ylabel: str = "$y$",
    explanation_md: Tuple[str, str] = ("Uitleg:", ""),
    subplot_dims: Tuple[int, int] = (1, 1),
) -> None:
    """
    Genereert een gestandaardiseerde Streamlit pagina met uitleg, sliders en een plot.

    Args:
        sliders: Ingevoerde waarden via sliders.
        plot_function: Functie die een plot tekent op de assen.
        figsize: Grootte van de figuur.
        page_header: header van de gehele pagina.
        plot_title: Titel van de figuur.
        xlabel: X-as label.
        ylabel: Y-as label.
        explanation_md: Markdown tekst voor uitleg.
        subplot_dims: Indeling (rijen, kolommen) van subplots.
    """

    set_plot_style("cyberpunk")

    # show_explanation(*explanation_md)

    fig, axes = create_figure(figsize, page_header, plot_title, xlabel, ylabel, subplot_dims=subplot_dims)

    plot_function(axes, sliders)


    # if style.lower() == "cyberpunk":
    mplcyberpunk.make_lines_glow()
    st.pyplot(fig)

    show_explanation(*explanation_md)
