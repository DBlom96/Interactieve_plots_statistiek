import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import mplcyberpunk
from scipy.stats import norm, t
from plot_utils import cyberpunk_color_cycle, generate_streamlit_page
import plotly.graph_objects as go

# Function to generate the plot with points and regression line
def plot_regression_plotly(axes, user_inputs):
    xcoords = []
    ycoords = []
    xmin, xmax, ymin, ymax = user_inputs.values()

    # Create scatter plot
    fig = go.Figure()

    # Add scatter points (original points)
    if len(xcoords) > 0 and len(ycoords) > 0:  # Only plot if there are points
        fig.add_trace(go.Scatter(x=xcoords, y=ycoords, mode='markers', name='Data Points', marker=dict(color='blue', size=10)))

    # Add regression line (if enough points are present to calculate regression)
    if len(xcoords) > 1:
        line_slope = 1
        line_intercept = 1
        fig.add_trace(go.Scatter(x=xcoords, y=line_slope * np.array(xcoords) + line_intercept, mode='lines', name='Regression Line', line=dict(color='red', width=2)))

    # Adjust axis ranges based on the input sliders
    fig.update_layout(
        title="Linear Regression (Interactive)",
        xaxis_title="X",
        yaxis_title="Y",
        xaxis=dict(range=[xmin, xmax]),  # Set x-axis range
        yaxis=dict(range=[ymin, ymax]),  # Set y-axis range
        showlegend=True
    )
    
    # Display the plot with Streamlit
    st.plotly_chart(fig, use_container_width=True)

# Function to add sliders and plot settings in the sidebar
def add_sidebar_regression():
    with st.sidebar:
        st.header("Sliders voor parameters")

        # Define sliders for adding data points
        minx = st.number_input(label="Minimum $x$", value=0)
        maxx = st.number_input(label="Maximum $x$", value=100)
        miny = st.number_input(label="Minimum $y$", value=0)
        maxy = st.number_input(label="Maximum $y$", value=100)
    
    slider_dict = {'minx': minx, 'maxx': maxx, 'miny': miny, 'maxy': maxy}
    return slider_dict

slider_dict = add_sidebar_regression()
title="Vergelijking tussen de standaardnormale verdeling $N(0,1)$ en de $t$-verdeling met df vrijheidsgraden"
xlabel="$x$"
ylabel="Kansdichtheid $f(x)$"
generate_streamlit_page(
    slider_dict,
    plot_regression_plotly,
    title=title,
    xlabel=xlabel,
    ylabel=ylabel,
    subplot_dims=(1,1))
