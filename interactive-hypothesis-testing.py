import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm
from utils.explanation_utils import show_explanation

def css_to_rgba(css_color, alpha=0.4):
    from matplotlib.colors import to_rgb
    r,g,b = [int(c*255) for c in to_rgb(css_color)]
    return f"rgba({r},{g},{b},{alpha})"

# Paginalay-out instellen op breed
st.set_page_config(
    page_title="Visualisatie van hypothesetoetsen met de normale verdeling",
    initial_sidebar_state="expanded",
    layout="wide"
)

# ----------------------------------
# PARAMETERS
# ----------------------------------

st.title("📊 Hypothesetoetsen voor het gemiddelde $\\mu$ van een normale verdeling")
with st.sidebar:
    st.header("Parameters")

    test_type = st.selectbox("Toetstype:", ['tweezijdig', 'linkszijdig', 'rechtszijdig'])
    mu_0 = st.number_input("Gemiddelde $\\mu_0$ (nulhypothese):", value=0.0)
    sigma = st.number_input("Standaardafwijking ($\\sigma$):", min_value=0.0, value=1.0)

    if test_type == "tweezijdig":
        minmu, maxmu = mu_0 - sigma, mu_0 + sigma
    elif test_type == "rechtszijdig":
        minmu, maxmu = mu_0, mu_0 + sigma
    else:
        minmu, maxmu = mu_0 - sigma, mu_0
    mu_1 = st.number_input("Gemiddelde $\\mu_1$ (alternatieve hypothese):", min_value=minmu, max_value=maxmu, value=(minmu + maxmu)/2 if test_type != "tweezijdig" else mu_0+1) # min_value=minmu, max_value=maxmu, value=mu_0+1 if test_type == "tweezijdig" else value, step=1)
    alpha = st.number_input("Significantieniveau ($\\alpha$):", min_value=0.001, max_value=0.2, value=0.05)
    sample_size = st.number_input("Steekproefgrootte ($n$):", min_value=1, value=30)

# -------------------------------
# SAMPLING
# -------------------------------

def draw_normal_distribution(mu_0, sigma, mu_1, sample_size):
    sample_std = sigma / np.sqrt(sample_size)
    minmu = min(mu_0, mu_1)
    maxmu = max(mu_0, mu_1)

    x = np.linspace(minmu - 4 * sample_std, maxmu + 4 * sample_std, 1_000)
    
    pdf_H0 = norm.pdf(x, mu_0, sample_std)
    pdf_H1 = norm.pdf(x, mu_1, sample_std)
    
    return x, pdf_H0, pdf_H1

# -------------------------------
# PLOTTING
# -------------------------------

acceptable_color = "springgreen" # "neongreen"
critical_color = "tomato" # "tomato red"
H0_color = "cyan" # "cyan"
H1_color = "gold" # "gold"
opacity = 1

x, pdf_H0, pdf_H1 = draw_normal_distribution(mu_0, sigma, mu_1, sample_size)

# Draw horizontal lines indicating the regions
xmin, xmax = x[0], x[-1]
ymax = max(pdf_H0)
ytext = -0.2 * ymax  # Position for the horizontal line 
ymu = 1/2 * ymax
ylines = 1/2 * ytext
sample_std = sigma / np.sqrt(sample_size)



fig = go.Figure()

# Add the normal distribution function under the null hypothesis H0 with H0_color, and an annotation for the mean
fig.add_trace(go.Scatter(
    x=x,
    y=pdf_H0,
    mode='lines',
    line=dict(color=H0_color),
    opacity=opacity,
    showlegend=False
))

# Add the normal distribution function under the alternative hypothesis H1 with H1_color, and an annotation for the mean
fig.add_trace(go.Scatter(
    x=x,
    y=pdf_H1,
    mode='lines',
    line=dict(color=H1_color),
    opacity=opacity,
    showlegend=False
))

