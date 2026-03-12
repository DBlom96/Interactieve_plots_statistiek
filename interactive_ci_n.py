import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm

st.set_page_config(layout="wide")

# ----------------------------------
# CSS
# ----------------------------------
with open("./styles/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def write_header(text, font_size):
    st.markdown(f'<p style="font-size:{font_size}px;">{text}</p>', unsafe_allow_html=True)

# --------------------------------------------------
# PARAMETERS
# --------------------------------------------------
st.title("Betrouwbaarheidsintervallen voor het populatiegemiddelde (μ)")
with st.sidebar:
    mu = st.number_input("Populatiegemiddelde ($\\mu$)", value=0)
    sigma = st.number_input("Populatiestandaarddeviatie $\\sigma$", min_value=0.01, value=2.0)
    n = st.number_input("Steekproefgrootte $n$", min_value=2, value=30)
    alpha = st.number_input("Significantieniveau $\\alpha$", 0.01, 0.10, 0.05)
    frame_duration = st.number_input("Frame duur (ms)", min_value=100, value=500)
    batch_size = st.number_input("Aantal steekproeven", min_value=1, value=100, max_value=1000)
    generate = st.button("Steekproeven trekken")

st.write("""In deze simulatie worden betrouwbaarheidsintervallen bepaald voor het populatiegemiddelde $\\mu$ van een normale verdeling $N(\\mu = ?, \\sigma)$ met bekende standaardafwijking $\\sigma$.
Als we een steekproef van grootte $n$ trekken uit deze kansverdeling en het steekproefgemiddelde $\\bar{x}$ berekenen, kunnen we een betrouwbaarheidsinterval construeren dat met een bepaalde betrouwbaarheidsniveau (1 - &alpha;) het werkelijke populatiegemiddelde $\\mu$ bevat.
Als we het proces van steekproeftrekking en intervalconstructie herhalen, kunnen we zien dat bij een betrouwbaarheidsniveau van bijvoorbeeld 0.95 (&alpha;=0.05) geldt dat ongeveer 95% van de intervallen het werkelijke populatiegemiddelde $\\mu$ zullen bevatten, wat inzicht geeft in het concept van betrouwbaarheidsintervallen en hun interpretatie.
         
Merk op: normaal gesproken weet je natuurlijk niet wat $\\mu$ is en wil je daarover uitspraken doen op basis van je steekproef. 
In deze simulatie is $\\mu$ echter bekend om het concept van betrouwbaarheidsintervallen en betrouwbaarheidsniveau (1 - &alpha;) beter te kunnen illustreren.""")

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def make_traces_for_frame(intervals, means, contains, current_sample, current_xbar, mu):
    traces = []

    traces.append(go.Scatter(
        x=[0],
        y=[1],
        mode="markers",
        marker=dict(size=9, color="white", opacity=0),
        showlegend=False,
    ))

    traces.append(go.Scatter(
        x=current_sample,
        y=[-1] * len(current_sample),
        mode="markers",
        marker=dict(size=9, color="white"),
        showlegend=False,
    ))

    traces.append(go.Scatter(
        x=[current_xbar],
        y=[-1],
        mode="markers",
        marker=dict(size=14, color="cyan"),
        showlegend=False,
    ))

    for i, (l, r) in enumerate(intervals[:10]):
        if (l, r) == (mu, mu):
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
            traces.append(go.Scatter(
                x=[l, r], y=[i, i], mode="lines",
                line=dict(color=color, width=3),
                showlegend=False,
            ))
            traces.append(go.Scatter(
                x=[means[i]], y=[i], mode="markers",
                marker=dict(size=9, color="cyan"),
                showlegend=False,
            ))

    return traces


def make_stat_card_annotations(count_contains, total, alpha):
    """Four styled stat cards: accent stripe on top + card body."""
    total_miss = total - count_contains
    coverage   = count_contains / total * 100
    expected   = (1 - alpha) * 100

    cards = [
        # dict(x=0.12, label="GETEST",        value=f"{total}",
        #      color="white",  border="#555555"),
        dict(x=0.12, label="BEVAT \u03bc",       value=f"{count_contains} / {total}",
             color="lime",   border="#39ff14"),
        dict(x=0.37, label="BEVAT \u03bc NIET",  value=f"{total_miss} / {total}",
             color="tomato", border="#ff4b4b"),
        dict(x=0.75, label=F"PERCENTAGE (VERWACHT: {expected:.0f}%)", value=f"{coverage:.1f}%",
             color="cyan",   border="#00e5ff")
    ]

    card_annotations = []
    for card in cards:
        # ── Card body ──
        body = (
            f"<span style='font-size:30px;color:#bbb;letter-spacing:5px;padding=5'>{card['label']}</span>"
            f"<br><b><span style='font-size:30px;color:{card['color']}'>{card['value']}</span></b>"
        )
        if "sub" in card:
            body += f"<br><span style='font-size:25px;color:#bbb'>{card['sub']}</span>"

        card_annotations.append(dict(
            x=card["x"], y=1.40,
            xref="paper", yref="paper",
            text=body,
            font=dict(size=30),
            showarrow=False,
            xanchor="center", 
            yanchor="top",
            align="center",
            bgcolor="#1d3557",
            bordercolor=card["border"],
            borderwidth=3,
            borderpad=30
        ))
    return card_annotations


def make_annotations_for_frame(intervals, means, contains, mu, count_contains, total, alpha):
    annotations = []

    # Interval value labels
    for j, (l, r) in enumerate(intervals[:10]):
        if (l, r) == (mu, mu):
            continue
        color = "lime" if contains[j] else "red"
        annotations += [
            dict(x=means[j], y=-j + 0.38, xref="x", text=f"x\u0304={means[j]:.2f}",
                 showarrow=False, font=dict(color="cyan", size=20), xanchor="center", bgcolor=None, bordercolor=None),
            dict(x=l, y=-j + 0.38, text=f"{l:.2f}",
                 showarrow=False, font=dict(color=color, size=20), xanchor="center", bgcolor=None, bordercolor=None),
            dict(x=r, y=-j + 0.38, text=f"{r:.2f}",
                 showarrow=False, font=dict(color=color, size=20), xanchor="center", bgcolor=None, bordercolor=None),
        ]

    # Stat cards
    card_annotations = make_stat_card_annotations(count_contains, total, alpha)
    return annotations + card_annotations


def build_animated_figure(mu, sigma, n, alpha, batch_size, frame_duration):
    z  = norm.ppf(1 - alpha / 2)
    se = sigma / np.sqrt(n)

    x_range = [mu - 4 * sigma, mu + 4 * sigma]
    y_range  = [-4, 10]

    all_samples = [np.random.normal(mu, sigma, n) for _ in range(batch_size)]
    all_xbars   = [s.mean() for s in all_samples]

    intervals_history = [(mu, mu)] * 10
    means_history     = [mu] * 10
    contains_history  = [False] * 10
    count_contains    = 0

    frames = []

    for k in range(batch_size):
        xbar  = all_xbars[k]
        left  = xbar - z * se
        right = xbar + z * se
        hit   = left <= mu <= right
        if hit:
            count_contains += 1

        intervals_history = [(left, right)] + intervals_history[:9]
        means_history     = [xbar] + means_history[:9]
        contains_history  = [hit]  + contains_history[:9]

        total       = k + 1
        traces      = make_traces_for_frame(intervals_history, means_history,
                                            contains_history, all_samples[k], xbar, mu)
        annotations = make_annotations_for_frame(intervals_history, means_history,
                                                  contains_history, mu,
                                                  count_contains, total, alpha)

        if k == 0:
            first_annotations = annotations

        # st.write(annotations)
        frames.append(go.Frame(
            data=traces,
            name=str(k),
            layout=go.Layout(annotations=annotations),
        ))

    fig = go.Figure(
        data=frames[0].data,
        frames=frames,
        layout=go.Layout(
            xaxis=dict(range=x_range, title="Populatiegemiddelde \u03bc", title_font=dict(size=30), tickfont=dict(size=30)),
            yaxis=dict(range=y_range, autorange="reversed", showticklabels=False),
            height=1000,
            margin=dict(t=300),
            annotations=first_annotations,
            shapes=[dict(
                type="line", x0=mu, x1=mu, y0=y_range[0]+2, y1=y_range[1],
                line=dict(color="yellow", dash="dash")
            )],
            updatemenus=[dict(
                type="buttons",
                pad=dict(t=20, r=20, b=20, l=20),
                showactive=False,
                y=-0.25,
                x=0.5,
                xanchor="center",
                direction="left",
                buttons=[
                    dict(
                        label="\u25b6 Speel",
                        method="animate",
                        args=[None, dict(
                            frame=dict(duration=frame_duration, redraw=True),
                            fromcurrent=True,
                            transition=dict(duration=0),
                        )]
                    ),
                    dict(
                        label="\u23f8 Pauze",
                        method="animate",
                        args=[[None], dict(
                            frame=dict(duration=0, redraw=False),
                            mode="immediate",
                            transition=dict(duration=0),
                        )]
                    ),
                ],
                font=dict(
                    size=25,        # Font size for button labels
                ),
            )]
        )
    )

    return fig


# --------------------------------------------------
# RENDER
# --------------------------------------------------

st.subheader(
    f"Berekening van een {(1 - alpha):.0%}-betrouwbaarheidsinterval "
    f"voor het populatiegemiddelde ($\\mu$), gegeven $\\sigma = {sigma}$ en $n={n}$."
)

if generate:
    fig = build_animated_figure(mu, sigma, n, alpha, int(batch_size), frame_duration)
    st.plotly_chart(fig, use_container_width=True, config=dict(displayModeBar=False))
else:
    st.info(f"### Klik op **Steekproeven trekken** in de sidebar om {batch_size} {'steekproeven' if batch_size > 1 else "steekproef"} te trekken van grootte $n={n}$.")