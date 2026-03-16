import streamlit as st
import numpy as np
import plotly.graph_objects as go

from scipy.stats import norm, t
from utils.explanation_utils import show_explanation
from utils.streamlit_utils import load_css, css_to_rgba, page_header
from utils.constants import *

# ----------------------------------
# PAGE CONFIG
# ----------------------------------    

st.set_page_config(
    page_title="Visualisatie van Student's t-verdeling",
    initial_sidebar_state="expanded",
    layout="wide"
)
# ----------------------------------
# CSS
# ----------------------------------
load_css()



# ----------------------------------
# HELPERS
# ----------------------------------

# ----------------------------------
# PARAMETERS
# ----------------------------------
page_header("📊 Student's t-verdeling", "Continue kansverdelingen")

with st.sidebar:
    st.header("Parameters")

    df = st.number_input(
        label="Aantal vrijheidsgraden (df):",
        min_value=1,
        max_value=100,
        value=1,
        step=1
    )
    alpha = st.number_input(
        label="Significantieniveau ($\\alpha$):",
        min_value=1e-6,
        value=0.05,
        max_value=1.0
    )

# ----------------------------------
# COMPUTATION
# ----------------------------------
confidence = 1 - alpha
conf_pct   = int(100 * confidence)
xmin, xmax = -4, 4
x          = np.linspace(xmin, xmax, 1_000)
normal_pdf = norm.pdf(x, loc=0, scale=1)
t_pdf      = t.pdf(x, df=df)
z_crit     = norm.ppf(1 - alpha / 2)
t_crit     = t.ppf(1 - alpha / 2, df=df)