fig.add_vline(x=mu_0, line=dict(color=H0_color, dash='dash'), opacity=opacity, name="Gemiddelde onder H0 ($\\mu_0$)")
fig.add_vline(x=mu_1, line=dict(color=H1_color, dash='dash'), opacity=opacity, name="Gemiddelde onder H1 ($\\mu_1$)")

fig.add_annotation(
    x=mu_0 - 1/4 * sample_std,
    xanchor="left",
    y=1/3 * ymax,
    text="&mu;<sub>0</sub>",
    font=dict(color=H0_color, size=25),
)
fig.add_annotation(
    x=mu_1 - 1/4 * sample_std,
    xanchor="left",
    y=2/3 * ymax,
    text="&mu;<sub>1</sub>",
    font=dict(color=H1_color, size=25),
)


# ----------------------------------
# TWEEZIJDIGE TOETS
# ----------------------------------

if test_type == "tweezijdig":
    z_alpha = norm.ppf(1 - alpha / 2)
    left = mu_0 - z_alpha * sample_std
    right = mu_0 + z_alpha * sample_std

    beta = norm.cdf(right, loc=mu_1, scale=sample_std) - norm.cdf(left, loc=mu_1, scale=sample_std)

    mask_left = (x < left) 
    mask_right = (x > right)
    mask_acceptable = (x >= left) & (x <= right)

    # Shade the type-I error region under H0
    for mask in [mask_left, mask_right]:
        fig.add_trace(go.Scatter(
            x=x[mask],
            y=pdf_H0[mask],
            fill='tozeroy',
            fillcolor=css_to_rgba(critical_color, alpha=0.2),
            opacity=opacity,
            showlegend=False,
        ))

    # Shade the type-II error region under H1
    fig.add_trace(go.Scatter(
        x=x[mask_acceptable],
        y=pdf_H1[mask_acceptable],
        fill='tozeroy',
        fillcolor=css_to_rgba(H1_color, alpha=0.2),
        showlegend=False,
    ))

    # Draw lines indicating the critical and acceptable regions
    fig.add_trace(go.Scatter(
        x=[xmin, left],
        y=[ylines, ylines],
        mode='lines',
        line=dict(color=critical_color, width=10),
        showlegend=False,
    ))

    fig.add_trace(go.Scatter(
        x=[left, right],
        y=[ylines, ylines],
        mode='lines',
        line=dict(color=acceptable_color, width=10),
        showlegend=False,
    ))

    fig.add_trace(go.Scatter(
        x=[right, xmax],
        y=[ylines, ylines],
        mode='lines',
        line=dict(color=critical_color, width=10),
        showlegend=False,
    ))

    # fig.add_vline(x=left, line_color="red")
    # fig.add_vline(x=right, line_color="red")

# --------------------------------------------------
# Rechtszijdig
# --------------------------------------------------

elif test_type == "rechtszijdig":
    z = norm.ppf(1 - alpha)
    right = mu_0 + z * sample_std
    beta = norm.cdf(right, mu_1, sample_std)
    mask_right = (x > right)
    mask_acceptable = (x <= right)

    # Shade the type-I error region under H0
    fig.add_trace(go.Scatter(
        x=x[mask_right],
        y=pdf_H0[mask_right],
        fill='tozeroy',
        fillcolor=css_to_rgba(critical_color, alpha=0.2),
        opacity=opacity,
        showlegend=False,
    ))
    
    # Shade the type-II error region under H1
    fig.add_trace(go.Scatter(
        x=x[mask_acceptable],
        y=pdf_H1[mask_acceptable],
        fill='tozeroy',
        fillcolor=css_to_rgba(H1_color, alpha=0.2),
        showlegend=False,
    ))

    # Draw lines indicating the critical and acceptable regions
    fig.add_trace(go.Scatter(
        x=[xmin, right],
        y=[ylines, ylines],
        mode='lines',
        line=dict(color=acceptable_color, width=10),
        showlegend=False,
    ))

    fig.add_trace(go.Scatter(
        x=[right, xmax],
        y=[ylines, ylines],
        mode='lines',
        line=dict(color=critical_color, width=10),
        showlegend=False,
    ))

    # fig.add_vline(x=right, line_color="red")

