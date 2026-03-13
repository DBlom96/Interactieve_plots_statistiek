import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from scipy.stats import t as t_dist
from sklearn.linear_model import LinearRegression

from utils.explanation_utils import show_explanation
from utils.streamlit_utils import load_css, page_header, css_to_rgba

# ----------------------------------
# PAGE CONFIG
# ----------------------------------

st.set_page_config(
    page_title="Lineaire regressie",
    initial_sidebar_state="expanded",
    layout="wide"
)

# ----------------------------------
# CSS
# ----------------------------------
load_css("./styles/style.css")

# ----------------------------------
# HELPERS
# ----------------------------------

if "points" not in st.session_state:
    st.session_state["points"] = {"x": [], "y": []}

POINT_COLOR      = "cyan"
REGRESSION_COLOR = "springgreen"
RESIDUAL_COLOR   = "tomato"
CI_COLOR         = "gold"
PI_COLOR         = "magenta"
CI_FILL_COLOR    = css_to_rgba(CI_COLOR, 0.25)
PI_FILL_COLOR    = css_to_rgba(PI_COLOR, 0.25)


def compute_intervals(X_flat, y, x_range, alpha):
    """
    Returns CI and PI bounds over x_range.

    CI (confidence interval for E[Y|X=x]):
        ŷ ± t * s * sqrt(1/n + (x - x̄)² / Sxx)

    PI (prediction interval for a new Y given X=x):
        ŷ ± t * s * sqrt(1 + 1/n + (x - x̄)² / Sxx)
    """
    n    = len(X_flat)
    x_mean = np.mean(X_flat)
    Sxx  = np.sum((X_flat - x_mean) ** 2)

    X_mat = np.column_stack([np.ones(n), X_flat])
    beta  = np.linalg.lstsq(X_mat, y, rcond=None)[0]
    y_hat = X_mat @ beta
    SSE   = np.sum((y - y_hat) ** 2)
    s2    = SSE / (n - 2)
    s     = np.sqrt(s2)

    t_crit = t_dist.ppf(1 - alpha / 2, df=n - 2)

    y_pred_range = beta[0] + beta[1] * x_range
    se_mean = s * np.sqrt(1 / n + (x_range - x_mean) ** 2 / Sxx)
    se_pred = s * np.sqrt(1 + 1 / n + (x_range - x_mean) ** 2 / Sxx)

    ci_lower = y_pred_range - t_crit * se_mean
    ci_upper = y_pred_range + t_crit * se_mean
    pi_lower = y_pred_range - t_crit * se_pred
    pi_upper = y_pred_range + t_crit * se_pred

    return ci_lower, ci_upper, pi_lower, pi_upper

# ----------------------------------
# PARAMETERS
# ----------------------------------

page_header("📊 Lineaire regressie", "Statistiek · Visualisatie")

with st.sidebar:
    st.header("Parameters")

    # ----- Excel upload -----
    st.subheader("📂 Bestand uploaden")
    uploaded_file = st.file_uploader(
        "Upload een Excel-bestand met kolommen X en Y",
        type=["xlsx", "xls", "csv"],
        help="Het bestand moet minimaal twee kolommen bevatten met de namen 'X' en 'Y' (hoofdlettergevoelig)."
    )

    if uploaded_file is not None:
        try:
            df_upload = pd.read_csv(uploaded_file)
            if "X" not in df_upload.columns or "Y" not in df_upload.columns:
                st.error("Het bestand moet kolommen met de namen 'X' en 'Y' bevatten.")
            else:
                df_upload = df_upload[["X", "Y"]].dropna()
                st.session_state["points"]["x"] = df_upload["X"].tolist()
                st.session_state["points"]["y"] = df_upload["Y"].tolist()
                st.success(f"{len(df_upload)} datapunten geladen.")
        except Exception as e:
            st.error(f"Fout bij het lezen van het bestand: {e}")

    st.divider()

    # ----- Manual input -----
    st.subheader("✏️ Handmatige invoer")
    point_input = st.text_input("Voer een punt x, y in (voorbeeld: 2.5, 5.1)", value="0.0, 0.0")
    col1, col2 = st.columns(2, vertical_alignment="center")
    add_point_button    = col1.button("➕ Punt toevoegen",         use_container_width=True)
    remove_point_button = col2.button("🗑️ Laatste punt verwijderen", use_container_width=True)

    if add_point_button:
        try:
            x_val, y_val = map(float, point_input.split(","))
            st.session_state["points"]["x"].append(x_val)
            st.session_state["points"]["y"].append(y_val)
        except ValueError:
            st.error("Schrijf het punt als twee getallen gescheiden door een komma. Gebruik een punt voor decimalen.")

    if remove_point_button and st.session_state["points"]["x"]:
        st.session_state["points"]["x"].pop()
        st.session_state["points"]["y"].pop()

    if st.button("🗑️ Alles wissen", use_container_width=True):
        st.session_state["points"] = {"x": [], "y": []}

    st.divider()

    # ----- Interval toggles -----
    st.subheader("📐 Intervallen")
    show_ci = st.toggle(
        "Betrouwbaarheidsinterval voor E[Y|X]",
        value=False,
        help="Toont het interval waarbinnen de gemiddelde Y-waarde voor een gegeven X valt."
    )
    show_pi = st.toggle(
        "Voorspellingsinterval voor Y gegeven X",
        value=False,
        help="Toont het interval waarbinnen een nieuwe individuele Y-waarde voor een gegeven X valt."
    )

    alpha_interval = st.number_input(
        "Significantieniveau α",
        min_value=0.01, max_value=0.20, value=0.05, step=0.01,
        help="Gebruik α = 0.05 voor een 95%-interval. Geldt voor zowel het betrouwbaarheids- als voorspellingsinterval."
    )
    conf_pct = int(100 * (1 - alpha_interval))

