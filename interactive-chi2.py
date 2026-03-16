import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import chi2

from utils.explanation_utils import show_explanation
from utils.streamlit_utils import load_css, css_to_rgba, page_header
from utils.constants import *

st.set_page_config(
    page_title="Visualisatie van de chikwadraatverdeling",
    initial_sidebar_state="expanded",
    layout="wide"
)
# ----------------------------------
# CSS
# ----------------------------------
load_css()

# ----------------------------------
# PARAMETERS
# ----------------------------------

page_header("📊 Chikwadraatverdeling", "Continue kansverdelingen")
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
P_VALUE_COLOR = css_to_rgba(BETA_COLOR, 0.4) # "cyan"
CRITICAL_SHADE_COLOR = css_to_rgba(CRITICAL_COLOR, 0.4)

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=x,
    y=y,
    mode='lines',
    line=dict(color=H0_COLOR),
    showlegend=False
))

if method == "Plot":
    fig.update_layout(
        font=dict(family=FONT_FAMILY, color=PLOT_FONT_COLOR),
        title = dict(
            text=(f"Chikwadraatverdeling met df = {df} {"vrijheidsgraden" if df > 1 else "vrijheidsgraad"}."),
            font=dict(size=TITLE_FONT_SIZE, family=FONT_FAMILY, color=PLOT_FONT_COLOR),
        ),
        xaxis = dict(
            title=dict(text="x", font=dict(size=AXIS_FONT_SIZE)),
            tickfont=dict(size=TICK_FONT_SIZE),    
        ),
        yaxis = dict(
            title=dict(text="Kansdichtheidsfunctie f(x)", font=dict(size=AXIS_FONT_SIZE)),
            tickfont=dict(size=TICK_FONT_SIZE),    
        ),
        height=600
    )