# --------------------------------------------------
# Linkszijdig
# --------------------------------------------------

elif test_type == "linkszijdig":
    z = norm.ppf(alpha)
    left = mu_0 + z * sample_std
    beta = 1 - norm.cdf(left, mu_1, sample_std)
    mask_left = (x < left)
    mask_acceptable = (x >= left)

    # Shade the type-I error region under H0
    fig.add_trace(go.Scatter(
        x=x[mask_left],
        y=pdf_H0[mask_left],
        fill='tozeroy',
        fillcolor=css_to_rgba(critical_color, alpha=0.2),
        opacity=opacity,
        showlegend=False,
    ))
    
    # Shade the type-II error region under H1
    fig.add_trace(go.Scatter(
        x=x[mask_acceptable],
        y=pdf_H1[mask_acceptable],
        fill='tozeroy',
        fillcolor=css_to_rgba(H1_color, alpha=0.2),
        showlegend=False,
    ))

    # Draw lines indicating the critical and acceptable regions
    fig.add_trace(go.Scatter(
        x=[xmin, left],
        y=[ylines, ylines],
        mode='lines',
        line=dict(color=critical_color, width=10),
        showlegend=False,
    ))

    fig.add_trace(go.Scatter(
        x=[left, xmax],
        y=[ylines, ylines],
        mode='lines',
        line=dict(color=acceptable_color, width=10),
        showlegend=False,
    ))

    # fig.add_vline(x=left, line_color="red")

# # Add the means mu0 and mu1 as vertical dashed lines
# for i, (mu, color) in enumerate([(mu_0, H0_color), (mu_1, H1_color)]):
#     fig.add_trace(go.Scatter(
#         x=[mu, mu],
#         y=[0, norm.pdf(mu, mu, sigma / np.sqrt(sample_size))],
#         mode='lines',
#         line=dict(color=color, dash='dash'),
#         opacity=opacity,
#         showlegend=False
#     ))
#     fig.add_annotation(
#         x=mu,
#         xanchor="left",
#         y=ymu,
#         text=f"&mu;<sub>{i}</sub>",
#         font=dict(color=color, size=25),
#     )

#     fig.add_annotation(
#         x=mu,
#         y=1.1 * norm.pdf(mu, mu, sigma / np.sqrt(sample_size)),
#         text=f"N(&mu;<sub>{i}</sub>, &#963; / &#8730; n)",
#         font=dict(color=color, size=25)
#     )


# if test_type == "tweezijdig":
#     fig.update_layout(
#         title = dict(
#             text=f"Tweezijdige toets met H<sub>0</sub>: &mu; = &mu;<sub>0</sub> versus H<sub>1</sub>: &mu; &#x2260; &mu;<sub>0</sub>",
#             font=dict(size=40),
#         )
#     )

#     z_alpha = norm.ppf(1 - alpha / 2)
#     critical_value_left = mu_0 - z_alpha * sample_std
#     critical_value_right = mu_0 + z_alpha * sample_std

#     mask_critical = (x < critical_value_left) | (x > critical_value_right)
#     mask_acceptable = (x >= critical_value_left) & (x <= critical_value_right)

# elif test_type == "rechtszijdig":
#     fig.update_layout(
#         title = dict(
#             text=f"Rechtszijdige toets met H<sub>0</sub>: &mu; &#8804; &mu;<sub>0</sub> versus H<sub>1</sub>: &mu; > &mu;<sub>0</sub>",
#             font=dict(size=40),
#         )
#     )
# elif test_type == "linkszijdig":
#     fig.update_layout(
#         title = dict(
#             text=f"Linkszijdige toets met H<sub>0</sub>: &mu; &#8805; &mu;<sub>0</sub> versus H<sub>1</sub>: &mu; < &mu;<sub>0</sub>",
#             font=dict(size=40),
#         )
#     )

