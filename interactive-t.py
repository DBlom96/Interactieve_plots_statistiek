import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy.stats import norm, t

from utils.explanation_utils import show_explanation
from utils.streamlit_utils import load_css, page_header, apply_dark_style
from utils.constants import *

st.set_page_config(
    page_title="Student's t-verdeling",
    initial_sidebar_state="expanded",
    layout="wide"
)

# ----------------------------------
# CSS
# ----------------------------------
load_css()

BG_COLOR = "#1a1f2e"

# ----------------------------------
# PARAMETERS
# ----------------------------------
page_header("📊 Student's $t$-verdeling", "Continue kansverdelingen")

with st.sidebar:
    st.header("Parameters")
    df    = st.number_input(r"Aantal vrijheidsgraden (df):", min_value=1, value=1, step=1)
    alpha = st.number_input(r"Significantieniveau $\alpha$:", min_value=1e-6, max_value=1.0, value=0.05)

# ----------------------------------
# COMPUTATIONS
# ----------------------------------
confidence = 1 - alpha
conf_pct   = int(100 * confidence)
x          = np.linspace(-4, 4, 1_000)
normal_pdf = norm.pdf(x)
t_pdf      = t.pdf(x, df=df)
z_crit     = norm.ppf(1 - alpha / 2)
t_crit     = t.ppf(1 - alpha / 2, df=df)

# Example computation (rekenvoorbeeld)
n_ex    = df + 1
t_score = 12 / (24 / np.sqrt(n_ex))
reject  = abs(t_score) > t_crit

# ----------------------------------
# STAT CARDS
# ----------------------------------
st.markdown(f"""
<div class="stats-row-3">
  <div class="stat-card bi">
    <span class="stat-label">Kritieke waarden <i>N</i>(0,1)</span>
    <span class="stat-value">&plusmn;{z_crit:.4f}</span>
    <span class="stat-desc">{conf_pct}%-betrouwbaarheidsinterval</span>
  </div>
  <div class="stat-card pi">
    <span class="stat-label">Kritieke waarden {to_lowercase(T_HTML)}({to_lowercase(DF_HTML)}={df})</span>
    <span class="stat-value">&plusmn;{t_crit:.4f}</span>
    <span class="stat-desc">{conf_pct}%-betrouwbaarheidsinterval</span>
  </div>
  <div class="stat-card beta">
    <span class="stat-label">Betrouwbaarheid normale benadering</span>
    <span class="stat-value">{(t.cdf(z_crit, df=df) - t.cdf(-z_crit, df=df)):.4f}</span>
    <span class="stat-desc"><i>t</i>-verdeling heeft bredere staarten</span>
  </div>"
</div>
""", unsafe_allow_html=True)

# text =   "<div class="stat-card beta">
#     <span class="stat-label">Verschil kritieke waarden</span>
#     <span class="stat-value">{t_crit - z_crit:.4f}</span>
#     <span class="stat-desc"><i>t</i>-verdeling heeft bredere staarten</span>
#   </div>"
# ----------------------------------
# HELPERS
# ----------------------------------
def fill_tails(ax, x, y, crit, color):
    """Shade both tails beyond ±crit."""
    for mask in [x < -crit, x > crit]:
        ax.fill_between(x, y, where=mask, color=color, alpha=0.2)


def crit_vlines(ax, x, pdf_func, crit, color, df=None):
    """Draw dashed vertical lines at ±crit up to the PDF height."""
    for xv in [-crit, crit]:
        yv = pdf_func(xv) if df is None else pdf_func(xv, df)
        ax.plot([xv, xv], [0, yv], color=color, linewidth=1.5, linestyle="--")

# ----------------------------------
# FIGURE
# ----------------------------------
fig, ax = plt.subplots(figsize=(10, 5))

# Shaded tails
fill_tails(ax, x, normal_pdf, z_crit, H0_COLOR)
fill_tails(ax, x, t_pdf,      t_crit, H1_COLOR)

# Critical value lines
crit_vlines(ax, x, norm.pdf, z_crit, H0_COLOR)
if df >= 3:   # avoid very tall lines for low df
    crit_vlines(ax, x, t.pdf, t_crit, H1_COLOR, df=df)

# Curves
ax.plot(x, normal_pdf, color=H0_COLOR, linewidth=2.5,
        label=r"Normale verdeling $\mathcal{N}(0,1)$")
ax.plot(x, t_pdf,      color=H1_COLOR, linewidth=2.5,
        label=rf"$t$-verdeling $(\mathrm{{df}}={df})$")

apply_dark_style(
    fig=fig,
    ax=ax,
    title=rf"Kansdichtheidsfuncties - $\mathcal{{N}}(0,1)$ en $t($df$={df})$",
    xlabel=r"$x$",
    ylabel=r"Kansdichtheid $f(x)$"
)
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))


