import streamlit as st
from utils.constants import *
from matplotlib.pyplot import rcParams

import matplotlib.font_manager as fm
fm.fontManager.addfont("./styles/JetBrainsMono-Regular.ttf")  # only if shipping the .ttf
fm._load_fontmanager(try_read_cache=False)

def load_css(path = "./styles/style.css"):
    """Laadt de gedeelde CSS-stylesheet in de Streamlit-app."""
    with open(path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def page_header(title: str, subtitle: str = "") -> None:
    """
    Toont een gestandaardiseerde paginatitel met optionele eyebrow-tekst.
 
    Args:
        title:    Hoofdtitel van de pagina (bijv. 'Binomiale verdeling').
        subtitle: Optionele eyebrow boven de titel (bijv. 'Kansverdelingen · Discreet').
    """
    if subtitle:
        st.markdown(
            f"<p style='font-size:14px; text-transform:uppercase; letter-spacing:0.10em;"
            f" color:rgba(168,218,220,0.55); margin-bottom:0.1rem; font-family:\"JetBrains Mono\",monospace;'>"
            f"{subtitle}</p>",
            unsafe_allow_html=True,
        )
    st.title(title)

# ----------------------------------
# MATPLOTLIB HELPERS
# ----------------------------------
def apply_dark_style(fig, ax, title=None, suptitle=None, xlabel=None, ylabel=None):
    rcParams.update({
        "font.family": "monospace",
        "font.monospace": ["JetBrains Mono", "Courier New", "monospace"],
    })

    # Background
    fig.patch.set_facecolor(color=BG_COLOR)
    ax.set_facecolor(color=BG_COLOR)

    # Spines - all invisible
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Grid - horizontal only
    ax.yaxis.grid(True, color=PLOT_FONT_COLOR, alpha=0.15, linewidth=0.6)
    ax.xaxis.grid(False)
    ax.set_axisbelow(True)

    # Ticks
    ax.tick_params(colors=PLOT_FONT_COLOR, labelsize=TICK_FONT_SIZE)

    # Labels
    if title:
        ax.set_title(title, fontsize=TITLE_FONT_SIZE, fontfamily=FONT_FAMILY,
                     color=PLOT_FONT_COLOR, pad=12)
    
    if suptitle:
        fig.suptitle(suptitle, fontsize=AXIS_FONT_SIZE, fontfamily=FONT_FAMILY,
                     color=PLOT_FONT_COLOR)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=AXIS_FONT_SIZE, fontfamily=FONT_FAMILY,
                      color=PLOT_FONT_COLOR)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=AXIS_FONT_SIZE, fontfamily=FONT_FAMILY,
                      color=PLOT_FONT_COLOR)
        
    # Tick label font
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontfamily(FONT_FAMILY)

def stem_plot(ax, k, y, color):
    """Draw a stem (needle) plot manually."""
    ax.scatter(k, y, color=color, s=40, zorder=3)
    for xi, yi in zip(k, y):
        ax.plot([xi, xi], [0, yi], color=color, linewidth=1.8)