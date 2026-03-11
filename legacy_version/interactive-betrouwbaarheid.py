import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import streamlit as st
from utils.streamlit_utils import generate_streamlit_page
from utils.plot_style import cyberpunk_color_cycle

# Setting up the page layout to wide
st.set_page_config(
    page_title="Visualisatie van betrouwbaarheidsintervallen",
    initial_sidebar_state="expanded",
    layout="wide"
)

# Sidebar function for getting user input
def add_sidebar_confidence_interval():
    with st.sidebar:
        st.header("Sliders voor parameters")
        mu = st.slider("Populatiegemiddelde ($\\mu$, eigenlijk onbekend!)", min_value=60, max_value=140, value=100, step=1)
        sigma = st.slider("Standaardafwijking $\\sigma$", min_value=10, max_value=20, value=15, step=1)
        sample_size = st.slider("Steekproefgrootte $n$", min_value=10, max_value=250, value=100, step=1)
        num_samples = st.slider("Aantal steekproeven", min_value=5, max_value=200, value=10, step=1)
        alpha = st.slider("Significantieniveau", min_value=0.01, max_value=0.10, value=0.05, step=0.01)
    slider_dict = {"mu": mu, "sigma": sigma, "sample_size": sample_size, "num_samples": num_samples, "alpha": alpha} 
    return slider_dict

# Function to plot confidence intervals
def plot_confidence_intervals(axes, user_inputs):
    mu, sigma, sample_size, num_samples, alpha = user_inputs.values()
    z_critical = norm.ppf(1 - alpha / 2)

    count_include_mu = 0
    color_cycle = cyberpunk_color_cycle()
    sample_std = sigma / np.sqrt(sample_size)
    margin_of_error = z_critical * sample_std
    
    for i in range(num_samples):
        sample = np.random.normal(mu, sigma, sample_size)
        sample_mean = np.mean(sample)
        
        ci_left, ci_right = sample_mean - margin_of_error, sample_mean + margin_of_error
        
        if ci_left <= mu <= ci_right:
            count_include_mu += 1
            color = color_cycle[1] # "neongreen"
        else:
            color = color_cycle[6] # "tomato red"

        axes[0].plot([ci_left, ci_right], [i, i], marker="|", color=color)
        axes[0].text(mu + 5 * sample_std, i, f"[{ci_left:.4f}, {ci_right:.4f}]", color=color)
        if i == 0:
            axes[0].scatter(sample_mean, i, color=color, s=100, label="Steekproefgemiddelde")  # Sample mean marker
        else:
            axes[0].scatter(sample_mean, i, color=color, s=100)  # Sample mean marker
    axes[0].axvline(mu, color=color_cycle[2], linestyle="--")
    
    # Update suptitle and title
    axes[0].set_xlim(mu - 6 * sample_std, mu + 6 * sample_std)
    axes[0].set_title(f"Aantal {int(100*(1-alpha))}%-betrouwbaarheidsintervallen dat $\\mu={mu}$ bevat: "
                 f"{count_include_mu} van de {num_samples} ({(count_include_mu / num_samples * 100):.2f}%)", pad=50)
    # axes[0].legend()

    # Reset the figsize
    plt.gcf().set_size_inches(12, 0.2 * num_samples)  # Resize the figure to the desired size

slider_dict = add_sidebar_confidence_interval()

