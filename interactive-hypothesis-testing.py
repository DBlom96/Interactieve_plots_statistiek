import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy.stats import norm
from dataclasses import dataclass

from utils.explanation_utils import show_explanation
from utils.streamlit_utils import load_css, page_header, apply_dark_style
from utils.constants import *

st.set_page_config(
    page_title="Hypothesetoetsen met de normale verdeling",
    initial_sidebar_state="expanded",
    layout="wide"
)

# ----------------------------------
# CSS
# ----------------------------------
load_css()

BG_COLOR = "#1a1f2e"

# ----------------------------------
# DATA CLASSES
# ----------------------------------
@dataclass
class TestRegions:
    left:  float | None
    right: float | None
    beta:  float

# ----------------------------------
# STATISTICS
# ----------------------------------
@st.cache_data
def generate_distributions(mu0, mu1, sigma, n, points=600):
    sample_std = sigma / np.sqrt(n)
    spread     = abs(mu1 - mu0) + 4 * sample_std
    x          = np.linspace(mu0 - spread, mu0 + spread, points)
    return x, norm.pdf(x, mu0, sample_std), norm.pdf(x, mu1, sample_std), sample_std


def compute_regions(test_type, mu0, mu1, sample_std, alpha):
    if test_type == "tweezijdig":
        z     = norm.ppf(1 - alpha / 2)
        left  = mu0 - z * sample_std
        right = mu0 + z * sample_std
        beta  = norm.cdf(right, mu1, sample_std) - norm.cdf(left, mu1, sample_std)
    elif test_type == "rechtszijdig":
        z     = norm.ppf(1 - alpha)
        left  = None
        right = mu0 + z * sample_std
        beta  = norm.cdf(right, mu1, sample_std)
    else:  # linkszijdig
        z     = norm.ppf(1 - alpha)
        left  = mu0 - z * sample_std
        right = None
        beta  = 1 - norm.cdf(left, mu1, sample_std)
    return TestRegions(left, right, beta)

# ----------------------------------
# PARAMETERS
# ----------------------------------
page_header("📊 Hypothesetoetsen", "Normale verdeling")

with st.sidebar:
    st.header("Parameters")
    test_type = st.selectbox("Toetstype:", ["tweezijdig", "linkszijdig", "rechtszijdig"])
    mu0       = st.number_input(r"Gemiddelde $\mu_0$ (nulhypothese):", value=0.0)
    sigma     = st.number_input(r"Standaardafwijking $\sigma$:", min_value=1e-6, value=1.0)
    n         = st.number_input(r"Steekproefgrootte $n$:", min_value=1, value=30)
    alpha     = st.number_input(r"Significantieniveau $\alpha$:", min_value=0.001, max_value=0.2, value=0.05)
    mu1       = st.number_input(r"Gemiddelde $\mu_1$ (alternatieve hypothese):",
                                min_value=mu0 - 1.0, max_value=mu0 + 1.0,
                                value=mu0 + 0.5)

# ----------------------------------
# COMPUTATIONS
# ----------------------------------
x, pdf0, pdf1, sample_std = generate_distributions(mu0, mu1, sigma, n)
regions = compute_regions(test_type, mu0, mu1, sample_std, alpha)
beta    = regions.beta
power   = 1 - beta
xmin, xmax = x[0], x[-1]
ymax    = max(pdf0)