# ----------------------------------
# COMPUTATION
# ----------------------------------

xcoords  = st.session_state["points"]["x"]
ycoords  = st.session_state["points"]["y"]
n_points = len(xcoords)

slope, intercept, r_squared = None, None, None

if n_points >= 2:
    X      = np.array(xcoords).reshape(-1, 1)
    y      = np.array(ycoords)
    X_flat = np.array(xcoords)

    model = LinearRegression()
    model.fit(X, y)

    slope       = model.coef_[0]
    intercept   = model.intercept_
    r_squared   = model.score(X, y)
    pearson_r   = np.corrcoef(X_flat, y)[0, 1]

    margin      = max(0.5, 0.15 * (max(xcoords) - min(xcoords)))
    xmin        = min(xcoords) - margin
    xmax        = max(xcoords) + margin
    x_range     = np.linspace(xmin, xmax, 1_000)
    y_pred_line = model.predict(x_range.reshape(-1, 1))
    y_pred_pts  = model.predict(X)

    if (show_ci or show_pi) and n_points >= 3:
        ci_lower, ci_upper, pi_lower, pi_upper = compute_intervals(
            X_flat, y, x_range, alpha_interval
        )

    # Always compute intervals at x_mean when alpha is defined (>= 3 points)
    if n_points >= 3:
        alpha_for_cards = alpha_interval
        x_mean_val = float(np.mean(X_flat))
        ci_lo_mean, ci_hi_mean, pi_lo_mean, pi_hi_mean = compute_intervals(
            X_flat, y, np.array([x_mean_val]), alpha_for_cards
        )
        conf_pct_cards = int(100 * (1 - alpha_for_cards))

# ----------------------------------
# STAT CARDS
# ----------------------------------

if n_points >= 2:
    sign = "+" if intercept >= 0 else "-"

    # Row 1: regression equation + Pearson r
    st.markdown(f"""
    <div class="stats-row-2">
        <div class="stat-card kritiek">
            <span class="stat-label">Regressievergelijking</span>
            <span class="stat-value">Ŷ = {slope:.2f}X {sign} {abs(intercept):.2f}</span>
            <span class="stat-desc">Geschatte lineaire relatie</span>
        </div>
        <div class="stat-card beta">
            <span class="stat-label">Pearson's r</span>
            <span class="stat-value">{pearson_r:.4f}</span>
            <span class="stat-desc">Sterkte en richting van de lineaire samenhang</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Row 2: CI and PI at x_mean — always shown, values filled in when available
    if n_points >= 3:
        ci_label = f"{conf_pct_cards}%-betrouwbaarheidsinterval voor E(Y | X = x&#772;)"
        pi_label = f"{conf_pct_cards}%-voorspellingsinterval voor Y | X = x&#772;"
        ci_value = f"[{ci_lo_mean[0]:.4f},  {ci_hi_mean[0]:.4f}]"
        pi_value = f"[{pi_lo_mean[0]:.4f},  {pi_hi_mean[0]:.4f}]"
        ci_desc  = f"Bij x&#772; = {x_mean_val:.4f} (&alpha; = {alpha_for_cards})"
        pi_desc  = f"Bij x&#772; = {x_mean_val:.4f} (&alpha; = {alpha_for_cards})"
    else:
        ci_label = "Betrouwbaarheidsinterval bij x&#772;"
        pi_label = "Voorspellingsinterval bij x&#772;"
        ci_value = "—"
        pi_value = "—"
        ci_desc  = "Minimaal 3 datapunten nodig"
        pi_desc  = "Minimaal 3 datapunten nodig"

    st.markdown(f"""
    <div class="stats-row-3">
        <div class="stat-card bi">
            <span class="stat-label">{ci_label}</span>
            <span class="stat-value">{ci_value}</span>
            <span class="stat-desc">{ci_desc}</span>
        </div>
        <div class="stat-card pi">
            <span class="stat-label">{pi_label}</span>
            <span class="stat-value">{pi_value}</span>
            <span class="stat-desc">{pi_desc}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------
# PLOTTING
# ----------------------------------

fig = go.Figure()

if n_points == 0:
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="JetBrains Mono, monospace", color="#f1faee"),
        title=dict(
            text="Voeg datapunten toe via de zijbalk.",
            font=dict(size=30, family="JetBrains Mono, monospace", color="#f1faee"),
        ),
        height=600,
        xaxis=dict(title=dict(text="X", font=dict(size=30)), tickfont=dict(size=25), gridcolor="rgba(168,218,220,0.08)", zerolinecolor="rgba(168,218,220,0.15)"),
        yaxis=dict(title=dict(text="Y", font=dict(size=30)), tickfont=dict(size=25), gridcolor="rgba(168,218,220,0.08)", zerolinecolor="rgba(168,218,220,0.15)"),
    )

