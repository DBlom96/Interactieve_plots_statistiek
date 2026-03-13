import streamlit as st
from matplotlib.colors import to_rgb

def css_to_rgba(css_color, alpha = 0.4) -> str:
    """Converteert een CSS-kleur naar een rgba-string voor Plotly."""
    r, g, b = [int(c * 255) for c in to_rgb(css_color)]
    return f"rgba({r},{g},{b},{alpha})"


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
            f"<p style='font-size:11px; text-transform:uppercase; letter-spacing:0.10em;"
            f" color:rgba(168,218,220,0.55); margin-bottom:0.1rem; font-family:\"JetBrains Mono\",monospace;'>"
            f"{subtitle}</p>",
            unsafe_allow_html=True,
        )
    st.title(title)