# ----------------------------------
# STAT CARDS
# ----------------------------------
st.markdown(f"""
<div class="stats-row-3">
  <div class="stat-card alpha">
    <span class="stat-label">Type-I fout</span>
    <span class="stat-value">&alpha; = {alpha:.4f}</span>
    <span class="stat-desc">Kans op onterecht verwerpen van H&#8320;</span>
    <span class="stat-desc">(rood gearceerd gebied)</span>
  </div>
  <div class="stat-card beta">
    <span class="stat-label">Type-II fout</span>
    <span class="stat-value">&beta; = {beta:.4f}</span>
    <span class="stat-desc">Kans op onterecht accepteren van H&#8320;</span>
    <span class="stat-desc">(blauw gearceerd gebied)</span>
  </div>
  <div class="stat-card acceptatie">
    <span class="stat-label">Onderscheidend vermogen</span>
    <span class="stat-value">1 &minus; &beta; = {power:.4f}</span>
    <span class="stat-desc">Kans op correct verwerpen van H&#8320;</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------
# HELPERS
# ----------------------------------
def fill_region(ax, x, y, mask, color, alpha_val=0.35, label=None):
    ax.fill_between(x, y, where=mask, color=color, alpha=alpha_val, label=label)


def add_interval_bar(ax, segments):
    """Draw coloured region bar and labels below x-axis."""
    for x0, x1, color, label in segments:
        ax.plot([x0, x1], [bar_y, bar_y], color=color, linewidth=8,
                solid_capstyle="butt", clip_on=False)
        if label:
            ax.text((x0 + x1) / 2, bar_y - 3.2 * tick_h, label,
                    ha="center", va="top", fontsize=ANNOTATION_FONT_SIZE,
                    color=color, fontfamily="JetBrains Mono")
    for xv in set(v for seg in segments for v in (seg[0], seg[1])):
        ax.plot([xv, xv], [bar_y - tick_h, bar_y + tick_h],
                color=PLOT_FONT_COLOR, linewidth=1, clip_on=False)

# ----------------------------------
# FIGURE
# ----------------------------------
fig, ax = plt.subplots(figsize=(10, 5))

bar_y  = -0.055 * ymax
tick_h = 0.018 * ymax
ytext = bar_y - 2 * tick_h
plt.ylim(bottom=3*bar_y, top=1.1*ymax)

# --- Shaded regions ---
if test_type == "tweezijdig":
    left, right = regions.left, regions.right
    fill_region(ax, x, pdf0, x < left,                    CRITICAL_COLOR,   label=rf"Type-I fout ($\alpha={alpha:.4f}$)")
    fill_region(ax, x, pdf0, x > right,                   CRITICAL_COLOR)
    fill_region(ax, x, pdf1, (x >= left) & (x <= right),  BETA_COLOR,       label=rf"Type-II fout ($\beta={beta:.4f}$)")
    add_interval_bar(ax, [
        (xmin, left,  CRITICAL_COLOR,   "Kritiek gebied"),
        (left,  right, ACCEPTABLE_COLOR, "Acceptatiegebied"),
        (right, xmax,  CRITICAL_COLOR,   "Kritiek gebied"),
    ])

elif test_type == "rechtszijdig":
    right = regions.right
    fill_region(ax, x, pdf0, x > right,  CRITICAL_COLOR, label=rf"Type-I fout ($\alpha={alpha:.4f}$)")
    fill_region(ax, x, pdf1, x <= right, BETA_COLOR,     label=rf"Type-II fout ($\beta={beta:.4f}$)")
    add_interval_bar(ax, [
        (xmin,  right, ACCEPTABLE_COLOR, "Acceptatiegebied"),
        (right, xmax,  CRITICAL_COLOR,   "Kritiek gebied"),
    ])

else:  # linkszijdig
    left = regions.left
    fill_region(ax, x, pdf0, x < left,  CRITICAL_COLOR, label=rf"Type-I fout ($\alpha={alpha:.4f}$)")
    fill_region(ax, x, pdf1, x >= left, BETA_COLOR,     label=rf"Type-II fout ($\beta={beta:.4f}$)")
    add_interval_bar(ax, [
        (xmin, left, CRITICAL_COLOR,   "Kritiek gebied"),
        (left, xmax, ACCEPTABLE_COLOR, "Acceptatiegebied"),
    ])

# --- Curves ---
ax.plot(x, pdf0, color=H0_COLOR, linewidth=2.5,
        label=rf"$H_0$: $\bar{{X}} \sim \mathcal{{N}}(\mu_0={mu0},\, \sigma/\sqrt{{n}})$")
ax.plot(x, pdf1, color=H1_COLOR, linewidth=2.5,
        label=rf"$H_1$: $\bar{{X}} \sim \mathcal{{N}}(\mu_1={mu1},\, \sigma/\sqrt{{n}})$")

# --- Mean dashed lines ---
ax.plot([mu0, mu0], [0, ymax], color=H0_COLOR, linewidth=1.0, linestyle="--", alpha=0.6)
ax.plot([mu1, mu1], [0, ymax], color=H1_COLOR, linewidth=1.0, linestyle="--", alpha=0.6)

# --- Title (two-color) ---
titles = {
    "tweezijdig":    (r"Tweezijdige toets:  ", rf"$H_0: \mu = {mu0}$", " versus ", rf"$H_1: \mu \neq {mu0}$"),
    "rechtszijdig":  (r"Rechtszijdige toets:  ", rf"$H_0: \mu \leq {mu0}$", " versus ", rf"$H_1: \mu > {mu0}$"),
    "linkszijdig":   (r"Linkszijdige toets:  ", rf"$H_0: \mu \geq {mu0}$", " versus ", rf"$H_1: \mu < {mu0}$"),
}
plain_part, H0_part, versus, H1_part = titles[test_type]

apply_dark_style(fig=fig, ax=ax,
                 xlabel=r"$x$",
                 ylabel=r"Kansdichtheid $f(x)$")

ax.text(0.4, 1.02, plain_part,
        transform=ax.transAxes, ha="right", va="center",
        fontsize=TITLE_FONT_SIZE, color=PLOT_FONT_COLOR, fontfamily="JetBrains Mono")
ax.text(0.45, 1.02, H0_part,
        transform=ax.transAxes, ha="center", va="center",
        fontsize=TITLE_FONT_SIZE, color=H0_COLOR, fontfamily="JetBrains Mono")
ax.text(0.58, 1.02, versus,
        transform=ax.transAxes, ha="center", va="center",
        fontsize=TITLE_FONT_SIZE, color=PLOT_FONT_COLOR, fontfamily="JetBrains Mono")
ax.text(0.71, 1.02, H1_part,
        transform=ax.transAxes, ha="center", va="center",
        fontsize=TITLE_FONT_SIZE, color=H1_COLOR, fontfamily="JetBrains Mono")

plt.tight_layout(pad=2.5)
st.pyplot(fig, width="stretch")
plt.close(fig)

# ----------------------------------
# EXPLANATION
# ----------------------------------
explanation_title = "📚 Hypothesetoetsen"
explanation_markdown = r"""
## 📜 Wat is een hypothesetoets?
 
Bij een **hypothesetoets** willen we op basis van steekproefdata een uitspraak doen over een
onbekende populatieparameter — in dit geval het populatiegemiddelde $\mu$. We stellen twee
hypothesen op:
 
- De **nulhypothese** $H_0$: de "status quo", de aanname die we willen toetsen. We gaan er
  standaard vanuit dat $H_0$ waar is, totdat de data voldoende bewijs leveren om haar te verwerpen.
- De **alternatieve hypothese** $H_1$: wat we willen aantonen als $H_0$ niet klopt. Deze hypothese is precies het tegenovergestelde van $H_0$.
 
De toetsprocedure berekent een **toetsingsgrootheid** op basis van de steekproef en vergelijkt
deze met een **kritieke waarde** die afhangt van het gekozen significantieniveau $\alpha$.
 
---
 
## 🔀 Toetstypen
 
Het teken in $H_1$ bepaalt welk toetstype van toepassing is:
 
| Toetstype | $H_0$ | $H_1$ | Kritiek gebied |
|---|---|---|---|
| Tweezijdig | $\mu = \mu_0$ | $\mu \neq \mu_0$ | Beide staarten |
| Rechtszijdig | $\mu \leq \mu_0$ | $\mu > \mu_0$ | Rechterstaart |
| Linkszijdig | $\mu \geq \mu_0$ | $\mu < \mu_0$ | Linkerstaart |
 
Bij een **tweezijdige toets** wordt de kans $\alpha$ gelijk verdeeld over beide staarten
($\alpha/2$ links, $\alpha/2$ rechts). Bij een **eenzijdige toets** zit de volledige $\alpha$ in
één staart.
 
---
 
## ❌ Type-I fout ($\alpha$)
 
Een **type-I fout** treedt op wanneer we $H_0$ **verwerpen terwijl $H_0$ in werkelijkheid waar
is**. Dit is een vals alarm — we concluderen ten onrechte dat er een effect is.
 
$$
    \alpha = P(\text{verwerp } H_0 \mid H_0 \text{ is waar})
$$
 
Het significantieniveau $\alpha$ is precies de kans op een type-I fout. Door $\alpha$ klein te
kiezen (bijv. $0.05$ of $0.01$) houden we dit risico beperkt. In de grafiek is dit het
**rood gearceerde oppervlak** onder de $H_0$-kromme buiten het acceptatiegebied.
 
---
 
## ❌ Type-II fout ($\beta$)
 
Een **type-II fout** treedt op wanneer we $H_0$ **accepteren terwijl $H_0$ in werkelijkheid
niet waar is**. We missen een echt effect — een gemiste detectie.
 
$$
    \beta = P(\text{accepteer } H_0 \mid H_1 \text{ is waar})
$$
 
In de grafiek is dit het **blauw gearceerde oppervlak** onder de $H_1$-kromme binnen het
acceptatiegebied. $\beta$ hangt af van hoe ver $\mu_1$ verwijderd is van $\mu_0$: hoe kleiner
het werkelijke verschil, hoe moeilijker het te detecteren is en hoe groter $\beta$.
 
---
 
## ⚡ Onderscheidend vermogen ($1 - \beta$)
 
Het **onderscheidend vermogen** (Engels: *power*) is de kans dat de toets een werkelijk effect
ook daadwerkelijk detecteert:
 
$$
    \text{power} = 1 - \beta = P(\text{verwerp } H_0 \mid H_1 \text{ is waar})
$$
 
Een goede toets heeft een hoog onderscheidend vermogen. Merk op dat $\alpha$ en $\beta$ met
elkaar in spanning staan: als je $\alpha$ verkleint (strenger criterium), vergroot je doorgaans
$\beta$ — en vice versa. De enige manier om beide tegelijk te verkleinen is een grotere
steekproef $n$.
 
---
 
## 📊 Overzichtstabel van uitkomsten
 
|  | $H_0$ is waar | $H_0$ is niet waar |
|---|---|---|
| **Verwerp $H_0$** | Type-I fout ($\alpha$) | Correct (power $= 1-\beta$) |
| **Accepteer $H_0$** | Correct ($1 - \alpha$) | Type-II fout ($\beta$) |

De rijen corresponderen in dit geval met **beslissingen** die we kunnen nemen op basis van de toetsuitslag van onze hypothesetoets.
De kolommen corresponderen met daadwerkelijke **toestanden** waar we ons in bevinden.
Ons doel is uiteraard om de juiste beslissing te nemen, dat wil zeggen, ofwel $H_0$ accepteren als deze waar blijkt te zijn (linksonder) ofwel $H_0$ verwerpen als deze niet waar blijkt te zijn (rechtsboven).
De kans op een type-I fout kiezen we vast met het significantieniveau $\alpha$. 
We hebben dus alleen nog onzekerheid op de kans op een type-II fout ($\beta$).
Deze kans willen we zo klein mogelijk hebben, oftewel we willen het onderscheidingsvermogen (power) $1 - \beta$ zo groot mogelijk hebben!

---
 
## ⚙️ Invloed van de parameters op het onderscheidend vermogen
 
| Parameter | Effect op $1 - \beta$ |
|---|---|
| Grotere $|\mu_1 - \mu_0|$ | Groter — effect is makkelijker te zien |
| Grotere $\sigma$ | Kleiner — meer ruis maskeert het effect |
| Grotere $n$ | Groter — meer data geeft preciezere schatting |
| Groter $\alpha$ | Groter — ruimer kritiek gebied, maar hogere kans op type-I fout |
 
---
 
## 🧮 Beslissingsregels
 
Bij bekende $\sigma$ is de toetsingsgrootheid $z = \dfrac{\bar{x} - \mu_0}{\sigma / \sqrt{n}}$.
 
**Tweezijdig** ($H_1: \mu \neq \mu_0$): verwerp $H_0$ als $|z| > z_{\alpha/2}$
 
**Rechtszijdig** ($H_1: \mu > \mu_0$): verwerp $H_0$ als $z > z_{\alpha}$
 
**Linkszijdig** ($H_1: \mu < \mu_0$): verwerp $H_0$ als $z < -z_{\alpha}$
 
waarbij $z_{\alpha} = \Phi^{-1}(1 - \alpha)$ de kritieke z-waarde is.
"""
 
show_explanation(explanation_title, explanation_markdown)