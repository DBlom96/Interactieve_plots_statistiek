import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import chi2
from utils.explanation_utils import show_explanation

st.set_page_config(
    page_title="Visualisatie van de chikwadraatverdeling",
    initial_sidebar_state="expanded",
    layout="wide"
)

# ----------------------------------
# PARAMETERS
# ----------------------------------

st.title("📊 Interactieve plot: de chikwadraatverdeling")
with st.sidebar:
    st.header("Parameters")

    df = st.number_input(label="Aantal vrijheidsgraden (df)", min_value=1, value=5)
    method = st.selectbox(
        label="Selecteer visualisatiemethode", 
        options=["Plot", "Kritiek gebied", "p-waarde"]
    )

    if method != "Plot":
        alpha = st.number_input("Significantieniveau $\\alpha$", min_value=0.001, value=0.05)
        toetsingsgrootheid = st.number_input("Geobserveerde toetsingsgrootheid $\\chi^2$", value=2.0)

# --------------------------------
# SAMPLING
# --------------------------------

def draw_chi2_distribution(df):
    x = np.linspace(0, max(10, df + 5 * np.sqrt(df)), 10_000)
    y = chi2.pdf(x, df)
    return x, y

# --------------------------------
# PLOTTING
# --------------------------------

x, y = draw_chi2_distribution(df)
acceptable_color = "springgreen" # "neongreen"
fill_color = "cyan" # "cyan"
critical_color = "tomato" # "tomato red"

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=x,
    y=y,
    mode='lines',
    line=dict(color=fill_color),
    showlegend=False
))

if method == "Plot":
    fig.update_layout(
        title = dict(
            text=(f"Chikwadraatverdeling met df = {df} {"vrijheidsgraden" if df > 1 else "vrijheidsgraad"}."),
            font=dict(size=40),
        ),
        xaxis = dict(
            title=dict(text="x", font=dict(size=30)),
            tickfont=dict(size=30),    
        ),
        yaxis = dict(
            title=dict(text="Kansdichtheidsfunctie f(x)", font=dict(size=30)),
            tickfont=dict(size=30),    
        ),
        height=800
    )

if method == "Kritiek gebied":
    grens = chi2.ppf(1 - alpha, df)
    p_waarde = 1 - chi2.cdf(toetsingsgrootheid, df=df)

    mask_acceptable = x < grens
    mask_critical = x >= grens

    fig.add_trace(go.Scatter(
        x=[toetsingsgrootheid, toetsingsgrootheid],
        y=[0, chi2.pdf(toetsingsgrootheid, df=df)],
        mode='lines',
        line=dict(color=fill_color, dash='dash'),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=[grens, grens],
        y=[0, chi2.pdf(grens, df=df)],
        mode='lines',
        line=dict(color=critical_color, dash='dash'),
        showlegend=False
    ))

    ytext = -0.2 * max(y)  # Position for the horizontal line
    ylines = 1/2 * ytext

    fig.add_trace(go.Scatter(
        x=[toetsingsgrootheid],
        y=[ytext],
        mode='text',
        marker=dict(color=fill_color, size=10),
        text=r"&#967;<sup>2</sup>",
        textfont=dict(size=30, color=fill_color),
        textposition="top center",
        showlegend=False
    ))

    # Add lines to indicate acceptable and critical intervals
    fig.add_trace(go.Scatter(
        x=[0, grens],
        y=[ylines, ylines],
        mode='lines',
        line=dict(color=acceptable_color, width=10),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=[grens, max(x)],
        y=[ylines, ylines],
        mode='lines',
        line=dict(color=critical_color, width=10),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=[(0 + grens) / 2],
        y=[ylines * 0.5],
        mode='text',
        text='Acceptatiegebied',
        textfont=dict(color=acceptable_color, size=30),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=[(grens + max(x)) / 2],
        y=[ylines * 0.5],
        mode='text',
        text='Kritiek gebied',
        textfont=dict(color=critical_color, size=30),
        showlegend=False
    ))


    fig.update_layout(
        title = dict(
            text=f"Chikwadraatverdeling met df = {df} {"vrijheidsgraden" if df > 1 else "vrijheidsgraad"}. | De geobserveerde toetsingsgrootheid &#967;<sup>2</sup> ligt in het " + ("kritieke gebied" if toetsingsgrootheid > grens else "acceptatiegebied") + ".",
            font=dict(size=30),
        ),
        xaxis = dict(
            title=dict(text="x", font=dict(size=30)),
            tickfont=dict(size=30),    
        ),
        yaxis = dict(
            title=dict(text="Kansdichtheidsfunctie f(x)", font=dict(size=30)),
            tickfont=dict(size=30),    
        ),
        height=800
    )