elif n_points == 1:
    fig.add_trace(go.Scatter(
        x=xcoords, y=ycoords,
        mode="markers",
        marker=dict(color=POINT_COLOR, size=12),
        showlegend=False
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="JetBrains Mono, monospace", color="#f1faee"),
        title=dict(
            text="Voeg minstens twee punten toe voor een regressielijn.", 
            font=dict(size=30, family="JetBrains Mono, monospace", color="#f1faee")),
        height=600,
        xaxis=dict(title=dict(text="X", font=dict(size=30)), tickfont=dict(size=25), gridcolor="rgba(168,218,220,0.08)", zerolinecolor="rgba(168,218,220,0.15)"),
        yaxis=dict(title=dict(text="Y", font=dict(size=30)), tickfont=dict(size=25), gridcolor="rgba(168,218,220,0.08)", zerolinecolor="rgba(168,218,220,0.15)"),
    )

else:
    # Prediction interval band (drawn first so it sits behind everything)
    if show_pi and n_points >= 3:
        fig.add_trace(go.Scatter(
            x=np.concatenate([x_range, x_range[::-1]]),
            y=np.concatenate([pi_upper, pi_lower[::-1]]),
            fill="toself",
            fillcolor=PI_FILL_COLOR,
            line=dict(color=PI_COLOR, width=1, dash="dot"),
            name=f"{conf_pct}% voorspellingsinterval",
            showlegend=False
        ))

    # Confidence interval band
    if show_ci and n_points >= 3:
        fig.add_trace(go.Scatter(
            x=np.concatenate([x_range, x_range[::-1]]),
            y=np.concatenate([ci_upper, ci_lower[::-1]]),
            fill="toself",
            fillcolor=CI_FILL_COLOR,
            line=dict(color=CI_COLOR, width=1, dash="dash"),
            name=f"{conf_pct}% betrouwbaarheidsinterval voor E[Y|X]",
            showlegend=False
        ))

    # Residuals
    for xi, yi, yh in zip(xcoords, ycoords, y_pred_pts):
        fig.add_trace(go.Scatter(
            x=[xi, xi],
            y=[yi, float(yh)],
            mode="lines",
            line=dict(color=RESIDUAL_COLOR, width=1.5, dash="dash"),
            showlegend=False
        ))

    # Regression line
    fig.add_trace(go.Scatter(
        x=x_range, y=y_pred_line,
        mode="lines",
        line=dict(color=REGRESSION_COLOR, width=3),
        name=f"Ŷ = {slope:.2f}X {'+' if intercept >= 0 else '-'} {abs(intercept):.2f}",
        showlegend=False
    ))

    # Data points
    fig.add_trace(go.Scatter(
        x=xcoords, y=ycoords,
        mode="markers",
        marker=dict(color=POINT_COLOR, size=12, line=dict(color="white", width=1)),
        name="Datapunten",
        showlegend=False
    ))

    if (show_ci or show_pi) and n_points < 3:
        st.warning("Minimaal 3 datapunten nodig om intervallen te berekenen.")

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="JetBrains Mono, monospace", color="#f1faee"),
        title=dict(
            text=f"Regressielijn: Ŷ = {slope:.2f}X {'+' if intercept >= 0 else '-'} {abs(intercept):.2f}  |  R² = {r_squared:.4f}",
            font=dict(size=30, family="JetBrains Mono, monospace", color="#f1faee"),
        ),
        height=600,
        xaxis=dict(title=dict(text="X", font=dict(size=30)), tickfont=dict(size=25), gridcolor="rgba(168,218,220,0.08)", zerolinecolor="rgba(168,218,220,0.15)"),
        yaxis=dict(title=dict(text="Y", font=dict(size=30)), tickfont=dict(size=25), gridcolor="rgba(168,218,220,0.08)", zerolinecolor="rgba(168,218,220,0.15)"),
        legend=dict(font=dict(size=18)),
    )

