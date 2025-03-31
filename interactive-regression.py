import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import mplcyberpunk
from scipy.stats import norm, t
from plot_utils import cyberpunk_color_cycle, generate_streamlit_page

# Function to add sliders and plot settings in the sidebar
def add_sidebar_regression():
    with st.sidebar:
        st.header("Sliders voor parameters")

        # Define sliders for the range of the plot
        minx = st.number_input(label="Minimum $x$", value=0)
        maxx = st.number_input(label="Maximum $x$", value=100)
        miny = st.number_input(label="Minimum $y$", value=0)
        maxy = st.number_input(label="Maximum $y$", value=100)
    
    slider_dict = {'minx': minx, 'maxx': maxx, 'miny': miny, 'maxy': maxy}
    return slider_dict

# Function to generate the plot with points and regression line
def plot_regression_plotly(user_inputs):
    xmin, xmax, ymin, ymax = user_inputs.values()

# Initialize session state to store points
if 'points' not in st.session_state:
    st.session_state.points = []

# Function to handle mouse click events on the plot
def on_click(event):
    # Only add points if the mouse is clicked inside the axes
    if event.inaxes:
        x = event.xdata
        y = event.ydata
        st.session_state.points.append((x, y))
        update_plot()

# Function to update the plot
def update_plot():
    # Create a figure and axis for plotting
    fig, ax = plt.subplots()
    
    # Extract points from session state
    xcoords, ycoords = zip(*st.session_state.points) if st.session_state.points else ([], [])
    
    # Plot the points
    ax.scatter(xcoords, ycoords, color='blue', label='Data Points')

    # Optionally, you can add a regression line if there are enough points
    if len(xcoords) > 1:
        # Fit a simple linear regression line
        slope, intercept = np.polyfit(xcoords, ycoords, 1)
        line_x = np.linspace(min(xcoords), max(xcoords), 100)
        line_y = slope * line_x + intercept
        ax.plot(line_x, line_y, color='red', label='Regression Line')

    # Add title and labels
    ax.set_title('Click to Add Points')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    
    # Show the legend
    ax.legend()

    # Display the plot in Streamlit
    st.pyplot(fig)

# Create a plot and add the click event handler
fig, ax = plt.subplots()
fig.canvas.mpl_connect('button_press_event', on_click)

# Display initial empty plot
update_plot()

# Sidebar setup for sliders
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