if method == "p-waarde":    
    grens = chi2.ppf(1 - alpha, df)
    p_waarde = 1 - chi2.cdf(toetsingsgrootheid, df=df)
    mask = x >= toetsingsgrootheid

    fig.add_trace(go.Scatter(
        x=[toetsingsgrootheid, toetsingsgrootheid],
        y=[0, chi2.pdf(toetsingsgrootheid, df=df)],
        mode='lines',
        line=dict(color=fill_color, dash='dash'),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=[grens, grens],
        y=[0, chi2.pdf(grens, df=df)],
        mode='lines',
        line=dict(color=critical_color, dash='dash'),
        showlegend=False
    ))

    ytext = -0.2 * max(y)  # Position for the horizontal line
    ylines = 1/2 * ytext

    fig.add_trace(go.Scatter(
        x=[toetsingsgrootheid, toetsingsgrootheid],
        y=[0, chi2.pdf(toetsingsgrootheid, df=df)],
        mode='lines',
        line=dict(color=fill_color, dash='dash'),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=[grens, grens],
        y=[0, chi2.pdf(grens, df=df)],
        mode='lines',
        line=dict(color=critical_color, dash='dash'),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=[toetsingsgrootheid],
        y=[ytext],
        mode='text',
        marker=dict(color=fill_color, size=10),
        text=r"&#967;<sup>2</sup>",
        textfont=dict(size=30, color=fill_color),
        textposition="top center",
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=[grens],
        y=[ytext],
        mode='text',
        marker=dict(color=critical_color, size=10),
        text="g",
        textfont=dict(size=30, color=critical_color),
        textposition="top center",
        showlegend=False
    ))

    # Add lines to indicate acceptable and critical intervals
    fig.add_trace(go.Scatter(
        x=x[mask],
        y=y[mask],
        mode='lines',
        fill='tozeroy',
        fillcolor=fill_color,
        opacity=0.3
    ))

    fig.update_layout(
        title = dict(
            text=f"Chikwadraatverdeling met df = {df} {"vrijheidsgraden" if df > 1 else "vrijheidsgraad"}. | De p-waarde behorende bij de geobserveerde toetsingsgrootheid &#967;<sup>2</sup> is gelijk aan {p_waarde:.4f}.",
            font=dict(size=30),
        ),
        xaxis = dict(
            title=dict(text="x", font=dict(size=30)),
            tickfont=dict(size=30),    
        ),
        yaxis = dict(
            title=dict(text="Kansdichtheidsfunctie f(x)", font=dict(size=30)),
            tickfont=dict(size=30),    
        ),
        height=800
    )

st.plotly_chart(fig, use_container_width=True, config=dict(displayModeBar=False))

explanation_title = "📚 De chikwadraatverdeling"
explanation_md = fr"""
### 📊 De chikwadraatverdeling

De **$\chi^2$-verdeling** (chikwadraatverdeling) is een verdeling die vooral wordt gebruikt bij toetsen over varianties, onafhankelijkheid tussen twee categorische variabelen en in goodness-of-fit tests.

### 📌 Eigenschappen van de $\chi^2$-verdeling:
- De verdeling is **niet symmetrisch** en altijd **positief**: $x \geq 0$
- De vorm hangt af van het aantal **vrijheidsgraden** df
  - In het geval dat df klein is (weinig vrijheidsgraden), is de verdeling scheef naar rechts.
  - In het geval dat df groot is (veel vrijheidsgraden), benadert de chikwadraatverdeling een normale verdeling.
- De verwachte waarde is gelijk aan df, en de variantie is 2 df

### 🧪 Typische toepassingen:
- Toetsen of een waargenomen variantie afwijkt van een verwachte waarde
- Goodness-of-fit toets: komt een verdeling overeen met een verwachte verdeling?
- Onafhankelijkheidstoetsen in kruistabellen: zijn twee categorische variabelen onafhankelijk van elkaar of niet?

### 🎨 Visualisatie
- Methode **Plot**: de curve toont de grafiek van de kansdichtheidsfunctie van de $\chi^2$-verdeling met df $= {df}$ {"vrijheidsgraad" if df == 1 else "vrijheidsgraden"}.
- Methode **Kritiek gebied**: onder de grafiek worden het acceptatiegebied (groen) en het kritieke gebied (rood) getoond voor chikwadraattoetsen met de bijbehorende chikwadraatverdeling. 
- Methode **p-waarde**: de p-waarde wordt gevisualiseerd als het gearceerde gebied onder de grafiek rechts van de geobserveerde toetsingsgrootheid &#967;<sup>2</sup>.
"""

show_explanation(explanation_title, explanation_md)

