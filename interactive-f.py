import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import f

from utils.explanation_utils import show_explanation
from utils.streamlit_utils import load_css, css_to_rgba, page_header

st.set_page_config(
    page_title="Visualisatie van de F-verdeling",
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

page_header("📊 $F$-verdeling", "Toets voor gelijke varianties")
with st.sidebar:
    st.header("Parameters")

    df1 = st.number_input(label="Aantal vrijheidsgraden eerste steekproef ($\\text{{df}}_1$)", min_value=1, value=5)
    df2 = st.number_input(label="Aantal vrijheidsgraden tweede steekproef ($\\text{{df}}_2$)", min_value=1, value=5)
    method = st.selectbox(
        label="Selecteer visualisatiemethode", 
        options=["Plot", "Kritiek gebied", "p-waarde"]
    )

    if method != "Plot":
        alpha = st.number_input("Significantieniveau $\\alpha$", min_value=0.001, value=0.05)
        toetsingsgrootheid = st.number_input("Geobserveerde toetsingsgrootheid $f$", value=2.0)

# --------------------------------
# SAMPLING
# --------------------------------

def draw_f_distribution(df1, df2, xmax):
    x = np.linspace(0, xmax, 10_000)
    y = f.pdf(x, df1, df2)
    return x, y

# ------------------------
# PRECOMPUTED VALUES
# ------------------------
xmax = f.ppf(0.99, dfn=df1, dfd=df2)
x, y = draw_f_distribution(df1, df2, xmax)
ACCEPTABLE_COLOR = "springgreen" # "neongreen"
DIST_COLOR = "gold"
P_VALUE_COLOR = css_to_rgba("#a8dadc", 0.4) # "cyan"
CRITICAL_COLOR = "tomato" # "tomato red"
CRITICAL_SHADE_COLOR = css_to_rgba(CRITICAL_COLOR, 0.4)

YTEXT = -0.2 * max(y)  # Position for the horizontal line
YLINES = 1/2 * YTEXT

if method != "Plot":
    linkergrens = f.ppf(q=alpha/2, dfn=df1, dfd=df2)
    rechtergrens = f.ppf(q=1-alpha/2, dfn=df1, dfd=df2)

    p_value_left = f.cdf(toetsingsgrootheid, dfn=df1, dfd=df2)
    p_value_right = 1 - f.cdf(toetsingsgrootheid, dfn=df1, dfd=df2)
    p_waarde = min(p_value_left, p_value_right)

    mask_acceptable = (linkergrens <= x) & (x <= rechtergrens)
    mask_critical_left = (x < linkergrens)
    mask_critical_right = (x > rechtergrens)

    inside_critical_region = (toetsingsgrootheid < linkergrens) or (toetsingsgrootheid > rechtergrens)



# ------------------------
# PLOTTING
# ------------------------
fig = go.Figure()

if method == "Kritiek gebied":
    # We toetsen altijd tweezijdig met de F-toets voor gelijke varianties

    # Teken stippellijnen om toetsingsgrootheid en kritieke grenzen aan te geven.
    for (val, color) in [(toetsingsgrootheid, DIST_COLOR), (linkergrens, CRITICAL_COLOR), (rechtergrens, CRITICAL_COLOR)]:
        fig.add_trace(go.Scatter(
            x=[val, val],
            y=[0, f.pdf(val, dfn=df1, dfd=df2)],
            mode='lines',
            line=dict(color=color, dash='dash'),
            showlegend=False
        ))

    # Arceer het kritieke gebied
    for mask in [mask_critical_left, mask_critical_right]:
        fig.add_trace(go.Scatter(
            x=x[mask],
            y=y[mask],
            mode='lines',
            fill='tozeroy',
            fillcolor=CRITICAL_SHADE_COLOR,
            showlegend=False
        ))  

    # Voeg tekst toe op positie van toetsingsgrootheid
    fig.add_trace(go.Scatter(
        x=[toetsingsgrootheid],
        y=[YLINES * 2],
        mode='text',
        marker=dict(color=DIST_COLOR, size=10),
        text="f",
        textfont=dict(size=20, color=DIST_COLOR),
        textposition="top center",
        showlegend=False
    ))

    # Voeg lijnen toe om de acceptatie- en kritieke gebieden aan te geven
    for (l, r, color, text) in [
        (0, linkergrens, CRITICAL_COLOR, ""),
        (linkergrens, rechtergrens, ACCEPTABLE_COLOR, "Acceptatiegebied"),
        (rechtergrens, xmax, CRITICAL_COLOR, "Kritiek gebied")
    ]:
        
        fig.add_trace(go.Scatter(
            x=[l, r],
            y=[YLINES, YLINES],
            mode='lines',
            line=dict(color=color, width=10),
            showlegend=False
        ))

        # Add text at position of regions
        fig.add_trace(go.Scatter(
            x=[(l + r) / 2],
            y=[YLINES * 2.5],
            mode='text',
            text=text,
            textfont=dict(color=color, size=20),
            showlegend=False
        ))
 
    # -------------------------------
    # STAT CARDS
    # -------------------------------

    st.markdown(f"""
    <div class="stats-row-3" >
        <div class="stat-card acceptatie">
            <span class="stat-label">Acceptatiegebied</span>
            <span class="stat-value">[{linkergrens:.4f}, {rechtergrens:.4f}]</span>
            <span class="stat-desc">Kans op redelijke uitkomst (laagste {int(100*(1-alpha))}%)</span>
        </div>
        <div class="stat-card kritiek">
            <span class="stat-label">Kritiek gebied</span>
            <span class="stat-value">[0, {linkergrens:.4f}) en ({rechtergrens:.4f}, &infin;)</span>
            <span class="stat-desc">Waarden die duiden op extreem groot verschil tussen de twee varianties</span>
        </div>
        <div class="stat-card bi">
            <span class="stat-label">Toetsingsgrootheid</span>
            <span class="stat-value">&chi;<sup>2</sup> = {toetsingsgrootheid:.4f}</span>
            <span class="stat-desc">De toetsingsgrootheid ligt {"" if inside_critical_region else "niet"} in het kritieke gebied</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

if method == "p-waarde":
    # Teken stippellijn om toetsingsgrootheid aan te geven.
    fig.add_trace(go.Scatter(
        x=[toetsingsgrootheid, toetsingsgrootheid],
        y=[0, f.pdf(toetsingsgrootheid, dfn=df1, dfd=df2)],
        mode='lines',
        line=dict(color=DIST_COLOR, dash='dash'),
        showlegend=False
    ))

    # Arceer het gebied corresponderend met de p-waarde
    if p_value_left < p_value_right:
        mask = (x < toetsingsgrootheid)
    else:
        mask = (x > toetsingsgrootheid)

    fig.add_trace(go.Scatter(
        x=x[mask],
        y=y[mask],
        mode='lines',
        fill='tozeroy',
        fillcolor=P_VALUE_COLOR,
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=[toetsingsgrootheid],
        y=[YTEXT],
        mode='text',
        marker=dict(color=DIST_COLOR, size=10),
        text=r"f",
        textfont=dict(size=30, color=DIST_COLOR),
        textposition="top center",
        showlegend=False
    ))

    # -------------------------------
    # STAT CARDS
    # -------------------------------
    
    st.markdown(f"""
    <div class="stats-row-3" >
        <div class="stat-card bi">
            <span class="stat-label">Toetsingsgrootheid</span>
            <span class="stat-value">f = {toetsingsgrootheid:.4f}</span>
            <span class="stat-desc">De toetsingsgrootheid ligt {"" if p_waarde < alpha / 2 else "niet"} in het kritieke gebied</span>
        </div>
        <div class="stat-card pvalue">
            <span class="stat-label">p-waarde</span>
            <span class="stat-value">{p_waarde:.4f}</span>
            <span class="stat-desc">Kans op uitkomst {"&le;" if p_value_right > p_value_left else "&ge;"} f = {toetsingsgrootheid:.3f}</span>
        </div>
        <div class="stat-card kritiek">
            <span class="stat-label">Significantieniveau</span>
            <span class="stat-value">&alpha; = {alpha:.4f}</span>
            <span class="stat-desc">Vastgestelde kans op type-I fout<br> (H<sub>0</sub> onterecht verwerpen)</span>
        </div>
        
    </div>
    """, unsafe_allow_html=True)

# Draw the pdf of the F-distribution
fig.add_trace(go.Scatter(
    x=x,
    y=y,
    mode='lines',
    line=dict(color=DIST_COLOR),
    showlegend=False
))

fig.update_layout(
    font=dict(family="JetBrains Mono, monospace", color="#f1faee"),
    title = dict(
        text=(f"F-verdeling met df<sub>1</sub> = {df1} en df<sub>2</sub> = {df2} vrijheidsgraden."),
        font=dict(size=30, family="JetBrains Mono, monospace", color="#f1faee"),
    ),
    xaxis = dict(
        title=dict(text="x", font=dict(size=25)),
        tickfont=dict(size=20),    
    ),
    yaxis = dict(
        title=dict(text="Kansdichtheidsfunctie f(x)", font=dict(size=25)),
        tickfont=dict(size=20),    
    ),
    height=600
)

st.plotly_chart(fig, use_container_width=True, config=dict(displayModeBar=False))

explanation_title = "📚 De $F$-verdeling"
explanation_md = fr"""
# 📊 De $F$-verdeling

De **$F$-verdeling** is een continue kansverdeling die optreedt als de verhouding van twee onafhankelijke, geschaalde $\chi^2$-verdelingen. Ze speelt een centrale rol bij de **toets voor gelijke varianties** van twee normaal verdeelde populaties.

----

## 💡 Intuïtie

De toetsingsgrootheid vergelijkt twee **steekproefvarianties**. Stel dat we twee normaal verdeelde populaties $X$ en $Y$ hebben, met parameters $(\mu_X, \sigma_X)$ en $(\mu_Y, \sigma_Y)$ die allevier onbekend zijn.

voor beide populaties een steekproef $(x_1, x_2, \ldots, x_n)$ en $(y_1, y_2, \ldots, y_m)$, waarbij $n$ en $m$ positieve gehele getallen zijn die de steekproefgroottes aan duiden.

Met behulp van de F-verdeling kunnen we een F-toets uitvoeren om te testen of de varianties gelijk zijn, oftewel $\sigma_X^2 = \sigma_Y^2$. De bijbehorende hypotheses van deze toets zijn dan ook

$$
    H_0: \sigma_X^2 = \sigma_Y^2 \text{{ versus }} H_1: \sigma_X^2 = \sigma_Y^2.
$$

Om de hypothesetoets uit te voeren nemen we twee steekproeven, een uit de populatie $X$ en een uit de populatie $Y$.
Deze steekproeven noteren we met $(X_1, X_2, \ldots, X_n)$ en $(Y_1, Y_2, \ldots, Y_m)$, waarbij $n$ en $m$ positieve gehele getallen zijn die de steekproefgroottes aan duiden. We beginnen door eerst de steekproefvarianties te berekenen, met behulp van de bekende formules:

$$
    S_X^2 = \frac{{(X_1-\bar{{X}})^2 + \ldots + (X_n - \bar{{X}})^2}}{{n-1}}
    S_Y^2 = \frac{{(Y_1-\bar{{Y}})^2 + \ldots + (Y_m - \bar{{Y}})^2}}{{m-1}}
$$

De toetsingsgrootheid die hoort bij deze hypothesetoets is
$$
    F = \frac{{S_1^2}}{{S_2^2}},
$$
oftewel de breuk van deze twee steekproefvarianties.

⚠️ Merk hierbij het volgende op:
- $F \approx 1$: de varianties lijken op elkaar — consistent met $H_0$.
- $F$ ligt veraf van $1$: één steekproef is veel meer gespreid dan de andere — bewijs tegen $H_0$.

Onder de nulhypothese $H_0$ volgt deze toetsingsgrootheid de F(n-1, m-1)-verdeling, oftewel de $F$-verdeling met $\text{{df}}_1 = n-1$ en $\\text{{df}}_2 = m-1$ vrijheidsgraden. Omdat de $F$-verdeling rechtsscheef is en altijd positief, is de **tweezijdige toets asymmetrisch**: de linker- en rechtergrens liggen niet even ver van het midden.

---

## 🧪 Hypothesen & beslissingsregels

| | |
|---|---|
| **$H_0$** | $\sigma_1^2 = \sigma_2^2$ |
| **$H_1$** | $\sigma_1^2 \neq \sigma_2^2$ |

De toets is altijd **tweezijdig**: zowel een te hoge als een te lage $f$-waarde geeft aanleiding tot verwerping.

**Via het kritieke gebied** — verwerp $H_0$ als:
$$f < F_{{\alpha/2;\, \text{{df}}_1,\, \text{{df}}_2}} \quad \text{{of}} \quad f > F_{{1-\alpha/2;\, \text{{df}}_1,\, \text{{df}}_2}}$$

**Via de $p$-waarde** — verwerp $H_0$ als:
$$p = \min\left(P(F \leq f),\; P(F \geq f)\right) < \alpha / 2$$

---

## 🎨 Over de visualisatie

| Methode | Wat zie je? |
|---|---|
| **Plot** | De kansdichtheidsfunctie $f(x)$ met de gekozen vrijheidsgraden $\text{{df}}_1 = {df1}$ en $\text{{df}}_2 = {df2}$. |
| **Kritiek gebied** | Het acceptatiegebied (groen) en de kritieke gebieden (rood) bij significantieniveau $\alpha$. |
| **$p$-waarde** | Het gearceerde oppervlak onder de curve corresponderend met de kans op een uitkomst minstens zo extreem als de geobserveerde $f$. |

---

## 🪖 Rekenvoorbeeld: precisie van twee sluipschuttersteams

Een defensie-onderzoeker wil weten of twee sluipschutterteams — **Team Alpha** en **Team Bravo** — even consistent schieten. Beide teams voeren $10$ oefenschoten uit op een doelwit op $300$ meter. De **afwijking ten opzichte van het middelpunt** (in cm) wordt geregistreerd. De onderzoeker wil bij een significantieniveau van $\alpha = 0.05$ toetsen of de spreiding in beide teams gelijk is.

De gemeten afwijkingen zijn:

| | Metingen (cm) |
|---|---|
| **Team Alpha** ($n = 10$) | $12, 15, 10, 14, 13, 16, 11, 14, 12, 13$ |
| **Team Bravo** ($m = 10$) | $9, 22, 7, 18, 25, 6, 20, 11, 19, 8$ |

### **Stap 1 — Hypothesen opstellen:**

$$
    H_0: \sigma_A^2 = \sigma_B^2 \quad \text{{versus}} \quad H_1: \sigma_A^2 \neq \sigma_B^2.
$$

### **Stap 2 — Steekproefvarianties berekenen:**

De steekproefgemiddelden zijn $\bar{{x}}_A = 13.0$ en $\bar{{x}}_B = 14.5$. De steekproefvarianties bedragen:

$$
    s_A^2 = \frac{{(12-13)^2 + (15-13)^2 + \ldots + (13-13)^2}}{{9}} = \frac{{30}}{{9}} \approx 3.3333, \\
    s_B^2 = \frac{{(9-14.5)^2 + (22-14.5)^2 + \ldots + (8-14.5)^2}}{{9}} = \frac{{432.5}}{{9}} \approx 48.0556.
$$

### **Stap 3 — Toetsingsgrootheid berekenen:**

$$
    f = \frac{{s_A^2}}{{s_B^2}} = \frac{{3.3333}}{{48.0556}} \approx 0.0694.
$$

### **Stap 4 — Toetsuitslag bepalen** bij $\alpha = 0.05$ en $\text{{df}}_1 = \text{{df}}_2 = 9$:

- **Methode 1: kritieke gebied**

    - Voor het berekenen van de linkergrens, los op:
    $$
        \text{{Fcdf}}(\text{{lower}} = 0, \text{{upper}} = X, \text{{df}}_1 = 9, \text{{df}}_1 = 9) = \alpha/2 \quad \Rightarrow \quad X \approx 0.2484.
    $$
    - Voor het berekenen van de rechtergrens, los op:
    $$
        \text{{Fcdf}}(\text{{lower}} = X, \text{{upper}} = \infty, \text{{df}}_1 = 9, \text{{df}}_1 = 9) = \alpha/2 \quad \Rightarrow \quad X \approx 4.0260.
    $$

    Het kritieke gebied wordt dus gegeven door $[0, 0.2484)$ en $(4.0260, \infty)$. De geobserveerde toetsingsgrootheid $f \approx 0.0694 < 0.2484$, oftewel de toetsingsgrootheid ligt **in het (linker)kritieke gebied**.

- **Methode 2: de $p$-waarde**

    - Voor het berekenen van de $p$-waarde, bereken de **kleinste** waarde van de linkeroverschrijdingskans en de rechteroverschrijdingskans:
        - Linkeroverschrijdingskans (kans op een kleinere waarde dan $f \approx 0.0694$):
        $$
            P(F \leq f) = \text{{Fcdf}}(\text{{lower}} = 0, \text{{upper}} = f = 0.0694, \text{{df}}_1 = 9, \text{{df}}_1 = 9) \approx 2.4733 \cdot 10^{{-4}}.
        $$

        - Rechteroverschrijdingskans (kans op een grotere waarde dan $f \approx 0.0694$):
    
    $$
        P(F \geq f) = \text{{Fcdf}}(\text{{lower}} = f = 0.0694, \text{{upper}} = 10^{{99}}, \text{{df}}_1 = 9, \text{{df}}_1 = 9) \approx 0.9998.
    $$

    De $p$-waarde is het minimum van deze twee waarden, dus $p \approx 2.4733 \cdot 10^{{-4}}$.

### **Stap 5 — Beslissing:**

- **Methode 1: kritieke gebied**
    - De toetsingsgrootheid $f \approx 0.0694$ ligt **in het kritieke gebied**, dus we verwerpen $H_0$.

- **Methode 2: de $p$-waarde**
    - De $p \approx 2.4733 \cdot 10^{{-4}}$ is (veel) kleiner dan $\alpha / 2 = 0.025$ (want we toetsen tweezijdig!), dus we verwerpen $H_0$.

Er is op basis van deze steekproeven voldoende statistisch bewijs om te concluderen dat de schietprecisie van Team Alpha en Team Bravo **significant verschilt** op het 5%-significantieniveau. Team Bravo schiet gemiddeld even ver, maar met een veel grotere spreiding.
"""

show_explanation(explanation_title, explanation_md)

