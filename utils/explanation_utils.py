import streamlit as st

def show_explanation(title: str, markdown_text: str):
    """Toont een uitlegblok onder een vaste titel, met optionele LaTeX-ondersteuning."""
    with st.expander(f"📘 {title}", expanded=False):
        st.markdown(markdown_text, unsafe_allow_html=False)