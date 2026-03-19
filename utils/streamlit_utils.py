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

def stem_plot(ax, k, y, color, highlighted=None, highlight_color=None):
    """Draw a stem (needle) plot, optionally highlighting a subset of k values."""
    for xi, yi in zip(k, y):
        c = highlight_color if (highlighted is not None and xi in highlighted) else color
        ax.plot([xi, xi], [0, yi], color=c, linewidth=1.8)
        ax.scatter(xi, yi, color=c, s=40, zorder=3)


def get_highlighted(mode, lo, hi, k):
    """Return the set of k values that fall inside the selected region."""
    if mode == r"P(X ≤ b)" and hi is not None:
        return set(k[k <= hi])
    elif mode == r"P(X ≥ a)" and lo is not None:
        return set(k[k >= lo])
    elif mode == r"P(a ≤ X ≤ b)" and lo is not None and hi is not None and lo <= hi:
        return set(k[(k >= lo) & (k <= hi)])
    return None


def add_cdf_markers(ax, k, cdf_y, mode, lo, hi):
    """Mark the queried CDF value(s) with a dot and dashed drop-lines."""
    points = []
    if mode == r"P(X ≤ b)" and hi is not None:
        points = [(hi, cdf_y[hi])]
    elif mode == r"P(X ≥ a)" and lo is not None:
        points = [(lo, cdf_y[lo])]
    elif mode == r"P(a ≤ X ≤ b)" and lo is not None and hi is not None:
        points = [(lo, cdf_y[lo]), (hi, cdf_y[hi])]