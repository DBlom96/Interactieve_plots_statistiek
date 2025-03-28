import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import mplcyberpunk

# Define a function to create a consistent figure style
def create_figure(figsize, title, xlabel, ylabel):
    """
    Creates a matplotlib figure with a consistent style
    """
    fig, ax = plt.subplots(figsize=figsize)
    plt.style.use("cyberpunk")
    ax.set_title(title, fontsize=14, fontweight='bold', pad=10)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.grid(True, linestyle="--", linewidth=0.7, alpha=0.6)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    return fig, ax

# Generic sidebar function for interactive inputs
def add_sidebar(params):
    """
    Creates a sidebar with sliders dynamically based on input dictionary"
    """
    with st.sidebar:
        st.header("Sliders voor parameters")
        values = {}
        for param, options in params.items():
            values[param] = st.slider(
                label=options['label'],
                min_value=options['min'],
                max_value=options['max'],
                value=options['value'],
                step=options['step'],
                format="%.2f" if isinstance(options['value'], float) else "%d"
            )
    return values

def generate_streamlit_page(params, plot_function, figsize=(8, 5), title="Interactieve plot", xlabel="$x$", ylabel="$y$"):
    """
    Generates a Streamlit page with a sidebar and a main plot area
    """
    user_inputs = add_sidebar(params)
    st.subheader(title)
    fig, ax = create_figure(figsize, title, xlabel, ylabel)
    plot_function(ax, user_inputs)
    mplcyberpunk.make_lines_glow()
    plt.tight_layout()
    st.pyplot(fig)
    return user_inputs