# ----------------------------------
# STAT CARDS
# ----------------------------------
st.markdown(f"""
<div class="stats-row-3">
  <div class="stat-card bi">
    <span class="stat-label">Kritieke waarden N(0,1)</span>
    <span class="stat-value bi">&plusmn;{z_crit:.4f}</span>
    <span class="stat-desc">{conf_pct}%-betrouwbaarheidsinterval</span>
  </div>
  <div class="stat-card pi">
    <span class="stat-label">Kritieke waarden t(df={df})</span>
    <span class="stat-value pi">&plusmn;{t_crit:.4f}</span>
    <span class="stat-desc">{conf_pct}%-betrouwbaarheidsinterval</span>
  </div>
  <div class="stat-card beta">
    <span class="stat-label">Verschil kritieke waarden</span>
    <span class="stat-value beta">{t_crit - z_crit:.4f}</span>
    <span class="stat-desc">t-verdeling heeft bredere staarten</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------
# PLOT
# ----------------------------------
FILL_OPACITY = 0.15

fig = go.Figure()

# ── Shaded tails: normal ──
mask_tail_normal_left = (x < -z_crit)
mask_tail_normal_right = (x > z_crit)
for mask in [mask_tail_normal_left, mask_tail_normal_right]:
    fig.add_trace(go.Scatter(
        x=x[mask], 
        y=normal_pdf[mask],
        fill="tozeroy",
        fillcolor=css_to_rgba(H0_COLOR, alpha=FILL_OPACITY),
        showlegend=False,
    ))

# ── Shaded tails: t ──
mask_tail_t_left = (x < -t_crit)
mask_tail_t_right = (x > t_crit)
for mask in [mask_tail_t_left, mask_tail_t_right]:
    fig.add_trace(go.Scatter(
        x=x[mask], y=t_pdf[mask],
        fill="tozeroy",
        fillcolor=css_to_rgba(H1_COLOR, alpha=FILL_OPACITY),
        showlegend=False,
    ))

# ── Critical value lines: normal ──
for xv in [-z_crit, z_crit]:
    fig.add_trace(go.Scatter(
        x=[xv, xv], y=[0, norm.pdf(xv)],
        mode="lines",
        line=dict(color=H0_COLOR, width=1.5, dash="dash"),
        showlegend=False,
        hoverinfo="skip",
    ))

# ── Critical value lines: t (only when df >= 3 to avoid very wide tails) ──
if df >= 3:
    for xv in [-t_crit, t_crit]:
        fig.add_trace(go.Scatter(
            x=[xv, xv], y=[0, t.pdf(xv, df=df)],
            mode="lines",
            line=dict(color=H1_COLOR, width=1.5, dash="dash"),
            showlegend=False, 
            hoverinfo="skip",
        ))

# ── Normal distribution curve ──
fig.add_trace(go.Scatter(
    x=x, y=normal_pdf,
    mode="lines",
    line=dict(color=H0_COLOR, width=2.5),
    name="Normale verdeling N(0,1)",
    showlegend=False
))

# ── t-distribution curve ──
t_label = f"t-verdeling (df={df})"
fig.add_trace(go.Scatter(
    x=x, y=t_pdf,
    mode="lines",
    line=dict(color=H1_COLOR, width=2.5),
    name=t_label,
    showlegend=False
))

# ── Layout ──
df_label = f"{df} {"vrijheidsgraad" if df == 1 else "vrijheidsgraden"}"
fig.update_layout(
    font=dict(family=FONT_FAMILY, color=PLOT_FONT_COLOR),
    title=dict(
        text=f"Kansdichtheidsfuncties van N(0,1) en t(df={df})",
        font=dict(size=TITLE_FONT_SIZE, family=FONT_FAMILY, color=PLOT_FONT_COLOR),
        x=0.03,
    ),
    xaxis=dict(
        title="x",
        range=[xmin, xmax],
        title_font=dict(size=AXIS_FONT_SIZE),
        tickfont=dict(size=TICK_FONT_SIZE),
        zerolinecolor="#cccccc",
    ),
    yaxis=dict(
        title="Kansdichtheid f(x)",
        title_font=dict(size=AXIS_FONT_SIZE),
        tickfont=dict(size=TICK_FONT_SIZE)
    ),
    height=600,
    hovermode="x unified",
    margin=dict(t=60, b=40, l=60, r=30),
)

st.plotly_chart(fig, use_container_width=True, config=dict(displayModeBar=False))

# ----------------------------------
# UITLEG
# ----------------------------------

explanation_title = "📚 Student's $t$-verdeling"
explanation_md = f"""
# 📊 Student's $t$-verdeling

Deze interactieve webapp toont een vergelijking tussen de standaardnormale verdeling $N(0,1)$ en Student's $t$-verdeling met verschillende aantallen vrijheidsgraden (df = degrees of freedom).

## 📌 Wat laat de grafiek zien?
De $t$-verdeling ontstaat wanneer je het gemiddelde van een steekproef wilt vergelijken met een populatiegemiddelde, maar de **populatiestandaardafwijking $\sigma$ onbekend** is.
Je schat $\\sigma$ dan met de steekproefstandaardafwijking $s$ en die schatting bevat zelf ook weer onzekerheid omdat we met een steekproef werken.

Die extra onzekerheid vertaalt zich direct naar een kansverdeling met **dikkere staarten**, oftewel een kansverdeling die breder is en waarbij extreme uitkomsten waarschijnlijker zijn dan in de standaardnormale verdeling.
Hoe kleiner de steekproefgrootte $n$, hoe kleiner het aantal vrijheidsgraden ($n-1$) en dus hoe groter de onzekerheid en hoe dikker dus de staarten.

Wanneer het aantal vrijheidsgraden groot is (oftewel je werkt met een grotere steekproef), dan is er steeds minder onzekerheid en de $t$-verdeling benadert de standaardnormale verdeling $N(0,1)$.
In de praktijk geldt dan ook dat bij $\\text{{df}} \geq 30$ het verschil verwaarloosbaar klein is (controleer dit voor jezelf door $\\text{{df}}=30$ in te vullen en te zien wat er gebeurt).

## ❓ Wanneer gebruik je een $t$-verdeling in plaats van de normale verdeling?
| Situatie | Gebruik |
|---|---|
| $\sigma$ bekend | $N(0,1)$ |
| $\sigma$ onbekend, $n \geq 30$ | Beide acceptabel, $t$-verdeling strikt genomen correct |
| $\sigma$ onbekend, $n < 30$ | $t$-verdeling verplicht |
| Populatie niet normaal verdeeld, $n < 30$ | Geen van beide — gebruik niet-parametrische toets |

Het aantal **vrijheidsgraden** is $\\text{{df}} = n - 1$, waarbij $n$ de steekproefgrootte is.
Je verliest één vrijheidsgraad omdat je $\mu$ schat met $\\bar{{x}}$.

Je gebruikt de $t$-verdeling bij een $t$-toets, oftewel een hypothesetoets met
$$
    H_0: \\mu = \mu_0 \\text{{ versus }} H_1: \\mu \\neq \\mu_0.
$$

De bijbehorende toetsingsgrootheid (**t-score**) is te berekenen met
$$
    t = \\frac{{\\bar{{x}} - \\mu_0}}{{s / \\sqrt{{n}}}},
$$ 
waarbij

- $\\bar{{x}}$ het steekproefgemiddelde,
- $\\mu_0$ de hypothetische waarde,
- $s$ de steekproefstandaardafwijking, en
- $n$ de steekproefgrootte.

De **toetsuitslag** kun je bepalen door de kritieke $t$-waarde $t_{{\\text{{crit}}}}$ bij een gegeven significantieniveau $\\alpha$ en aantal vrijheidsgraden $\\text{{df}} = {df}$ te berekenen:
$$
    t_{{\\text{{crit}}}}  = \\text{{tcdf}}(\\text{{opp}}=1-\\frac{{\\alpha}}{{2}}, \\text{{df}}={df}) = {t_crit:.4f}.
$$
We accepteren $H_0$ als de absolute waarde van de toetsingsgrootheid $t$ kleiner dan of gelijk aan de kritieke $t$-waarde is, en anders verwerpen we $H_0$:
$$
    |t| \\leq t_{{\\text{{crit}}}} = {t_crit:.4f} \\quad \\Rightarrow \\quad H_0 \\text{{ accepteren: geen significant verschil gevonden}}, \\\\
    |t| > t_{{\\text{{crit}}}} = {t_crit:.4f} \\quad \\Rightarrow \\quad H_0 \\text{{ verwerpen: wel een significant verschil gevonden}}.
$$
 
---
 
## 🧮 Rekenvoorbeeld
 
Stel: je meet de reactietijd van {df + 1} proefpersonen en wil toetsen of het gemiddelde **verschilt** van $\\mu_0 = 300$ ms.

| Eigenschap | Waarde |
|------------|--------|
| Steekproefgrootte: | $n = {df + 1}$, dus $\\text{{df}} = n - 1 = {df}$ |
| Steekproefgemiddelde: | $\\bar{{x}} = 312$ ms |
| Steekproefstandaardafwijking: | $s = 24$ ms |

We voeren een hypothesetoets uit met 
$$
    H_0: \\mu = 300 \\text{{ versus }} H_1: \\mu \\neq 300.
$$

**Bereken de toetsingsgrootheid:**
 
$$
    t = \\frac{{\\bar{{x}} - \\mu_0}}{{s / \\sqrt{{n}}}} = \\frac{{312 - 300}}{{24 / \\sqrt{{{df + 1}}}}} = \\frac{{12}}{{24 / {np.sqrt(df + 1):.4f}}} = \\frac{{12}}{{{24 / np.sqrt(df + 1):.4f}}} = {12 / (24 / np.sqrt(df + 1)):.4f}.
$$
 
**Vergelijk met kritieke waarde** bij $\\alpha = {alpha}$ en $\\text{{df}} = {df}$:
 
$$
    t_{{\\text{{crit}}}} = \\text{{tcdf}}(\\text{{opp}}=1-\\frac{{\\alpha}}{{2}}, \\text{{df}}={df}) = {t_crit:.4f}.
$$
 
{"✅ $|t| = " + f"{abs(12 / (24 / np.sqrt(df + 1))):.4f}" + f" < {t_crit:.4f} \\qquad \\Rightarrow \\qquad H_0$ **niet verwerpen**: geen significant verschil gevonden." if abs(12 / (24 / np.sqrt(df + 1))) < t_crit else "❌ $|t| = " + f"{abs(12 / (24 / np.sqrt(df + 1))):.4f}" + f" > {t_crit:.4f}\\qquad \\Rightarrow \\qquad H_0$ **verwerpen**: wel een significant verschil gevonden."}
"""

# Call show_explanation for printing the explanation on the webapp
show_explanation(explanation_title, explanation_md)