# fig.add_trace(go.Scatter(
#     x=x,
#     y=pdf_H0,
#     mode='lines',
#     line=dict(color=H0_color),
#     opacity=opacity,
#     showlegend=False
# ))

# fig.add_trace(go.Scatter(
#     x=x[mask_critical],
#     y=pdf_H0[mask_critical],
#     mode='lines',
#     line=dict(color=critical_color),
#     fill='tozeroy',
#     opacity=opacity,
#     name=f'Type I fout (&#945;): {alpha:.3f}'
# ))


# # fig.add_trace(go.Scatter(
# #     x=[mu_0, mu_0],
# #     y=[0, norm.pdf(mu_0, mu_0, sigma / np.sqrt(sample_size))],
# #     mode='lines',
# #     line=dict(color=H0_color, dash='dash'),
# #     opacity=opacity,
# #     showlegend=False
# # ))

# # fig.add_annotation(
# #     x=mu_0,
# #     xanchor="left",
# #     y=ymu,
# #     text="&mu;<sub>0</sub>",
# #     font=dict(color=H0_color, size=25),
# # )

# # fig.add_annotation(
# #     x=mu_0,
# #     y=1.03 * norm.pdf(mu_0, mu_0, sigma / np.sqrt(sample_size)),
# #     text=r"N(&mu;<sub>0</sub>, &#963; / &#8730; n)",
# #     font=dict(color=H0_color, size=25)
# # )

# # # Add the normal distribution curve for H1 with gold color, and an annotation
# # fig.add_trace(go.Scatter(
# #     x=x,
# #     y=pdf_H1,
# #     mode='lines',
# #     line=dict(color=H1_color),
# #     opacity=opacity,
# #     showlegend=False
# # ))

# # fig.add_trace(go.Scatter(
# #     x=[mu_1, mu_1],
# #     y=[0, norm.pdf(mu_1, mu_1, sigma / np.sqrt(sample_size))],
# #     mode='lines',
# #     line=dict(color=H1_color, dash='dash'),
# #     opacity=opacity,
# #     showlegend=False
# # ))

# # fig.add_annotation(
# #     x=mu_1,
# #     xanchor="left",
# #     y=ymu,
# #     text="&mu;<sub>1</sub>",
# #     font=dict(color=H1_color, size=25),
# # )

# # fig.add_annotation(
# #     x=mu_1,
# #     y=1.1 * norm.pdf(mu_1, mu_1, sigma / np.sqrt(sample_size)),
# #     text=r"N(&mu;<sub>1</sub>, &#963; / &#8730; n)",
# #     font=dict(color=H1_color, size=25)
# # )

# # fig.update_layout(
# #     xaxis = dict(
# #         title=dict(text="x", font=dict(size=30)),
# #         tickfont=dict(size=30),    
# #     ),
# #     yaxis = dict(
# #         title=dict(text="Kansdichtheidsfunctie f(x)", font=dict(size=30)),
# #         tickfont=dict(size=30),    
# #     ),
# # )

# # if test_type == "tweezijdig":
# #     z_alpha = norm.ppf(1 - alpha / 2)
# #     critical_value_left = mu_0 - z_alpha * sigma / np.sqrt(sample_size)
# #     critical_value_right = mu_0 + z_alpha * sigma / np.sqrt(sample_size)

# #     mask_critical = (x < critical_value_left) | (x > critical_value_right)
# #     mask_acceptable = (x >= critical_value_left) & (x <= critical_value_right)

