import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm
import time

st.set_page_config(layout="wide")

# MathJax laden
st.markdown(
"""
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
""",
unsafe_allow_html=True
)

# --------------------------------------------------
# PARAMETERS
# --------------------------------------------------

with st.sidebar:
    mu = st.slider("Populatiegemiddelde &mu;",50.0,100.0,73.0)
    sigma = st.slider("Populatiestandaarddeviatie &sigma;",1.0,20.0,8.0)
    n = st.slider("Steekproefgrootte $n$",2,100,30)
    alpha = st.slider("Significantieniveau &alpha;",0.01,0.10,0.05)

    speed = st.slider("Simulatiesnelheid",0.05,1.0,0.35)

    col1, col2, col3 = st.columns(3)
    with col1:
        start = st.button("Start")
    with col2:
        pause = st.button("Pauze")
    with col3:
        reset = st.button("Reset")

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "running" not in st.session_state:
    st.session_state.running = False

if "phase" not in st.session_state:
    st.session_state.phase = 0

if "intervals" not in st.session_state:
    st.session_state.intervals = [(mu,mu) for _ in range(10)]

if "means" not in st.session_state:
    st.session_state.means = [mu for _ in range(10)]

if "contains" not in st.session_state:
    st.session_state.contains = [False for _ in range(10)]

if "sample" not in st.session_state:
    st.session_state.sample = None

if "count_contains" not in st.session_state:
    st.session_state.count_contains = 0

if "count_miss" not in st.session_state:
    st.session_state.count_miss = 0

if start:
    st.session_state.running = True

if pause:
    st.session_state.running = False

if reset:
    st.session_state.running = False
    st.session_state.intervals = [(mu,mu) for _ in range(10)]
    st.session_state.means = [mu for _ in range(10)]
    st.session_state.contains = [False for _ in range(10)]
    st.session_state.phase = 0
    st.session_state.count_contains = 0
    st.session_state.count_miss = 0


# --------------------------------------------------
# SIMULATION STEP
# --------------------------------------------------

z = norm.ppf(1-alpha/2)
se = sigma/np.sqrt(n)

if st.session_state.running:

    if st.session_state.phase == 0:

        # nieuwe steekproef
        st.session_state.sample = np.random.normal(mu,sigma,n)
        st.session_state.xbar = np.mean(st.session_state.sample)

    elif st.session_state.phase == 2:

        xbar = st.session_state.xbar

        left = xbar - z*se
        right = xbar + z*se

        contains = left <= mu <= right
        if contains:
            st.session_state.count_contains += 1
        else:
            st.session_state.count_miss += 1

        st.session_state.intervals.insert(0,(left,right))
        st.session_state.means.insert(0,xbar)
        st.session_state.contains.insert(0,contains)

        st.session_state.intervals = st.session_state.intervals[:10]
        st.session_state.means = st.session_state.means[:10]
        st.session_state.contains = st.session_state.contains[:10]

    st.session_state.phase = (st.session_state.phase + 1) % 3


# --------------------------------------------------
# PLOT
# --------------------------------------------------

fig = go.Figure()

x_range = [mu-4*sigma, mu+4*sigma]
y_range = [-2,10]

fig.update_xaxes(range=x_range,title=r'Populatiegemiddelde &mu;')
fig.update_yaxes(range=y_range,autorange="reversed",showticklabels=False)

fig.add_vline(x=mu,line_dash="dash",line_color="yellow")

# sample points
if st.session_state.phase == 1 and st.session_state.sample is not None:
    fig.add_trace(
        go.Scatter(
            x=st.session_state.sample,
            y=[-1]*len(st.session_state.sample),
            mode="markers",
            marker=dict(size=9,color="white"),
            showlegend=False
        )
    )

# sample mean
if st.session_state.phase >= 2 and st.session_state.sample is not None:

    fig.add_trace(
        go.Scatter(
            x=[st.session_state.xbar],
            y=[-1],
            mode="markers",
            marker=dict(size=14,color="cyan"),
            showlegend=False
        )
    )

# intervals
for i, (l,r) in enumerate(st.session_state.intervals):
    if st.session_state.intervals[i] != (mu,mu):

        color = "lime" if st.session_state.contains[i] else "red"

        fig.add_trace(
            go.Scatter(
                x=[l,r],
                y=[i,i],
                mode="lines",
                line=dict(color=color,width=5),
                showlegend=False
            )
        )

        fig.add_trace(
            go.Scatter(
                x=[st.session_state.means[i]],
                y=[i],
                mode="markers",
                marker=dict(color="white",size=9),
                showlegend=False
            )
        )
    else:
        fig.add_trace(
            go.Scatter(
                x=[st.session_state.means[i]],
                y=[i],
                mode="markers",
                marker=dict(color="white",opacity=0,size=9),
                showlegend=False
            )
        )

    if st.session_state.intervals[i] != (mu,mu):
        fig.add_annotation(
            x=st.session_state.means[i],
            y=i+0.3,
            text=f"x̄={st.session_state.means[i]:.2f}",
            showarrow=False,
            font=dict(color="cyan")
        )
        fig.add_annotation(
            x=l,
            y=i-0.3,
            text=f"{l:.2f}",
            showarrow=False,
            font=dict(color=color)
        )
        fig.add_annotation(
            x=r,
            y=i-0.3,
            text=f"{r:.2f}",
            showarrow=False,
            font=dict(color=color)
        )

# Update layout
total = st.session_state.count_contains + st.session_state.count_miss

coverage = st.session_state.count_contains / total if total > 0 else 0

suptitle = f"Berekening van een {(1-alpha):.0%}-betrouwbaarheidsinterval voor het populatiegemiddelde ($\\mu$), gegeven $\\sigma={sigma}$ en $n={n}$."
    
st.subheader(suptitle)

st.write(
    """In deze interactieve plot wordt het betrouwbaarheidsinterval bepaald voor de populatiegemiddelde $\\mu$ van een normale verdeling met bekende standaardafwijking $\\sigma$.
        Hierbij wordt gekeken voor welke mogelijke waardes voor $\\mu$ het waargenomen steekproefgemiddelde binnen het voorspellingsinterval valt.
        De paarse normale verdeling correspondeert met de laagst mogelijke waarde van $\\mu$ waarvoor $\\bar{x}$ in het voorspellingsinterval ligt.
        de groene normale verdeling correspondeert met de hoogst mogelijke waarde van $\\mu$ waarvoor $\\bar{x}$ in het voorspellingsinterval ligt.
    """       
)

fig.update_layout(
    title=f"Bevat &mu;: {st.session_state.count_contains} | Bevat niet &mu;: {st.session_state.count_miss} | Percentage: {coverage*100:.1f}%",
    title_font=dict(size=40),
    # subtitle=f"Laatste 10 steekproeven",
    height=600
)

st.plotly_chart(fig,use_container_width=True)


# --------------------------------------------------
# LOOP
# --------------------------------------------------

if st.session_state.running:

    time.sleep(speed)
    st.rerun()