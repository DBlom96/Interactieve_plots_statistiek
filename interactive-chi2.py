import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy.stats import chi2

from utils.explanation_utils import show_explanation
from utils.streamlit_utils import load_css, page_header, apply_dark_style
from utils.constants import *

st.set_page_config(
    page_title="Chikwadraatverdeling",
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
    df     = st.number_input(r"Vrijheidsgraden (df):", min_value=1, value=5)
    method = st.selectbox("Visualisatiemethode:", ["Plot", "Kritiek gebied", "p-waarde"])

    alpha, toets = None, None
    if method != "Plot":
        alpha = st.number_input(r"Significantieniveau $\alpha$:", min_value=0.001, value=0.05)
        toets = st.number_input(r"Toetsingsgrootheid $\chi^2$:", value=2.0, min_value=0.0)

# ----------------------------------
# COMPUTATIONS
# ----------------------------------
if method == "Plot":
    x_max = max(10, df + 5 * np.sqrt(df))
else:
    x_max = max(10, df + 5 * np.sqrt(df), toets)

x     = np.linspace(0, x_max, 10_000)
y     = chi2.pdf(x, df)

grens, p_waarde = None, None
if method != "Plot":
    grens    = chi2.ppf(1 - alpha, df)
    p_waarde = 1 - chi2.cdf(toets, df=df)

vg_label = "vrijheidsgraad" if df == 1 else "vrijheidsgraden"

# ----------------------------------
# STAT CARDS
# ----------------------------------
if method == "Kritiek gebied":
    in_critical = toets > grens
    st.markdown(f"""
    <div class="stats-row-3">
      <div class="stat-card acceptatie">
        <span class="stat-label">Acceptatiegebied</span>
        <span class="stat-value">[0, {grens:.4f}]</span>
        <span class="stat-desc">Laagste {int(100 * (1 - alpha))}% van de verdeling</span>
      </div>
      <div class="stat-card kritiek">
        <span class="stat-label">Kritiek gebied</span>
        <span class="stat-value">({grens:.4f}, &infin;)</span>
        <span class="stat-desc">Top {int(100 * alpha)}% van de verdeling</span>
      </div>
      <div class="stat-card bi">
        <span class="stat-label">Toetsingsgrootheid</span>
        <span class="stat-value">{to_lowercase(CHISQ_HTML)} = {toets:.4f}</span>
        <span class="stat-desc">Ligt {"wel" if in_critical else "niet"} in het kritieke gebied</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

elif method == "p-waarde":
    significant = p_waarde < alpha
    st.markdown(f"""
    <div class="stats-row-3">
      <div class="stat-card bi">
        <span class="stat-label">Toetsingsgrootheid</span>
        <span class="stat-value">{to_lowercase(CHISQ_HTML)} = {toets:.4f}</span>
        <span class="stat-desc">Ligt {"wel" if significant else "niet"} in het kritieke gebied</span>
      </div>
      <div class="stat-card pvalue">
        <span class="stat-label">p-waarde</span>
        <span class="stat-value">{p_waarde:.4f}</span>
        <span class="stat-desc">Kans op uitkomst groter dan {to_lowercase(CHISQ_HTML)} = {toets:.3f}</span>
      </div>
      <div class="stat-card kritiek">
        <span class="stat-label">Significantieniveau</span>
        <span class="stat-value">{to_lowercase(ALPHA_HTML)} = {alpha:.4f}</span>
        <span class="stat-desc">Vastgestelde kans op type-I fout</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------
# HELPERS
# ----------------------------------
def add_interval_bar(ax, x_max, grens, y):
    """Draw the coloured acceptance/critical bar below the x-axis."""
    

    ax.plot([0, grens],  [bar_y, bar_y], color=ACCEPTABLE_COLOR, linewidth=8,
            solid_capstyle="butt", clip_on=False)
    ax.plot([grens, x_max], [bar_y, bar_y], color=CRITICAL_COLOR, linewidth=8,
            solid_capstyle="butt", clip_on=False)

    # Tick marks at boundary
    for xv in [0, grens, x_max]:
        ax.plot([xv, xv], [bar_y - tick_h, bar_y + tick_h],
                color=PLOT_FONT_COLOR, linewidth=1, clip_on=False)

    # Labels
    ax.text((0 + grens) / 2, ytext, "Acceptatiegebied",
            ha="center", va="center", fontsize=ANNOTATION_FONT_SIZE,
            color=ACCEPTABLE_COLOR, fontfamily="JetBrains Mono")
    ax.text((grens + x_max) / 2, ytext, "Kritiek gebied",
            ha="center", va="center", fontsize=ANNOTATION_FONT_SIZE,
            color=CRITICAL_COLOR, fontfamily="JetBrains Mono")



# ----------------------------------
# FIGURE
# ----------------------------------
fig, ax = plt.subplots(figsize=(10, 5))

bar_y  = -0.055 * max(y)
tick_h = 0.018 * max(y)
ytext = bar_y - 3.8 * tick_h

# Base curve — always drawn
ax.plot(x, y, color=H0_COLOR, linewidth=2.5,
        label=rf"$\\chi^2(\mathrm{{df}}={df})$")

if method == "Kritiek gebied":
    # Shade acceptance and critical regions
    # ax.fill_between(x, y, where=(x <= grens), color=ACCEPTABLE_COLOR, alpha=0.15)
    ax.fill_between(x, y, where=(x >= grens), color=CRITICAL_SHADE_COLOR)

    # Critical value line
    ax.plot([grens, grens], [0, chi2.pdf(grens, df)],
            color=CRITICAL_COLOR, linewidth=1.5, linestyle="--",
            label=rf"$\\chi^2_{{\mathrm{{crit}}}} = {grens:.4f}$")

    # Test statistic line
    ax.plot([toets, toets], [0, chi2.pdf(toets, df)],
            color=H0_COLOR, linewidth=1.5, linestyle=":",
            label=rf"$\\chi^2 = {toets:.4f}$")
    ax.text(toets,  ytext, f"$\\chi^2 = {toets:.2f}$",
            ha="center", va="center", fontsize=ANNOTATION_FONT_SIZE,
            color=H0_COLOR, fontfamily="JetBrains Mono")

    add_interval_bar(ax, x_max, grens, y)
    plt.ylim(bottom=3*bar_y, top=1.1*max(y))

elif method == "p-waarde":
    # Shade p-value region
    ax.fill_between(x, y, where=(x >= toets),  color=BETA_COLOR,     alpha=0.25,
                    label=rf"p-waarde $= {p_waarde:.4f}$")
    # Shade critical region on top
    ax.fill_between(x, y, where=(x >= grens),  color=CRITICAL_COLOR, alpha=0.25,
                    label=rf"Kritiek gebied $(\alpha={alpha})$")

    # Lines
    ax.plot([toets, toets], [0, chi2.pdf(toets, df)],
            color=H0_COLOR,      linewidth=1.5, linestyle=":",
            label=rf"$\chi^2 = {toets:.4f}$")
    ax.plot([grens, grens], [0, chi2.pdf(grens, df)],
            color=CRITICAL_COLOR, linewidth=1.5, linestyle="--",
            label=rf"$\chi^2_{{\mathrm{{crit}}}} = {grens:.4f}$")
    
    # Test statistic line
    ax.plot([toets, toets], [0, chi2.pdf(toets, df)],
            color=H0_COLOR, linewidth=1.5, linestyle=":",
            label=rf"$\chi^2$")
    ax.text(toets,  1/2*ytext, f"$\\chi^2$",
            ha="center", va="center", fontsize=ANNOTATION_FONT_SIZE,
            color=H0_COLOR, fontfamily="JetBrains Mono")

    plt.ylim(bottom=2*bar_y, top=1.1*max(y))



# Title — two-color for method != "Plot"
if method == "Plot":
    apply_dark_style(
        fig=fig, ax=ax,
        title=rf"Kansdichtheidsfunctie — $\chi^2(\mathrm{{df}}={df})$",
        xlabel=r"$x$",
        ylabel=r"Kansdichtheid $f(x)$"
    )
elif method == "Kritiek gebied":
    apply_dark_style(
        fig=fig, ax=ax,
        xlabel=r"$x$",
        ylabel=r"Kansdichtheid $f(x)$"
    )
    acceptable = (toets < grens) if grens is not None else False
    ax.text(0.35, 1.02,
        rf"$\chi^2 = {toets:.4f}$ ligt in het ",
        transform=ax.transAxes, ha="right", va="center",
        fontsize=TITLE_FONT_SIZE, 
        color=PLOT_FONT_COLOR,
        fontfamily="JetBrains Mono"
    )
    ax.text(0.36, 1.016,
        f"{'acceptatiegebied' if acceptable else 'kritieke gebied'}",
        transform=ax.transAxes, ha="left", va="center",
        fontsize=TITLE_FONT_SIZE,
        color=ACCEPTABLE_COLOR if acceptable else CRITICAL_COLOR,
        fontfamily="JetBrains Mono"
    )
elif method == "p-waarde":
    apply_dark_style(
        fig=fig, ax=ax,
        xlabel=r"$x$",
        ylabel=r"Kansdichtheid $f(x)$"
    )
    acceptable = (p_waarde > alpha)
    ax.text(0.6, 1.02,
        rf"De $p$-waarde die hoort bij $\chi^2 = {toets:.4f}$ is",
        transform=ax.transAxes, ha="right", va="center",
        fontsize=TITLE_FONT_SIZE, 
        color=PLOT_FONT_COLOR,
        fontfamily="JetBrains Mono"
    )
    ax.text(0.615, 1.02,
        f"{'groter' if p_waarde > alpha else 'kleiner'}",
        transform=ax.transAxes, ha="left", va="center",
        fontsize=TITLE_FONT_SIZE,
        color=ACCEPTABLE_COLOR if p_waarde > alpha else CRITICAL_COLOR,
        fontfamily="JetBrains Mono"
    )
    if p_waarde > alpha:
        xshift=0.73
    else:
        xshift=0.745
    ax.text(xshift, 1.02,
        f"dan $\\alpha = {alpha}$.",
        transform=ax.transAxes, ha="left", va="center",
        fontsize=TITLE_FONT_SIZE,
        color=PLOT_FONT_COLOR,
        fontfamily="JetBrains Mono"
    )

plt.tight_layout(pad=2.5)
st.pyplot(fig, use_container_width=True)
plt.close(fig)

# ----------------------------------
# EXPLANATION
# ----------------------------------
explanation_title = "📚 De chikwadraatverdeling"
explanation_markdown = rf"""
## 🧠 Intuïtie: waar komt de verdeling vandaan?
 
Stel je voor dat je een standaardnormaal verdeelde toevalsvariabele $Z \sim N(0,1)$ kwadrateert.
Het kwadraat $Z^2$ is altijd positief en heeft een scheve verdeling — dat is de $\chi^2$-verdeling
met **1 vrijheidsgraad**.
 
Als je $\text{{df}}$ onafhankelijke standaardnormale variabelen kwadrateert en optelt, krijg je de
$\chi^2$-verdeling met $\text{{df}}$ vrijheidsgraden:
 
$$
    \chi^2(\text{{df}}) = Z_1^2 + Z_2^2 + \cdots + Z_{{\text{{df}}}}^2, \quad Z_i \sim N(0,1)
$$
 
Dit verklaart direct de belangrijkste eigenschappen:
 
- **Altijd positief** — een som van kwadraten kan niet negatief zijn.
- **Scheef naar rechts** — bij weinig termen domineren uitschieters; bij veel termen
  middelt alles uit en lijkt de verdeling steeds meer op een normale verdeling (centrale limietstelling).
- **Verwachtingswaarde = df** — elk kwadraat $Z_i^2$ heeft verwachtingswaarde 1, dus de som heeft
  verwachtingswaarde $\text{{df}}$.
- **Variantie = 2·df** — de variantie van $Z_i^2$ is 2, dus de totale variantie is $2\,\text{{df}}$.
 
In de praktijk komt $\chi^2$ voor wanneer je **afwijkingen van een verwachte waarde kwadreert en
optelt**, wat precies de structuur is van de meeste statistische toetsen die de verdeling gebruiken.
 
---
  
## 🧪 Toepassingen met voorbeelden
 
### 1. Aanpassingstoets (goodness-of-fit test)
Toetst of waargenomen frequenties overeenkomen met een verwachte verdeling.
 
**Voorbeeld:** Een dobbelsteen wordt 120 keer gegooid. Bij een eerlijke dobbelsteen verwacht je
elk getal 20 keer. De daadwerkelijk waargenomen getallen zijn echter 25, 17, 19, 22, 18, 19.
Samengevat in een tabel geeft dit:

| Uitkomst | **Verwachte** frequentie $E_i$ | **Observed** frequentie $O_i$ |
|---|---|---|
| 1 | 20 | 25 |
| 2 | 20 | 17 |
| 3 | 20 | 19 |
| 4 | 20 | 22 |
| 5 | 20 | 18 |
| 6 | 20 | 19 |

We willen nu de volgende hypothesetoets uitvoeren:
- $H_0$: de dobbelsteen is eerlijk
- $H_1$: de dobbelsteen is niet eerlijk en bepaalde uitkomsten komen significant vaker voor.

De toetsingsgrootheid die bij deze toets hoort berekenen we als volgt:
$$
\chi^2 = \sum_{{i=1}}^{{6}} \frac{{(O_i - E_i)^2}}{{E_i}}
= \frac{{(25-20)^2}}{{20}} + \frac{{(17-20)^2}}{{20}} + \cdots = 2.20.
$$

Omdat er 6 mogelijke uitkomsten zijn, is het aantal vrijheidsgraden df $=5$.

Bij een significantieniveau van $\alpha = 0.05$ berekenen we de grens van het kritieke gebied als volgt:
$$
    \chi^2\text{{cdf}}(\text{{lower}}=X, \text{{upper}}=10^{{99}}, \text{{df}}=5) = \frac{{\alpha}}{{2}}=0.025 \Rightarrow X = 11.07.
$$

Het kritieke gebied is dus $(11.07, \infty)$.
Omdat $2.20$ niet in het kritieke gebied ligt, wordt $H_0$ niet verworpen.
Op basis van de steekproefdata is er onvoldoende bewijs om aan te nemen dat de dobbelsteen oneerlijk is.
 
---
 
### 2. Onafhankelijkheidstoets
Toetst of twee categorische variabelen samenhangen in een kruistabel.
 
**Voorbeeld:** Aan een testpanel van 200 personen wordt gevraagd wat hun rookgedrag is en of ze last hebben van een longziekte.
De wetenschappers willen onderzoeken mensen die roken meer kans hebben om last te hebben van een longziekte.
De vraag is dus: zijn de variabelen **rookgedrag** en **longziekte** onafhankelijk?

De resultaten van het onderzoek (dus de **observed frequenties** $O_{{ij}}$) kunnen worden samengevat in onderstaande tabel:

|  | Ziek | Niet ziek | **Totaal**
|---|---|---|---|
| Rokers | 40 | 60 | 100 |
| Niet-rokers | 20 | 80 | 100 |
| **Totaal** | 60 | 140 | 200 |

Hier is $i=1,2$ de index van de rij en $j=1,2$ de index van de kolom.

We willen nu de volgende hypothesetoets uitvoeren:
- $H_0$: de variabelen **rookgedrag** en **lijden aan een longziekte** zijn onafhankelijk van elkaar.
- $H_1$: de variabelen **rookgedrag** en **lijden aan een longziekte** zijn wel afhankelijk van elkaar.

Onder de nulhypothese zijn de variabelen onafhankelijk van elkaar.
In dat geval kunnen we de **verwachte frequenties** $E_{{ij}}$ berekenen als volgt:
$$
    E_{{ij}} = \frac{{\text{{rijtotaal rij $i$}} \cdot \text{{kolomtotaal kolom $j$}}}}{{\text{{totaal}}}}
$$

|  | Ziek | Niet ziek | **Totaal**
|---|---|---|---|
| Rokers | $\frac{{100 \cdot 60}}{{200}} = 30$ | $\frac{{100 \cdot 140}}{{200}} = 70$ | 100 |
| Niet-rokers | $\frac{{100 \cdot 60}}{{200}} = 30$ | $\frac{{100 \cdot 140}}{{200}} = 70$ | 100 |
| **Totaal** | 60 | 140 | 200 |


De toetsingsgrootheid die bij deze toets hoort berekenen we als volgt:
$$
    \chi^2 = \sum_{{i,j=1}}^{{2}} \frac{{(O_{{ij}} - E_{{ij}})^2}}{{E_{{ij}}}}
    = \frac{{(40-30)^2}}{{30}} + \frac{{(60-70)^2}}{{70}} + \cdots = 9.52.
$$
 
Het aantal vrijheidsgraden is gelijk aan df = $(\#\text{{aantal rijen}}-1)(\#\text{{aantal kolommen}}-1) = (2-1)(2-1)=1$.

Bij een significantieniveau van $\alpha = 0.05$ berekenen we de grens van het kritieke gebied als volgt:
$$
    \chi^2\text{{cdf}}(\text{{lower}}=X, \text{{upper}}=10^{{99}}, \text{{df}}=1) = \frac{{\alpha}}{{2}}=0.025 \Rightarrow X \approx {chi2.ppf(q=0.95, df=1):.2f}.
$$

Het kritieke gebied is dus $({chi2.ppf(q=0.95, df=1):.2f}, \infty)$.
Omdat $9.52$ wel in het kritieke gebied ligt, wordt $H_0$ verworpen.
Op basis van de steekproefdata is er voldoende bewijs om aan te nemen dat de variabelen **rookgedrag** en **lijden aan een longziekte** afhankelijk zijn van elkaar.
Als we de waargenomen frequenties bekijken, zien we dat rokers relatief gezien veel vaker aan een longziekte lijden (40/100, oftewel 40%) vergeleken met niet-rokers (20/100, oftewel 20%).
 
---
 
## 🎯 Interpretatie: kritiek gebied en $p$-waarde
 
### Kritiek gebied
Het kritieke gebied is het gedeelte van de verdeling dat zo onwaarschijnlijk is onder $H_0$,
dat je bereid bent $H_0$ te verwerpen. Bij de $\chi^2$-toets is dit altijd **rechtszijdig**.
De reden hiervoor is

— hoe groter de waarde van $\chi^2$, hoe groter de verschillen tussen de verwachte frequenties en de daadwerkelijk waargenomen frequenties - minder consistent met $H_0$.
 
$$
    \text{{Verwerp }} H_0 \text{{ als }} \chi^2 > g
$$
 
waarbij $g$ de oplossing is van: 
$$
    \chi^2\text{{cdf}}(\text{{lower}}=X, \text{{upper}}=10^{{99}}, \text{{df}}=1) = \frac{{\alpha}}{{2}}=0.025.
$$
  
### p-waarde
De p-waarde is de kans om een $\chi^2$-waarde te observeren die **minstens zo extreem** is
als de gevonden toetsingsgrootheid, gegeven dat $H_0$ waar is:
 
$$
p = P(X^2 \geq \chi^2) = \chi^2\text{{cdf}}(\text{{lower}}=\chi^2, \text{{upper}}=10^{{99}}, \text{{df}}=df)
$$
 
- **Kleine p-waarde** ($p < \alpha$): het is onwaarschijnlijk dat we nog extremere data zouden waarnemen onder $H_0$ → verwerp $H_0$.
- **Grote p-waarde** ($p \geq \alpha$): het is niet onwaarschijnlijk dat we nog extremere data zouden waarnemen onder $H_0$ → geen reden om $H_0$ te verwerpen.
 
⚠️ Een grote p-waarde betekent **niet** dat $H_0$ waar is — alleen dat je onvoldoende bewijs hebt om hem te verwerpen.
"""

show_explanation(explanation_title, explanation_markdown)