# #     fig.add_trace(go.Scatter(
# #         x=x[mask_critical],
# #         y=pdf_H0[mask_critical],
# #         mode='lines',
# #         line=dict(color=critical_color),
# #         fill='tonexty',
# #         opacity=opacity,
# #         name=f'Type I fout (&#945;): {alpha:.3f}'
# #     ))
# # if test_type == "tweezijdig":
# #     # Kritieke waarde onder H0 (voor tweezijdige toets)
# #     z_alpha = norm.ppf(1 - alpha / 2)
# #     critical_value_left = mu_0 - z_alpha * sample_std
# #     critical_value_right = mu_0 + z_alpha * sample_std
# #     axes[0].fill_between(x, 0, pdf_H0, where=((x < critical_value_left) | (x > critical_value_right)), color=critical_color, alpha=opacity, label=f'Type I fout ($\\alpha$): {alpha:.3f}')

# #     # Bereken de type II fout en arceer de bijbehorende oppervlakte
# #     beta = norm.cdf(critical_value_right, loc=mu_1, scale=sample_std) - norm.cdf(critical_value_left, loc=mu_1, scale=sample_std)
# #     axes[0].fill_between(x, 0, pdf_H1, where=((x < critical_value_right) & (x > critical_value_left)), color=H1_color, alpha=opacity, label=f'Type II fout ($\\beta$): {beta:.3f}')

# #     # Teken de grenzen van het kritieke gebied
# #     axes[0].plot([critical_value_left, critical_value_left], [0, norm.pdf(critical_value_left, mu_0, sample_std)], color=critical_color, linestyle='-')#, label='Kritieke grens links')
# #     axes[0].plot([critical_value_right, critical_value_right], [0, norm.pdf(critical_value_right, mu_0, sample_std)], color=critical_color, linestyle='-')#, label='Kritieke grens rechts')

# #     # Teken het acceptatiegebied
# #     axes[0].hlines(ylines, critical_value_left, critical_value_right, color=acceptable_color, linewidth=5)
# #     axes[0].text((critical_value_left + critical_value_right) / 2, ytext, 'Accepteer $H_0$', color=acceptable_color, fontsize=11, ha='center')

# #     # Teken het kritieke gebied
# #     axes[0].hlines(ylines, xmin, critical_value_left, color=critical_color, linewidth=5, label=f"Kritiek gebied: $(-\\infty; {critical_value_left:.2f}]$ en $[{critical_value_right:.2f}; \\infty)$")
# #     axes[0].hlines(ylines, critical_value_right, xmax, color=critical_color, linewidth=5)
# #     axes[0].text((critical_value_left + xmin) / 2, ytext, 'Verwerp $H_0$', color=critical_color, fontsize=11, ha='center')
# #     axes[0].text((critical_value_right + xmax) / 2, ytext, 'Verwerp $H_0$', color=critical_color, fontsize=11, ha='center')

# #     plt.suptitle(f'Tweezijdige hypothesetoets: $H_0$: $\\mu={mu_0}$ vs. $H_1$: $\\mu \\neq {mu_0}$')

# # elif test_type == "rechtszijdig":
# #     z_alpha = norm.ppf(1 - alpha)
# #     critical_value_right = mu_0 + z_alpha * sample_std
# #     axes[0].fill_between(x, 0, pdf_H0, where=(x > critical_value_right), color=critical_color, alpha=opacity, label=f'Type I fout ($\\alpha$): {alpha:.3f}')

# #     # Bereken de type II fout en arceer de bijbehorende oppervlakte
# #     beta = norm.cdf(critical_value_right, loc=mu_1, scale=sample_std)
# #     axes[0].fill_between(x, 0, pdf_H1, where=(x < critical_value_right), color=H1_color, alpha=opacity, label=f'Type II fout ($\\beta$): {beta:.3f}')

# #     # Teken de grens van het kritieke gebied
# #     axes[0].plot([critical_value_right, critical_value_right], [0, norm.pdf(critical_value_right, mu_0, sample_std)], color=critical_color, linestyle='-')#, label='Kritieke grens rechts')

