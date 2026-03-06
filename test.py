import streamlit as st
import plotly.graph_objects as go

fig = go.Figure()

fig.update_layout(
    title=r"$\mu$",
    xaxis=dict(title=r"$\bar{x}$"),
    yaxis=dict(title=r"$i$")
)

st.plotly_chart(fig)