st.plotly_chart(fig, use_container_width=True, config=dict(displayModeBar=False))

# ----------------------------------
# POINTS TABLE
# ----------------------------------

if n_points > 0:
    with st.expander("📋 Lijst met ingevoerde datapunten", expanded=False):
        st.table({"X": xcoords, "Y": ycoords})

# ----------------------------------
# EXPLANATION
# ----------------------------------

explanation_title = "📚 Lineaire regressie"
explanation_md = r"""
# 📊 Lineaire regressie

**Lineaire regressie** is een statistische methode waarmee we de lineaire relatie tussen een onafhankelijke variabele $X$ en een afhankelijke variabele $Y$ modelleren. Het doel is een rechte lijn te vinden die de datapunten zo goed mogelijk beschrijft.

## 📜 Het regressiemodel

De geschatte regressielijn heeft de vorm:

$$
\hat{Y} = b_0 + b_1 X
$$

waarbij:
- $b_0$ het **intercept** is: de verwachte waarde van $\hat{Y}$ wanneer $X = 0$
- $b_1$ de **helling** is: de verandering in $\hat{Y}$ per eenheid toename in $X$

## 🔧 Kleinste-kwadratenmethode

De parameters $b_0$ en $b_1$ worden bepaald met de **kleinste-kwadratenmethode**: we minimaliseren de som van de kwadraten van de residuen (de verticale afstanden tussen de datapunten en de regressielijn):

$$
\min_{b_0, b_1} \sum_{i=1}^{n} \left(y_i - \hat{y}_i\right)^2
$$

De rode stippellijnen in de plot tonen deze residuen.

## 📈 Pearson's correlatieco\"effici\"ent $r$

De **correlatiecoefficient van Pearson** geeft aan in hoeverre er lineaire samenhang is tussen de twee ratiovariabelen $X$ en $Y$:

$$
r^2 = \frac{\bar{xy} - \bar{x}\cdot\bar{y}}{(\bar{y^2} - \bar{y})^2 \cdot (\bar{x^2} - \bar{x}^2)^2}
$$

- $r = -1$: het model heeft een perfecte negatieve lineaire samenhang
- $r = 0$: het model heeft geen lineaire samenhang
- $r = 1$: het model heeft een perfecte positieve lineaire samenhang

## 📐 Betrouwbaarheidsinterval voor E(Y|X)

Het **betrouwbaarheidsinterval** (gouden band) toont de onzekerheid over de *gemiddelde* waarde van $Y$ voor een gegeven $X=x_0$:

$$
\hat{Y} \pm t_{\alpha/2,\, n-2} \cdot s \cdot \sqrt{\frac{1}{n} + \frac{(x_0 - \bar{x})^2}{\sum_{i} (x_i - \bar{x})^2}}
$$

## 🔮 Voorspellingsinterval voor Y gegeven X

Het **voorspellingsinterval** (paarse band) is breder: het toont de onzekerheid over een *individuele nieuwe waarneming* van $Y$ voor een gegeven $X = x_0$:

$$
\hat{Y} \pm t_{\alpha/2,\, n-2} \cdot s \cdot \sqrt{1 + \frac{1}{n} + \frac{(x_0 - \bar{x})^2}{\sum_{i} (x_i - \bar{x})^2}}
$$

Het voorspellingsinterval is altijd breder dan het betrouwbaarheidsinterval (let op de extra 1 onder de wortel), omdat de spreiding steeds kleiner wordt naarmate je naar gemiddeldes van grotere steekproeven kijkt. Uit de centrale limietstelling volgt immers dat steekproefgemiddelden bij benadering normaal verdeeld zijn, maar de standaardafwijking wordt dan gedeeld door de wortel van de steekproefgrootte.
"""

show_explanation(explanation_title, explanation_md)