# #     # Teken het acceptatiegebied
# #     axes[0].hlines(ylines, xmin, critical_value_right, color=acceptable_color, linewidth=5)
# #     axes[0].text((xmin + critical_value_right) / 2, ytext, 'Accepteer $H_0$', color=acceptable_color, fontsize=11, ha='center')

# #     # Teken het kritieke gebied
# #     axes[0].hlines(ylines, critical_value_right, xmax, color=critical_color, linewidth=5, label=f"Kritiek gebied: $[{critical_value_right:.2f}; \\infty)$")
# #     axes[0].text((critical_value_right + xmax) / 2, ytext, 'Verwerp $H_0$', color=critical_color, fontsize=11, ha='center')
        
# #     plt.suptitle(f'Rechtszijdige hypothesetoets: $H_0$: $\\mu\\leq{mu_0}$ vs. $H_1$: $\\mu > {mu_0}$')

# # else: # linkszijdig
# #     z_alpha = norm.ppf(alpha)
# #     critical_value_left = mu_0 + z_alpha * sample_std
# #     axes[0].fill_between(x, 0, pdf_H0, where=(x < critical_value_left), color=critical_color, alpha=opacity, label=f'Type I fout ($\\alpha$): {alpha:.3f}')

# #     # Bereken de type II fout en arceer de bijbehorende oppervlakte
# #     beta = norm.cdf(critical_value_left, loc=mu_1, scale=sample_std)
# #     axes[0].fill_between(x, 0, pdf_H1, where=(x > critical_value_left), color=H1_color, alpha=opacity, label=f'Type II fout ($\\beta$): {beta:.3f}')

# #     # Teken de grens van het kritieke gebied
# #     axes[0].plot([critical_value_left, critical_value_left], [0, norm.pdf(critical_value_left, mu_0, sample_std)], color=critical_color, linestyle='-')#, label='Kritieke grens rechts')

# #     # Teken het acceptatiegebied
# #     axes[0].hlines(ylines, critical_value_left, xmax, color=acceptable_color, linewidth=5)
# #     axes[0].text((critical_value_left + xmax) / 2, ytext, 'Accepteer $H_0$', color=acceptable_color, fontsize=11, ha='center')

# #     # Teken het kritieke gebied
# #     axes[0].hlines(ylines, xmin, critical_value_left, color=critical_color, linewidth=5, label=f"Kritiek gebied: $(-\\infty; {critical_value_left:.2f}]$")
# #     axes[0].text((xmin + critical_value_left) / 2, ytext, 'Verwerp $H_0$', color=critical_color, fontsize=11, ha='center')

# #     plt.suptitle(f'Linkszijdige hypothesetoets: $H_0$: $\\mu\\geq{mu_0}$ vs. $H_1$: $\\mu < {mu_0}$')

# #     axes[0].legend(loc='center left', bbox_to_anchor=(1, 0.5), ncol=1)
# # # slider_dict = add_sidebar_hypothesis_testing()

if test_type == "tweezijdig":
    fig.update_layout(
        title = dict(
            text=f"Tweezijdige toets met H<sub>0</sub>: &mu; = &mu;<sub>0</sub> versus H<sub>1</sub>: &mu; &#x2260; &mu;<sub>0</sub>  (Type-I fout (&#945;): {alpha:.3f} | Type-II fout (&#946;): {beta:.3f})",
            font=dict(size=35),
        )
    ) 
elif test_type == "linkszijdig":
    fig.update_layout(
        title = dict(
            text=f"Linkszijdige toets met H<sub>0</sub>: &mu; &#8805; &mu;<sub>0</sub> versus H<sub>1</sub>: &mu; < &mu;<sub>0</sub> (Type-I fout (&#945;): {alpha:.3f} | Type-II fout (&#946;): {beta:.3f})",
            font=dict(size=35),
        )
    )
