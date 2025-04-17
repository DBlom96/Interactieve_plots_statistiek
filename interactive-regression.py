import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import mplcyberpunk
from sklearn.linear_model import LinearRegression
from plot_utils import cyberpunk_color_cycle, generate_streamlit_page

# Initialize session state for storing points
if "points" not in st.session_state:
    st.session_state["points"] = {"x": {}, "y": {}}

# Function to handle sidebar input
def add_sidebar_regression():

    with st.sidebar:
        st.header("Invoer voor lineaire regressie:")

        point_input = st.sidebar.text_input(f"Voer een punt x, y in (voorbeeld: 2.5, 5.1)", value="0.0, 0.0")
        add_point_button = st.sidebar.button("Punt toevoegen")

        if add_point_button:
            # Parse the input and add the point to session state
            try:
                x, y = map(float, point_input.split(","))
                if st.session_state["points"]["x"] == {}:
                    idx_x = 0
                    idx_y = 0
                else:
                    idx_x = max(st.session_state["points"]["x"]) + 1
                    idx_y = max(st.session_state["points"]["y"]) + 1
        
                st.session_state["points"]["x"][idx_x] = x
                st.session_state["points"]["y"][idx_y] = y
                    
            except ValueError:
                st.sidebar.error("Schrijf het punt als twee getallen gescheiden door een komma. Gebruik een punt voor decimalen.")
    
    return st.session_state["points"]

def plot_regression(axes, user_inputs):
    """Plots the scatter points and regression line."""
    x_data, y_data = user_inputs["x"], user_inputs["y"]
    if x_data != {}:
        print(x_data, y_data)
        xcoords = list(x_data.values())
        ycoords = list(y_data.values()) 
        st.write(xcoords)

        # Set colors for the different parts of the regression plot
        color_cycle = cyberpunk_color_cycle()
        point_color = color_cycle[2] # "cyan"
        regression_line_color = color_cycle[1] # neon green"
        error_color = color_cycle[6] # "tomato red"

        # Perform linear regression if there are at least two points
        if len(ycoords) >= 2:
            xmin = min(xcoords) - 0.1 * (max(xcoords) - min(xcoords))
            xmax = max(xcoords) + 0.1 * (max(xcoords) - min(xcoords))
            ymin = min(ycoords) - 0.1 * (max(ycoords) - min(ycoords))
            ymax = max(ycoords) + 0.1 * (max(ycoords) - min(ycoords))
            axes[0].set_xlim(xmin, xmax)
            axes[0].set_ylim(ymin, ymax)

            xcoords = np.array(xcoords).reshape(-1, 1)
            ycoords = np.array(ycoords)

            # Scatter plot for the data points
            axes[0].scatter(xcoords, ycoords, color=point_color, label= "Datapunten", s=50)

            model = LinearRegression()
            model.fit(xcoords.reshape(-1, 1), ycoords)
            x_range = np.linspace(xmin, xmax, 1_000)
            y_pred = model.predict(x_range.reshape(-1, 1))

            # Add regression line to the plot
            slope = model.coef_[0]
            intercept = model.intercept_
            axes[0].plot(x_range, y_pred, color=regression_line_color, linewidth=2)
            st.write(f"Regressielijn: Y = {slope:.2f}X+{intercept:.2f}")

            for x, y in zip(xcoords, ycoords):
                axes[0].plot([x, x], [y, slope * x + intercept], linestyle="--", color=error_color)

    # Customize the plot
    st.header("Interactieve plot: lineaire regressie")
    axes[0].set_xlabel("X") #Interactieve plot: lineaire regressie", fontweight='bold')
    axes[0].set_ylabel("Y") #"Interactieve plot: lineaire regressie", fontweight='bold')

def display_points_table(user_inputs):
    """Displays a table of added points."""
    if user_inputs["x"] and user_inputs["y"]:  # Ensure points exist before showing table
        st.write("### Lijst met toegevoegde punten:")
        points_table = {
            "X": user_inputs["x"].values(),
            "Y": user_inputs["y"].values()
        }
        st.table(points_table)  # Display the table in Streamlit

user_inputs = add_sidebar_regression()
title="" #Interactieve plot: lineaire regressie"
xlabel=""#r"$X$"
ylabel=""#r"$Y$"

# Call generate_streamlit_page with the plot_binomiale_verdeling function
generate_streamlit_page(
    user_inputs, 
    plot_regression, 
    title=title, 
    xlabel=xlabel, 
    ylabel=ylabel,
    subplot_dims=(1, 1)  # Single plot (1x1)
)

# Display the points table
display_points_table(user_inputs)