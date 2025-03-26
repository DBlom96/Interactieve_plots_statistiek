import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ipywidgets as widgets
from scipy.stats import norm, uniform, expon, binom, poisson
from IPython.display import display

# Functie om steekproefgemiddelden te genereren
def generate_sample_means(dist, n_samples, sample_size, **params):
    if dist == "normaal":
        samples = norm.rvs(loc=params["mu"], scale=params["sigma"], size=(sample_size, n_samples))
    elif dist == "uniform":
        samples = uniform.rvs(loc=params["a"], scale=params["b"] - params["a"], size=(sample_size, n_samples))
    elif dist == "exponentieel":
        samples = expon.rvs(scale=1/params["lambda_"], size=(sample_size, n_samples))
    elif dist == "binomiaal":
        samples = binom.rvs(n=params["n"], p=params["p"], size=(sample_size, n_samples))
    elif dist == "Poisson":
        samples = poisson.rvs(mu=params["lambda_"], size=(sample_size, n_samples))
    else:
        raise ValueError("Onbekende verdeling")
    
    return samples.mean(axis=0)  # Correcte as voor steekproefgemiddelden

# Functie om de grafiek te plotten
def plot_clt(dist, n_samples, sample_size, **params):
    sample_means = generate_sample_means(dist, n_samples, sample_size, **params)
    
    plt.figure(figsize=(8, 5))
    sns.histplot(sample_means, bins=30, kde=True, color='blue', label="Steekproefgemiddelden")
    
    plt.axvline(np.mean(sample_means), color='red', linestyle='dashed', label=f'Gemiddelde: {np.mean(sample_means):.2f}')
    plt.suptitle(f"Centrale limietstelling: gemiddelden van {dist} verdeelde kansvariabelen")
    plt.title(f'Steekproefgrootte = {sample_size}, Aantal steekproeven = {n_samples}')
    plt.xlabel("Steekproefgemiddelde")
    plt.ylabel("Frequentie")
    plt.legend()
    plt.show()

# Interactieve widgets
dist_selector = widgets.Dropdown(options=["normaal", "uniform", "exponentieel", "binomiaal", "Poisson"], value="normaal", description="Kansverdeling:")
sample_size_slider = widgets.IntSlider(min=1, max=500, step=1, value=30, description="Steekproefgrootte:")
n_samples_slider = widgets.IntSlider(min=1, max=100_000, step=10, value=1000, description="Aantal steekproeven:")

# Specifieke sliders per verdeling
mu_slider = widgets.FloatSlider(min=-10, max=10, step=0.5, value=0, description="Gemiddelde $\\mu$:")
sigma_slider = widgets.FloatSlider(min=0.1, max=5, step=0.1, value=1, description="Standaardafwijking $\\sigma$:")
a_slider = widgets.FloatSlider(min=-10, max=0, step=0.5, value=-5, description="Uniform $a$:")
b_slider = widgets.FloatSlider(min=0, max=10, step=0.5, value=5, description="Uniform $b$:")
lambda_slider = widgets.FloatSlider(min=0.1, max=5, step=0.1, value=1, description="Exponential $\\lambda$:")
n_slider = widgets.IntSlider(min=1, max=100, step=1, value=10, description="Binomiaal $n$:")
p_slider = widgets.FloatSlider(min=0, max=1, step=0.01, value=0.5, description="Binomiaal $p$:")

# Output widget voor sliders
slider_output = widgets.Output()

# Functie om juiste sliders te tonen
def update_sliders(change):
    with slider_output:
        slider_output.clear_output()
        new_dist = change["new"]
        if new_dist == "normaal":
            display(widgets.VBox([mu_slider, sigma_slider]))
        elif new_dist == "uniform":
            display(widgets.VBox([a_slider, b_slider]))
        elif new_dist == "exponentieel":
            display(lambda_slider)
        elif new_dist == "binomiaal":
            display(widgets.VBox([n_slider, p_slider]))
        elif new_dist == "Poisson":
            display(lambda_slider)

# Observer koppelen aan verdeling-keuze
dist_selector.observe(update_sliders, names="value")

# Functie om grafiek te updaten
def update_plot(dist, n_samples, sample_size, mu, sigma, a, b, lambda_, n, p):
    params = {"mu": mu, "sigma": sigma, "a": a, "b": b, "lambda_": lambda_, "n": n, "p": p}
    plot_clt(dist, n_samples, sample_size, **params)

# Interactieve plot
interactive_plot = widgets.interactive_output(update_plot, {
    "dist": dist_selector,
    "n_samples": n_samples_slider,
    "sample_size": sample_size_slider,
    "mu": mu_slider,
    "sigma": sigma_slider,
    "a": a_slider,
    "b": b_slider,
    "lambda_": lambda_slider,
    "n": n_slider,
    "p": p_slider
})

# UI weergeven
display(dist_selector, slider_output, sample_size_slider, n_samples_slider, interactive_plot)

# Eerste sliders tonen
update_sliders({"new": dist_selector.value})