# Generate the Streamlit page with the sidebar and plot
page_header=f"📊 Interactieve plot: betrouwbaarheidsintervallen"
plot_title=f"Visualisatie van betrouwbaarheidsintervallen en het concept van betrouwbaarheid"
xlabel="$x$"
ylabel="Steekproefindex"
explanation_title = "# :book: Uitleg: betrouwbaarheidsintervallen"
explanation_markdown = """
    # 🔢 Betrouwbaarheidsintervallen: Een Conceptuele Uitleg

    ## Wat is een betrouwbaarheidsinterval?
    Een **betrouwbaarheidsinterval** (BI) is een manier om een schatting van een populatieparameter, zoals het gemiddelde, te maken op basis van een steekproef. Het geeft een bereik aan waarbinnen de echte waarde met een bepaalde zekerheid (betrouwbaarheid) ligt.

    Stel dat we een populatie hebben met een onbekend gemiddeld gewicht $\\mu$. Door meerdere steekproeven te nemen, kunnen we een schatting van $\\mu$ maken en daar een onzekerheidsmarge aan koppelen.

    ## 📜 Formule van een betrouwbaarheidsinterval
    Laat $X_1, X_2, \\ldots, X_n$ een theoretische steekproef zijn.
    Een betrouwbaarheidsinterval voor $\\mu$ wordt berekend als:

    $$
    \\text{Steekproefgemiddelde} \\pm \\text{foutmarge}
    $$

    De foutmarge wordt bepaald door:

    $$
    z_{\\alpha/2} \\cdot \\frac{\\sigma}{\\sqrt{n}}
    $$

    - $z_{\\alpha/2}$ is de grenswaarde uit de standaardnormale verdeling $N(0,1)$ waarvoor de rechteroverschrijdingskans $P(Z \\ge z_{\\alpha/2}) = \\alpha/2$.
      Deze grenswaarde is dus afhankelijk van het betrouwbaarheidsniveau $1-\\alpha$.
    - $\\sigma$ is de standaardafwijking van de populatie.
    - $n$ is de steekproefgrootte.

    De formule van het betrouwbaarheidsinterval is dus een **intervalschatter**, omdat verschillende steekproeven een ander interval kunnen geven, oftewel de grenzen van het betrouwbaarheidsintervallen zijn kansvariabelen.

    ## 🔍 Betekenis van het betrouwbaarheidsniveau
    Het **betrouwbaarheidsniveau** (bijvoorbeeld 95%) betekent dat als we **veel** steekproeven nemen en voor elke steekproef het betrouwbaarheidsinterval berekenen, ongeveer **95%** van deze intervallen de echte populatieparameter $\\mu$ zal bevatten.
    Het betrouwbaarheidsniveau noteren we met $1 - \\alpha$, oftewel de kans dat voor een willekeurige steekproef het bijbehorende betrouwbaarheidsinterval de echte populatieparameter zal bevatten.

    Een lager significantieniveau $\\alpha$ betekent een breder interval, maar een lagere fractie van de intervallen die de echte populatieparameter bevatten.
    Een hogere waarde van $\\alpha$ levert een smaller interval op, maar ook een grotere kans om de echte waarde van $\\mu$ mis te lopen.

    ## 📊 Visuele interpretatie
    In een grafische weergave zien we vaak meerdere steekproeven, waarbij:

    - **🔵 de blauwe lijn** de werkelijke populatieparameter aangeeft.
    - **🟢 de groene intervallen** de betrouwbaarheidsintervallen zijn die $\\mu$ wel bevatten. De bolletjes duiden het steekproefgemiddelde aan.
    - **🔴 de rode intervallen** de werkelijke waarde $\\mu$ niet bevatten.

    ## 🚀 Praktische toepassingen
    Betrouwbaarheidsintervallen worden veel gebruikt in wetenschappelijk onderzoek, geneeskunde en marktanalyses, bijvoorbeeld bij:
    - 😊 Het inschatten van gemiddelde klanttevredenheidsscores.
    - 💊 Klinische studies om het effect van een medicijn vast te stellen.
    - 📈 Financiële voorspellingen op basis van economische steekproeven.

    Door betrouwbaarheid op deze manier visueel en mathematisch te interpreteren, krijgen we een krachtig instrument voor statistische besluitvorming. ✨
"""

# Call generate_streamlit_page with the plot_binomiale_verdeling function
generate_streamlit_page(
    slider_dict, 
    plot_confidence_intervals, 
    page_header=page_header,
    plot_title=plot_title,
    xlabel=xlabel, 
    ylabel=ylabel,
    explanation_md=(explanation_title, explanation_markdown),
    subplot_dims=(1, 1)  # Single plot (1x1)
)