if method == "Kritiek gebied":
    # We toetsen altijd rechtszijdig met de chikwadraattoets.
    grens = chi2.ppf(1 - alpha, df)
    p_waarde = 1 - chi2.cdf(toetsingsgrootheid, df=df)

    mask_acceptable = (x < grens)
    mask_critical = (x >= grens)

    fig.add_trace(go.Scatter(
        x=[toetsingsgrootheid, toetsingsgrootheid],
        y=[0, chi2.pdf(toetsingsgrootheid, df=df)],
        mode='lines',
        line=dict(color=H0_COLOR, dash='dash'),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=[grens, grens],
        y=[0, chi2.pdf(grens, df=df)],
        mode='lines',
        line=dict(color=CRITICAL_COLOR, dash='dash'),
        showlegend=False
    ))

    ytext = -0.2 * max(y)  # Position for the horizontal line
    ylines = 1/2 * ytext

    fig.add_trace(go.Scatter(
        x=[toetsingsgrootheid],
        y=[ylines * 2],
        mode='text',
        marker=dict(color=H0_COLOR, size=ANNOTATION_FONT_SIZE),
        text=r"&#967;<sup>2</sup>",
        textfont=dict(size=ANNOTATION_FONT_SIZE, color=H0_COLOR),
        textposition="top center",
        showlegend=False
    ))

    # Add lines to indicate acceptable and critical intervals
    fig.add_trace(go.Scatter(
        x=[0, grens],
        y=[ylines, ylines],
        mode='lines',
        line=dict(color=ACCEPTABLE_COLOR, width=10),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=[grens, max(x)],
        y=[ylines, ylines],
        mode='lines',
        line=dict(color=CRITICAL_COLOR, width=10),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=[(0 + grens) / 2],
        y=[ylines * 2.5],
        mode='text',
        text='Acceptatiegebied',
        textfont=dict(color=ACCEPTABLE_COLOR, size=ANNOTATION_FONT_SIZE),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=[(grens + max(x)) / 2],
        y=[ylines * 2.5],
        mode='text',
        text='Kritiek gebied',
        textfont=dict(color=CRITICAL_COLOR, size=ANNOTATION_FONT_SIZE),
        showlegend=False
    ))
 
    # -------------------------------
    # STAT CARDS
    # -------------------------------
    
    stat_card_test = f"""
        <div class="stat-card {"kritiek" if toetsingsgrootheid > grens else "acceptatie"}">
            <span class="stat-label">Toetsingsgrootheid</span>
            <span class="stat-value">{toetsingsgrootheid:.4f}</span>
            <span class="stat-desc"></span>
        </div>
    """

    st.markdown(f"""
    <div class="stats-row-3" >
        <div class="stat-card acceptatie">
            <span class="stat-label">Acceptatiegebied</span>
            <span class="stat-value">[0, {grens:.4f}]</span>
            <span class="stat-desc">Kans op redelijke uitkomst (laagste {int(100*(1-alpha))}%)</span>
        </div>
        <div class="stat-card kritiek">
            <span class="stat-label">Kritiek gebied</span>
            <span class="stat-value">({grens:.4f}, &infin;)</span>
            <span class="stat-desc">Kans op extreme hoge uitkomst (top {int(100*alpha)}%)</span>
        </div>
        <div class="stat-card bi">
            <span class="stat-label">Toetsingsgrootheid</span>
            <span class="stat-value">&chi;<sup>2</sup> = {toetsingsgrootheid:.4f}</span>
            <span class="stat-desc">De toetsingsgrootheid ligt {"" if toetsingsgrootheid > grens else "niet"} in het kritieke gebied</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


    fig.update_layout(
        font=dict(family=FONT_FAMILY, color=PLOT_FONT_COLOR),
        title = dict(
            text=f"Chikwadraatverdeling met df = {df} {"vrijheidsgraden" if df > 1 else "vrijheidsgraad"}.<br><sup>&#967;<sup>2</sup> = {toetsingsgrootheid:.4f} ligt in het " + ("kritieke gebied" if toetsingsgrootheid > grens else "acceptatiegebied") + ".</sup>",
            font=dict(size=TITLE_FONT_SIZE, family=FONT_FAMILY, color=PLOT_FONT_COLOR),
        ),
        xaxis = dict(
            title=dict(text="x", font=dict(size=AXIS_FONT_SIZE)),
            tickfont=dict(size=TICK_FONT_SIZE),    
        ),
        yaxis = dict(
            title=dict(text="Kansdichtheidsfunctie f(x)", font=dict(size=AXIS_FONT_SIZE)),
            tickfont=dict(size=TICK_FONT_SIZE),    
        ),
        height=600
    )

if method == "p-waarde":    
    grens = chi2.ppf(1 - alpha, df)
    p_waarde = 1 - chi2.cdf(toetsingsgrootheid, df=df)
    mask = x >= toetsingsgrootheid
    mask_critical = x >= grens

    ytext = -0.2 * max(y)  # Position for the horizontal line
    ylines = 1/2 * ytext

    fig.add_trace(go.Scatter(
        x=[toetsingsgrootheid, toetsingsgrootheid],
        y=[0, chi2.pdf(toetsingsgrootheid, df=df)],
        mode='lines',
        line=dict(color=H0_COLOR, dash='dash'),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=[grens, grens],
        y=[0, chi2.pdf(grens, df=df)],
        mode='lines',
        line=dict(color=CRITICAL_COLOR, dash='dash'),
        showlegend=False
    ))

    # Shade region corresponding to the p-value
    fig.add_trace(go.Scatter(
        x=x[mask],
        y=y[mask],
        mode='lines',
        fill='tozeroy',
        fillcolor=P_VALUE_COLOR,
        opacity=0.3,
        showlegend=False
    ))

    # Draw lines and text for test statistic and critical value
    fig.add_trace(go.Scatter(
        x=[toetsingsgrootheid, toetsingsgrootheid],
        y=[0, chi2.pdf(toetsingsgrootheid, df=df)],
        mode='lines',
        line=dict(color=H0_COLOR, dash='dash', width=3),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=[grens, grens],
        y=[0, chi2.pdf(grens, df=df)],
        mode='lines',
        line=dict(color=CRITICAL_COLOR, dash='dash', width=3),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=[toetsingsgrootheid],
        y=[ytext],
        mode='text',
        marker=dict(color=H0_COLOR, size=10),
        text=r"&#967;<sup>2</sup>",
        textfont=dict(size=AXIS_FONT_SIZE, color=H0_COLOR),
        textposition="top center",
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=x[mask_critical],
        y=y[mask_critical],
        mode='lines',
        fill='tozeroy',
        fillcolor=CRITICAL_SHADE_COLOR,
        showlegend=False
    ))

    fig.update_layout(
        font=dict(family=FONT_FAMILY, color=PLOT_FONT_COLOR),
        title = dict(
            text=f"Chikwadraatverdeling met df = {df} {"vrijheidsgraden" if df > 1 else "vrijheidsgraad"}.",
            font=dict(size=TITLE_FONT_SIZE, family=FONT_FAMILY, color=PLOT_FONT_COLOR),
        ),
        xaxis = dict(
            title=dict(text="x", font=dict(size=AXIS_FONT_SIZE)),
            tickfont=dict(size=TICK_FONT_SIZE),    
        ),
        yaxis = dict(
            title=dict(text="Kansdichtheidsfunctie f(x)", font=dict(size=AXIS_FONT_SIZE)),
            tickfont=dict(size=TICK_FONT_SIZE),    
        ),
        height=600
    )

    # -------------------------------
    # STAT CARDS
    # -------------------------------
    
    st.markdown(f"""
    <div class="stats-row-3" >
        <div class="stat-card bi">
            <span class="stat-label">Toetsingsgrootheid</span>
            <span class="stat-value">&chi;<sup>2</sup> = {toetsingsgrootheid:.4f}</span>
            <span class="stat-desc">De toetsingsgrootheid ligt {"" if p_waarde < alpha else "niet"} in het kritieke gebied</span>
        </div>
        <div class="stat-card pvalue">
            <span class="stat-label">p-waarde</span>
            <span class="stat-value">{p_waarde:.4f}</span>
            <span class="stat-desc">Kans op uitkomst &ge; &chi;<sup>2</sup> = {toetsingsgrootheid:.3f}</span>
        </div>
        <div class="stat-card kritiek">
            <span class="stat-label">Significantieniveau</span>
            <span class="stat-value">{alpha:.4f}</span>
            <span class="stat-desc">Vastgestelde kans op type-I fout (H<sub>0</sub> onterecht verwerpen)</span>
        </div>
        
    </div>
    """, unsafe_allow_html=True)

st.plotly_chart(fig, use_container_width=True, config=dict(displayModeBar=False))

explanation_title = "📚 De chikwadraatverdeling"
explanation_md = fr"""
# 📊 De chikwadraatverdeling

De **$\chi^2$-verdeling** (chikwadraatverdeling) is een verdeling die vooral wordt gebruikt bij toetsen over varianties, onafhankelijkheid tussen twee categorische variabelen en in goodness-of-fit tests.

## 📌 Eigenschappen van de $\chi^2$-verdeling:
- De verdeling is **niet symmetrisch** en altijd **positief** ($\chi^2 \geq 0$)
- De vorm hangt af van het aantal **vrijheidsgraden** (df)
  - Voor kleine waarden van df (weinig vrijheidsgraden), is de verdeling scheef naar rechts.
  - Voor grote waarden van df (veel vrijheidsgraden), benadert de chikwadraatverdeling een normale verdeling.
- De verwachte waarde is gelijk aan df, en de variantie is 2 df

## 🧪 Typische toepassingen:
- Toetsen of een waargenomen variantie afwijkt van een verwachte waarde
- Aanpassingstoets (goodness-of-fit test): in hoeverre komen de gegevens overeen met wat je zou verwachten op basis van een bepaalde (discrete) kansverdeling.
- Onafhankelijkheidstoetsen in kruistabellen: zijn twee categorische (nominale / ordinale) variabelen onafhankelijk van elkaar of niet?

## 🎨 Visualisatie
- Methode **Plot**: de curve toont de grafiek van de kansdichtheidsfunctie van de $\chi^2$-verdeling met df $= {df}$ {"vrijheidsgraad" if df == 1 else "vrijheidsgraden"}.
- Methode **Kritiek gebied**: onder de grafiek worden het acceptatiegebied (groen) en het kritieke gebied (rood) getoond voor chikwadraattoetsen met de bijbehorende chikwadraatverdeling. 
- Methode **p-waarde**: de p-waarde wordt gevisualiseerd als het gearceerde gebied onder de grafiek rechts van de geobserveerde toetsingsgrootheid $\chi^2$.
"""

show_explanation(explanation_title, explanation_md)

