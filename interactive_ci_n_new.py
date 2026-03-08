import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm
import time

st.set_page_config(layout="wide")

# --------------------------------------------------
# PARAMETERS
# --------------------------------------------------
st.title("Betrouwbaarheidsintervallen voor het populatiegemiddelde (μ)")
with st.sidebar:
    mu = st.number_input("Populatiegemiddelde &mu;", value=0)
    sigma = st.number_input("Populatiestandaarddeviatie &sigma;", min_value=0.01, value=2.0)
    n = st.number_input("Steekproefgrootte $n$", min_value=2, value=30)
    alpha = st.number_input("Significantieniveau &alpha;", 0.01, 0.10, 0.05)
    frame_duration = st.number_input("Frame duur (ms)", min_value=100, value=500)
    batch_size = st.number_input("Aantal steekproeven", min_value=1, value=100, max_value=1000)
    generate = st.button("Genereer & Animeer")

st.write("""In deze simulatie worden betrouwbaarheidsintervallen bepaald voor het populatiegemiddelde $\\mu$ van een normale verdeling $N(\\mu = ?, \\sigma)$ met bekende standaardafwijking $\\sigma$.
Als we een steekproef van grootte $n$ trekken uit deze kansverdeling en het steekproefgemiddelde $\\bar{x}$ berekenen, kunnen we een betrouwbaarheidsinterval construeren dat met een bepaalde betrouwbaarheidsniveau (1 - &alpha;) het werkelijke populatiegemiddelde $\\mu$ bevat.
Als we het proces van steekproeftrekking en intervalconstructie herhalen, kunnen we zien dat bij een betrouwbaarheidsniveau van bijvoorbeeld 0.95 (&alpha;=0.05) geldt dat ongeveer 95% van de intervallen het werkelijke populatiegemiddelde $\\mu$ zullen bevatten, wat inzicht geeft in het concept van betrouwbaarheidsintervallen en hun interpretatie.
         
Merk op: normaal gesproken weet je natuurlijk niet wat $\\mu$ is en wil je daarover uitspraken doen op basis van je steekproef. In deze simulatie is $\\mu$ echter bekend om het concept van betrouwbaarheidsintervallen en betrouwbaarheidsniveau (1 - &alpha;) beter te kunnen illustreren.""")

# --------------------------------------------------
# SIMULATION STEP
# --------------------------------------------------

z = norm.ppf(1-alpha/2)
se = sigma/np.sqrt(n)

def make_traces_for_frame(intervals, means, contains, current_sample, current_xbar, mu):
    """Return a flat list of Plotly trace dicts for one animation frame."""
    traces = []

    # Trace 0: current sample scatter
    traces.append(go.Scatter(
        x=current_sample,
        y=[-1] * len(current_sample),
        mode="markers",
        marker=dict(size=9, color="white"),
        showlegend=False,
    ))

    # Trace 1: current sample mean
    traces.append(go.Scatter(
        x=[current_xbar],
        y=[-1],
        mode="markers",
        marker=dict(size=14, color="cyan"),
        showlegend=False,
    ))

    # Trace 2 to 21: two traces per interval slot (line + mean marker)
    for i, (l, r) in enumerate(intervals[:10]):
        if (l, r) == (mu, mu):
            # Placeholder - invisible but keeps the trace count stable
            traces.append(go.Scatter(
                x=[mu, mu], y=[i, i], mode="markers",
                marker=dict(size=0, opacity=0),
                showlegend=False,
            ))
            traces.append(go.Scatter(
                x=[mu], y=[i], mode="markers",
                marker=dict(size=0, opacity=0),
                showlegend=False,
            ))
        else:
            color = "lime" if contains[i] else "red"

            # Interval line
            traces.append(go.Scatter(
                x=[l, r], y=[i, i], mode="lines",
                line=dict(color=color, width=3),
                showlegend=False,
            ))

            # Sample mean marker for this interval
            traces.append(go.Scatter(
                x=[means[i]], y=[i], mode="markers",
                marker=dict(size=9, color="cyan"), # cyan to match the current mean style
                showlegend=False,
            ))

    return traces