plt.tight_layout(pad=2.0)
st.pyplot(fig, width="stretch")
plt.close(fig)

# ----------------------------------
# EXPLANATION
# ----------------------------------
explanation_title = "📚 Student's $t$-verdeling"
explanation_markdown = rf"""
## 📌 Wat laat de grafiek zien?
 
De grafiek toont twee kansdichtheidsfuncties naast elkaar:
 
- **Goud** — de standaardnormale verdeling $\mathcal{{N}}(0,1)$: symmetrisch, klokvormig, en
  volledig bepaald door gemiddelde 0 en standaardafwijking 1.
- **Magenta** — de $t$-verdeling met df $= {df}$ vrijheidsgraden: ook symmetrisch en klokvormig, maar met
  **dikkere staarten** en een **lager piekpunt**. De $t$-verdeling is breder, omdat het gebruikt wordt indien ook de standaardafwijking $\sigma$ van een populatie onbekend is.
  Deze moet dan met behulp van een steekproef geschat worden, wat toch nog meer onzekerheid leidt.
  Het totale oppervlak onder beide krommen is gelijk aan 1 (het zijn kansverdelingen), dus wat de $t$-verdeling "verliest" in het midden
  compenseert ze in de staarten.
- **Betrouwbaarheid normale benadering** - we verliezen een klein beetje betrouwbaarheid als we de kritieke grenzen van de normale verdeling gebruikt in plaats van de $t$-verdeling. 
Deze betrouwbaarheid is de kans dat de $t$-verdeling met df $={df}$ vrijheidsgraden een waarde tussen de kritieke grenzen van de normale verdeling aanneemt.
 
De **stippellijnen** markeren de kritieke waarden: het punt waarbuiten je $H_0$ verwerpt.
Het gekleurde oppervlak in de staarten is het kritieke gebied van grootte $\alpha$ ($\alpha/2$ in de linkerstaart en $\alpha/2$ in de rechterstaart).
 
Merk op wat er visueel gebeurt als je df vergroot:
- De $t$-verdeling schuift omhoog en de staarten worden dunner.
- De kritieke waarden van $t$ naderen die van $z$.
- Bij $\text{{df}} \geq 30$ zijn de krommen vrijwel niet meer van elkaar te onderscheiden. Dit is de reden waar de vuistregel van $n = 30$ op gebaseerd is.

⚠️ Technisch gezien zou je bij een onbekende standaardafwijking $\sigma$ altijd de $t$-verdeling moeten gebruiken (ook voor steekproefgroottes $n \ge 30$).
De verschillen met de normale verdeling zijn echter dusdanig kleiner dat we de normale benadering kunnen gebruiken.

 
De $t$-verdeling ontstaat omdat je $\sigma$ niet kent en schat met $s$. Die schatting heeft
zelf ook variabiliteit — bij kleine $n$ is $s$ onbetrouwbaar en moeten de staarten dikker zijn
om die extra onzekerheid te modelleren.
 
---
 
## ❓ Wanneer gebruik je de $t$-verdeling?
 
| Situatie | $\sigma$ | $n$ | Gebruik | Reden |
|---|---|---|---|---|
| Populatiestandaardafwijking is bekend | Bekend | Willekeurig | $\mathcal{{N}}(0,1)$ | Geen schattingsonzekerheid |
| $\sigma$ onbekend, grote steekproef | Onbekend | $\geq 30$ | $t$ (of $z$ als benadering) | $s \approx \sigma$ bij grote $n$, maar $t$ is altijd correct |
| $\sigma$ onbekend, kleine steekproef | Onbekend | $< 30$ | $t$ verplicht | $s$ is onbetrouwbaar; $t$ modelleert de extra onzekerheid |
| Populatie sterk niet-normaal | Onbekend | $< 30$ | Niet-parametrische toets | Aanname normaliteit geschonden |
 
> **Praktische vuistregel:** gebruik altijd de $t$-toets als $\sigma$ onbekend is. De $z$-toets
> is alleen correct als $\sigma$ écht bekend is — wat in de praktijk zelden voorkomt.
 
---
 
## 🧮 Toetsingsgrootheid
 
Bij een éénsteekproef $t$-toets toets je $H_0: \mu = \mu_0$ versus een alternatieve hypothese.
De toetsingsgrootheid is:
 
$$
    t = \frac{{\bar{{x}} - \mu_0}}{{s / \sqrt{{n}}}}
$$
 
Onder $H_0$ volgt $t$ een $t$-verdeling met $\text{{df}} = n - 1$ vrijheidsgraden.
De noemer $s / \sqrt{{n}}$ is de **standaardfout** van het steekproefgemiddelde: hoe nauwkeurig
$\bar{{x}}$ het populatiegemiddelde schat.
 
We verwerpen $H_0$ (tweezijdig) als $|t| > t_{{crit}}$, waarbij:
 
$$
    t_{{\text{{crit}}}} = t_{{1-\alpha/2,\; \text{{df}}={df}}} = {t_crit:.4f}
$$
 
---
 
## 🔢 Rekenvoorbeeld — stap voor stap
 
**Situatie:** $n = {n_ex}$ proefpersonen meten hun reactietijd. We toetsen of de gemiddelde
reactietijd verschilt van $\mu_0 = 300$ ms, bij significantieniveau $\alpha = {alpha}$.
 
Gemeten: $\bar{{x}} = 312$ ms, $s = 24$ ms.
 
---
 
**Stap 1 — Hypothesen opstellen:**
 
$$
H_0: \mu = 300 \quad \text{{versus}} \quad H_1: \mu \neq 300 \quad \text{{(tweezijdig)}}
$$
 
---
 
**Stap 2 — Standaardfout berekenen:**
 
$$
SE = \frac{{s}}{{\sqrt{{n}}}} = \frac{{24}}{{\sqrt{{{n_ex}}}}} = {24 / np.sqrt(n_ex):.4f} \text{{ ms.}}
$$
 
---
 
**Stap 3 — Toetsingsgrootheid berekenen:**
 
$$
t = \frac{{\bar{{x}} - \mu_0}}{{\frac{{s}}{{\sqrt{{n}}}}}} = \frac{{312 - 300}}{{\frac{{24}}{{\sqrt{{{n_ex}}}}}}} \approx {t_score:.4f}.
$$
 
---
 
**Stap 4 — Kritieke waarde opzoeken:**
 
$$
t_{{\text{{crit}}}} = t_{{1 - \alpha/2,\; n-1}} = t_{{1 - {alpha/2},\; {n_ex - 1}}} = {t_crit:.4f}.
$$
 
---
 
**Stap 5 — $p$-waarde berekenen:**
 
De p-waarde is de kans om een $t$ te observeren die minstens zo groot is als de gevonden waarde, gegeven dat $H_0$ waar is:
 
$$
    p = \text{{tcdf}}(\text{{lower}}={t_score:.4f}, \text{{upper}}=10^{{99}}, \text{{df}}={n_ex - 1}) = {(1 - t.cdf(abs(t_score), n_ex - 1)):.4f}.
$$
 
Omdat we tweezijdig toetsen, vergelijken we deze $p$-waarde met $\frac{{\alpha}}{{2}} = {alpha/2}$.
Een kleine $p$-waarde ($p < $\frac{{\alpha}}{{2}}$) betekent dat de gevonden uitkomst onwaarschijnlijk is onder
$H_0$. 
Een grote $p$-waarde betekent **niet** dat $H_0$ waar is, alleen dat er onvoldoende
bewijs is om haar te verwerpen.
 
---
 
**Stap 6 — Conclusie:**
 
$$
|t| = {abs(t_score):.4f} \quad {"<" if not reject else ">"} \quad t_{{\text{{crit}}}} = {t_crit:.4f}
$$
 
{"✅ $H_0$ **niet verwerpen**: er is onvoldoende bewijs dat de reactietijd verschilt van 300 ms." if not reject else "❌ $H_0$ **verwerpen**: er is voldoende bewijs dat de reactietijd significant verschilt van 300 ms."}
 
---
 
## 📏 Betrouwbaarheidsinterval
 
Een $t$-toets en een betrouwbaarheidsinterval zijn twee kanten van dezelfde medaille.
Het $(1 - \alpha)$-betrouwbaarheidsinterval voor $\mu$ is:
 
$$
\bar{{x}} \pm t_{{\text{{crit}}}} \cdot \frac{{s}}{{\sqrt{{n}}}}
= 312 \pm {t_crit:.4f} \cdot {24 / np.sqrt(n_ex):.4f}
= \left[{312 - t_crit * 24 / np.sqrt(n_ex):.2f},\; {312 + t_crit * 24 / np.sqrt(n_ex):.2f}\right] \text{{ ms}}
$$
 
{"✅ $\\mu_0 = 300$ ms **valt binnen** dit interval — consistent met het niet-verwerpen van $H_0$." if not reject else "❌ $\\mu_0 = 300$ ms **valt buiten** dit interval — consistent met het verwerpen van $H_0$."}
 
> Het betrouwbaarheidsinterval geeft extra informatie die de toets niet geeft: niet alleen
> *of* er een verschil is, maar ook *hoe groot* dat verschil plausibel is.
"""

show_explanation(explanation_title, explanation_markdown)