elif test_type == "rechtszijdig":
    fig.update_layout(
        title = dict(
            text=f"Rechtszijdige toets met H<sub>0</sub>: &mu; &#8804; &mu;<sub>0</sub> versus H<sub>1</sub>: &mu; > &mu;<sub>0</sub> (Type-I fout (&#945;): {alpha:.3f} | Type-II fout (&#946;): {beta:.3f})",
            font=dict(size=35),
        )
    )  


fig.update_layout(
    xaxis = dict(
        title=dict(text="x", font=dict(size=30)),
        tickfont=dict(size=20),
    ),
    yaxis = dict(
        title=dict(text="Kansdichtheidsfunctie f(x)", font=dict(size=30)),
        tickfont=dict(size=20),
    ),
    height=800
)

st.plotly_chart(fig, use_container_width=True, config=dict(displayModeBar=False, mathjax="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"))

explanation_title = "📚 Uitleg: hypothesetoetsen"
explanation_md=r"""
# 📊 Interactieve Streamlit Webapp: Hypothesetoetsing

Deze interactieve webapp toont de werking van **hypothesetoetsen voor het populatiegemiddelde** $\mu$, inclusief visualisatie van:

-  Type-I fout ($\alpha$)
-  Type-II fout ($\beta$)
-  Acceptatie- en kritieke gebieden

## ⚙️ Functionaliteiten

Met de webapp kun je onderstaande parameters instellen via een **sidebar**:

-  **Toetstype:** tweezijdig, linkszijdig of rechtszijdig (dit geeft het teken "\neq", "<" of ">" aan in de alternatieve hypothese).
-  **Nulhypothese-gemiddelde** $\mu_0$
-  **Alternatieve hypothese** $\mu_1$
-  **Standaardafwijking** $\sigma$
-  **Significantieniveau** $\alpha$
-  **Steekproefgrootte** $n$

## 🧠 Uitleg: hypothesetoetsing

### 📌 Wat laat de grafiek zien?

- De **cyaanblauwe kromme** is de kansverdeling onder $H_0$, d.w.z. $\bar{X} \sim N(\mu_0, \frac{\sigma}{\sqrt{n}})$.
- Het **lichtgroene interval** onder de grafiek toont het **acceptatiegebied**.
- De **rode intervallen** tonen het **kritieke gebied**, afhankelijk van de gekozen toets.
- De **goudgele kromme** stelt de kansverdeling onder de alternatieve hypothese $H_1$ voor.
- Het **rood gearceerde oppervlak** geeft de kans op een **type-I fout** ($\alpha$) weer.
- Het ** geel gearceerde oppervlak** geeft de kans op een **type-II fout** ($\beta$) weer.

### 🧩 Interpretatie

-  **Type-I fout ($\alpha$):** de kans dat we $H_0$ onterecht verwerpen.
-  **Type-II fout ($\beta$):** de kans dat we $H_0$ niet verwerpen terwijl $H_1$ waar is.
- ✅ **Onderscheidend vermogen van de toets:** $1 - \beta$

### 🧮 Invloeden op het onderscheidend vermogen

- Kleinere afstand tussen $\mu_0$ en $\mu_1$ $\rightarrow$ lager onderscheidend vermogen $1 - \beta$
- Grotere standaardafwijking $\sigma$ $\rightarrow$ lager onderscheidend vermogen $1 - \beta$
- Grotere steekproefgrootte $n$ $\rightarrow$ hoger onderscheidend vermogen $1 - \beta$
- Grotere $\alpha$ $\rightarrow$ hoger onderscheidend vermogen $1 - \beta$ (omdat we de kans op een type-I fout verhogen, en daardoor de kans op een type-II fout $\beta$ verlagen)
"""

# Call show_explanation with the plot_hypothesis_testing function
show_explanation(explanation_title, explanation_md)