def make_annotations_for_frame(intervals, means, contains, mu):
    """Three annotations per real interal: lower bound, upper bound, and mean."""
    annotations = []
    for i, (l, r) in enumerate(intervals[:10]):
        if (l, r) == (mu, mu):
            continue  # skip placeholder intervals

        color = "lime" if contains[i] else "red"
        annotations += [
            dict(
                x=means[i], y=i + 0.38,
                text=f"x̄={means[i]:.2f}",
                showarrow=False,
                font=dict(color="cyan", size=10),
                xanchor="center",
            ),
            dict(
                x=l, y=i + 0.38,
                text=f"{l:.2f}",
                showarrow=False,
                font=dict(color=color, size=10),
                xanchor="center",
            ),
            dict(
                x=r, y=i + 0.38,
                text=f"{r:.2f}",
                showarrow=False,
                font=dict(color=color, size=10),
                xanchor="center",
            ),
        ]
    return annotations

def build_animated_figure(mu, sigma, n, alpha, batch_size, frame_duration):
    z = norm.ppf(1 - alpha / 2)
    se = sigma / np.sqrt(n)

    x_range = [mu - 4 * sigma, mu + 4 * sigma]
    y_range = [-2, 10]

    # --- Pre-compute all samples and intervals for the batch ---
    all_samples = [np.random.normal(mu, sigma, n) for _ in range(batch_size)]
    all_xbars = [s.mean() for s in all_samples]

    intervals_history = [(mu, mu)] * 10
    means_history = [mu] * 10
    contains_history = [False] * 10
    count_contains = 0

    frames = []

    for k in range(batch_size):
        xbar = all_xbars[k]
        left = xbar - z * se
        right = xbar + z * se
        hit = left <= mu <= right
        if hit:
            count_contains += 1

        intervals_history = [(left, right)] + intervals_history[:9]
        means_history = [xbar] + means_history[:9]
        contains_history = [hit] + contains_history[:9]

        traces      = make_traces_for_frame(intervals_history, means_history,
                                            contains_history, all_samples[k], xbar, mu)
        annotations = make_annotations_for_frame(intervals_history, means_history,
                                                  contains_history, mu)
        total = k + 1
        coverage = count_contains / total
        title =f"Bevat μ: {count_contains} | Bevat niet μ: {total - count_contains} | Percentage: {coverage * 100:.1f}%"

        if k == 0:
            first_annotations = annotations
            first_title = title

        frames.append(go.Frame(
            data=traces,
            name=str(k),
            layout=go.Layout(
                annotations=annotations,
                title=dict(text=title),
            ),
        ))

    # --- Base figure (first frame as initial state) ---
    fig = go.Figure(
        data=frames[0].data,
        frames=frames,
        layout=go.Layout(
            xaxis=dict(range=x_range, title="Populatiegemiddelde μ"),
            yaxis=dict(range=y_range, autorange="reversed", showticklabels=False),
            height=800,
            annotations=first_annotations,
            shapes=[dict(
                type="line", x0=mu, x1=mu, y0=y_range[0], y1=y_range[1],
                line=dict(color="yellow", dash="dash")
            )],
            title=dict(
                text=first_title,
                font=dict(size=28),
            ),
            updatemenus=[dict(
                type="buttons",
                showactive=False,
                y=-0.25,
                x=0.5,
                xanchor="center",
                direction="left",
                buttons=[
                    dict(
                        label="▶ Speel",
                        method="animate",
                        args=[
                            None,
                            dict(
                                frame=dict(duration=frame_duration, redraw=True),
                                fromcurrent=True,
                                transition=dict(duration=0),
                            )
                        ]
                    ),
                    dict(
                        label="⏸ Pauze",
                        method="animate",
                        args=[
                            [None],
                            dict(
                                frame=dict(duration=0, redraw=False),
                                mode="immediate",
                                transition=dict(duration=0),
                            )
                        ]
                    ),
                ]
            )]
        )
    )

    return fig


# --------------------------------------------------
# RENDER
# --------------------------------------------------

st.subheader(
    f"Berekening van een {(1 - alpha):.0%}-betrouwbaarheidsinterval "
    f"voor het populatiegemiddelde (μ), gegeven σ={sigma} en n={n}."
)

if generate:
    fig = build_animated_figure(mu, sigma, n, alpha, batch_size, frame_duration)
    st.plotly_chart(fig, use_container_width=True, config=dict(displayModeBar=False))
else:
    st.info("Klik op **Genereer & Animeer** in de sidebar om een batch te starten.")