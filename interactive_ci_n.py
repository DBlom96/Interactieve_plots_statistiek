import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm
from collections import deque

from utils.streamlit_utils import load_css, page_header
from utils.explanation_utils import show_explanation
from utils.constants import *

st.set_page_config(
    page_title="Betrouwbaarheidsintervallen voor het populatiegemiddelde",
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
page_header("📊 Betrouwbaarheidsintervallen", "Schatten · Populatiegemiddelde μ")

with st.sidebar:
    st.header("Parameters")
    mu             = st.number_input(r"Populatiegemiddelde $\mu$:", value=0)
    sigma          = st.number_input(r"Populatiestandaardafwijking $\sigma$:", min_value=0.01, value=2.0)
    n              = st.number_input(r"Steekproefgrootte $n$:", min_value=2, value=30)
    alpha          = st.number_input(r"Significantieniveau $\alpha$:", min_value=0.01, max_value=0.10, value=0.05)
    frame_duration = st.number_input("Frame duur (ms):", min_value=100, value=500)
    batch_size     = st.number_input("Aantal steekproeven:", min_value=1, max_value=1000, value=100)
    generate       = st.button("Steekproeven trekken")

st.markdown(f"""
In deze simulatie worden betrouwbaarheidsintervallen bepaald voor het populatiegemiddelde
$\\mu$ van $N(\\mu, \\sigma)$ met bekende $\\sigma$. Bij een betrouwbaarheidsniveau van
$1 - \\alpha = {(1 - alpha):.2f}$ verwachten we dat ongeveer **{(1 - alpha):.0%} van de intervallen**
het werkelijke populatiegemiddelde $\\mu$ bevat.

> **Let op:** in de praktijk is $\\mu$ onbekend en is het hele idee van betrouwbaarheidsinterval dat we met een bepaalde mate van zekerheid iets over $\\mu$ willen kunnen zeggen.
Als we data verzamelen, gaan we er echter vanuit dat er een echte $\\mu$ bestaat en dat de data uit een normale verdeling komt met dat gemiddelde $\\mu$.
Hier is $\\mu$ bekend om het concept van betrouwbaarheidsintervallen te illustreren.
""")

# ----------------------------------
# HELPERS
# ----------------------------------
def make_traces(intervals, means, contains, sample, xbar, mu):
    traces = []

    # Invisible anchor to fix axis range
    traces.append(go.Scatter(
        x=[mu - 4 * sigma, mu + 4 * sigma], y=[1, 1],
        mode="markers", marker=dict(opacity=0), showlegend=False,
    ))

    # Raw sample observations
    traces.append(go.Scatter(
        x=sample, y=[-1] * len(sample),
        mode="markers", marker=dict(size=8, color=OBSERVATION_COLOR),
        showlegend=False,
    ))

    # Current sample mean
    traces.append(go.Scatter(
        x=[xbar], y=[-1],
        mode="markers", marker=dict(size=14, color=SAMPLE_MEAN_COLOR),
        showlegend=False,
    ))

    # Last 10 confidence intervals
    for i, (l, r) in enumerate(intervals):
        if (l, r) == (mu, mu):       # placeholder — not yet drawn
            traces += [
                go.Scatter(x=[mu, mu], y=[i, i], mode="markers",
                           marker=dict(size=0, opacity=0), showlegend=False),
                go.Scatter(x=[mu], y=[i], mode="markers",
                           marker=dict(size=0, opacity=0), showlegend=False),
            ]
        else:
            color = ACCEPTABLE_COLOR if contains[i] else CRITICAL_COLOR
            traces += [
                go.Scatter(x=[l, r], y=[i, i], mode="lines",
                           line=dict(color=color, width=3), showlegend=False),
                go.Scatter(x=[means[i]], y=[i], mode="markers",
                           marker=dict(size=9, color=SAMPLE_MEAN_COLOR), showlegend=False),
            ]
    return traces


def make_annotations(intervals, means, contains, mu):
    annotations = []
    for j, (l, r) in enumerate(intervals):
        if (l, r) == (mu, mu):
            continue
        if j == 1:
            break
        color = ACCEPTABLE_COLOR if contains[j] else CRITICAL_COLOR
        annotations += [
            dict(x=means[j], y=j + 0.40, xanchor="center", xref="x", yref="y",
                 text=f"{means[j]:.2f}", showarrow=False,
                 font=dict(color=SAMPLE_MEAN_COLOR, size=10+ANNOTATION_FONT_SIZE,
                           family=FONT_FAMILY)),
            dict(x=l, y=j + 0.40, xref="x",  xanchor="right",
                 text=f"{l:.2f}", showarrow=False,
                 font=dict(color=color, size=10+ANNOTATION_FONT_SIZE,
                           family=FONT_FAMILY)),
            dict(x=r, y=j + 0.40, xref="x",  xanchor="left",
                 text=f"{r:.2f}", showarrow=False,
                 font=dict(color=color, size=10+ANNOTATION_FONT_SIZE, 
                           family=FONT_FAMILY)),
        ]
    return annotations

@st.cache_data
def build_figure(mu, sigma, n, alpha, batch_size, frame_duration):
    z  = norm.ppf(1 - alpha / 2)
    se = sigma / np.sqrt(n)
    num_intervals = 10

    all_samples = [np.random.normal(mu, sigma, n) for _ in range(batch_size)]
    all_xbars   = np.array([s.mean() for s in all_samples])
    lefts = all_xbars - z * se
    rights = all_xbars + z * se
    hits = (lefts <= mu) & (mu <= rights)
    count_contains = hits.cumsum()[-1]

    intervals_history = deque([(mu, mu)] * num_intervals, maxlen=num_intervals)
    means_history     = deque([mu]       * num_intervals, maxlen=num_intervals)
    contains_history  = deque([False]    * num_intervals, maxlen=num_intervals)

    frames = []

    for k in range(batch_size):
        xbar  = all_xbars[k]

        intervals_history.appendleft((lefts[k], rights[k]))
        means_history.appendleft(xbar)
        contains_history.appendleft(hits[k])

        traces      = make_traces(intervals_history, means_history,
                                  contains_history, all_samples[k], xbar, mu)
        annotations = make_annotations(intervals_history, means_history,
                                       contains_history, mu)

        frames.append(go.Frame(
            data=traces,
            name=str(k),
            layout=go.Layout(annotations=annotations),
        ))

    fig = go.Figure(
        data=frames[0].data,
        frames=frames,
        layout=go.Layout(
            font=dict(family=FONT_FAMILY, color=PLOT_FONT_COLOR),
            xaxis=dict(
                range=[mu - 4 * sigma, mu + 4 * sigma],
                title=dict(text=r"x", font=dict(size=2*AXIS_FONT_SIZE)),
                tickfont=dict(size=2*TICK_FONT_SIZE),
            ),
            yaxis=dict(
                range=[-4, 10],
                autorange="reversed",
                tickfont=dict(size=2*TICK_FONT_SIZE),
                showticklabels=False,
            ),
            height=700,
            annotations=frames[0].layout.annotations,
            shapes=[dict(
                type="line",
                x0=mu, x1=mu, y0=-3, y1=9,
                line=dict(color=H0_COLOR, dash="dash", width=1.5),
            )],
            updatemenus=[dict(
                type="buttons",
                pad=dict(t=20, r=20, b=20, l=20),
                showactive=False,
                y=0.15, x=0.95,
                xanchor="center",
                direction="left",
                font=dict(size=BUTTON_FONT_SIZE, family=FONT_FAMILY),
                buttons=[
                    dict(
                        label="▶ Speel",
                        method="animate",
                        args=[None, dict(
                            frame=dict(duration=frame_duration, redraw=True),
                            fromcurrent=True,
                            transition=dict(duration=0),
                        )],
                    ),
                    dict(
                        label="⏸ Pauze",
                        method="animate",
                        args=[[None], dict(
                            frame=dict(duration=0, redraw=False),
                            mode="immediate",
                            transition=dict(duration=0),
                        )],
                    ),
                ],
            )],
        ),
    )

    return fig, count_contains


# ----------------------------------
# RENDER
# ----------------------------------
conf_pct = int((1 - alpha) * 100)
st.subheader(
    f"{conf_pct}%-betrouwbaarheidsinterval voor $\\mu$, gegeven $\\sigma={sigma}$ en $n={n}$."
)

if generate:
    fig, count_contains = build_figure(mu, sigma, n, alpha, int(batch_size), frame_duration)
    total      = int(batch_size)
    total_miss = total - count_contains
    coverage   = count_contains / total * 100

    st.markdown(f"""
    <div class="stats-row-3">
      <div class="stat-card acceptatie">
        <span class="stat-label">Bevat {to_lowercase(MEAN_HTML)}</span>
        <span class="stat-value">{count_contains} / {total}</span>
        <span class="stat-desc">Verwacht: {conf_pct}%</span>
      </div>
      <div class="stat-card kritiek">
        <span class="stat-label">Bevat niet {to_lowercase(MEAN_HTML)}</span>
        <span class="stat-value">{total_miss} / {total}</span>
        <span class="stat-desc">Verwacht: {int(alpha * 100)}%</span>
      </div>
      <div class="stat-card beta">
        <span class="stat-label">Werkelijk percentage</span>
        <span class="stat-value">{coverage:.1f}%</span>
        <span class="stat-desc">Verwacht: {conf_pct}%</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.plotly_chart(fig, use_container_width=True, config=dict(displayModeBar=False))

else:
    n_label = f"$n={n}$" if batch_size == 1 else f"$n={n}$"
    amount  = "1 steekproef" if batch_size == 1 else f"{batch_size} steekproeven"
    st.info(f"Klik op **Steekproeven trekken** in de sidebar om {amount} te trekken van grootte {n_label}.")

# ----------------------------------
# EXPLANATION
# ----------------------------------
explanation_title = "📚 Betrouwbaarheidsintervallen"
explanation_markdown = r"""
## 📜 Wat is een betrouwbaarheidsinterval?

Een **betrouwbaarheidsinterval** (ook wel als **confidence interval**) is een interval dat — bij herhaalde steekproeftrekking — met
een bepaalde kans $1 - \alpha$ het werkelijke populatiegemiddelde $\mu$ bevat.

Bij bekende $\sigma$ wordt het $(1-\alpha)$-betrouwbaarheidsinterval voor $\mu$ gegeven door:

$$
    \bar{X} \pm z_{\alpha/2} \cdot \frac{\sigma}{\sqrt{n}}
$$

waarbij $z_{\alpha/2}$ de kritieke grenswaarde is waarvoor bij een standaardnormaal verdeelde kansvariabele $Z \sim N(0, 1)$ geldt dat
$$
    P(Z \ge z_{\alpha/2}) = \alpha/2.
$$

Merk op dat de grenzen van een betrouwbaarheidsinterval ook kansvariabelen zijn (omdat het steekproefgemiddelde $\bar{X}$ een kansvariabele is)! 
Zodra je een steekproef hebt getrokken, kun je een realisatie van deze grenzen bepalen aan de hand van het geobserveerde steekproefgemiddelde $\bar{x}$:

$$
    \bar{x} \pm z_{\alpha/2} \cdot \frac{\sigma}{\sqrt{n}}.
$$

## ⚠️ Veelgemaakte misvatting

In wetenschappelijke literatuur zie je geregeld dat er bijvoorbeeld een 95%-betrouwbaarheidsinterval wordt gerapporteerd.
Dit is een realisatie van de kansvariabele gebaseerd op de steekproefdata die is verzameld in het onderzoek.

Vaak wordt dit als volgt geïnterpreteerd: met kans $0.95$ valt het echte populatiegemiddelde $\mu$ in *dit specifieke interval*.
Dit is echter niet juist: omdat $\mu$ en de grenzen van het gerapporteerde interval vaststaande getallen zijn, is er geen sprake van onzekerheid.
Het gerapporteerde interval bevat $\mu$ wel of niet.
De concepten "onbekendheid" en "onzekerheid" zijn dus subtiel verschillend en worden om die reden ook vaak met elkaar verward.

De correcte interpretatie is: als we heel vaak achter elkaar een steekproef trekken en het bijbehorende betrouwbaarheidsinterval opstellen, zal **95% van de zo
geconstrueerde intervallen** $\mu$ bevatten.
Dit komt op hetzelfde neer als dat de kans dat een **arbitrair gekozen steekproef** het echte populatiegemiddelde $\mu$ bevat is $1 - \alpha = 0.95$.

$$
    P(\bar{X} - z_{\alpha/2} \cdot \frac{\sigma}{\sqrt{n}} \leq \mu \leq \bar{X} + z_{\alpha/2} \cdot \frac{\sigma}{\sqrt{n}}) = 0.95.
$$

## 🔢 Invloed van de parameters

- **Grotere $n$**: smaller interval (meer precisie).
- **Grotere $\sigma$**: breder interval (meer spreiding in de populatie).
- **Kleinere $\alpha$**: breder interval (hogere betrouwbaarheid vereist een groter net).
"""

show_explanation(explanation_title, explanation_markdown)