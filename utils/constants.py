import tomllib
from matplotlib.colors import to_rgb

PLOT_TYPE="plt"

def css_to_rgba(css_color, alpha = 0.4) -> str:
    """Converteert een CSS-kleur naar een rgba-string voor Plotly."""
    r, g, b = [int(c * 255) for c in to_rgb(css_color)]
    if PLOT_TYPE == "plt":
        return (r/255, g/255, b/255, alpha)
    else:
        return f"rgba({r},{g},{b},{alpha})"
    
# ---------------------------------
# FONTS
# ---------------------------------
FONT_FAMILY = "JetBrains Mono"#, monospace"

TITLE_FONT_SIZE = 16
ANNOTATION_FONT_SIZE = 20
AXIS_FONT_SIZE = 13
TICK_FONT_SIZE = 10
BUTTON_FONT_SIZE = 20


# ---------------------------------
# COLORS
# ---------------------------------

with open("./.streamlit/config.toml", "rb+") as f:
    config = tomllib.load(f)

    # PLOT GENERIC VALUES
    BG_COLOR = config.get("theme", {}).get("backgroundColor", "#141f30")

# CONFIDENCE INTERVALS
OBSERVATION_COLOR = "lavenderblush"
SAMPLE_MEAN_COLOR = "paleturquoise"
INTERVAL_COLOR = "mediumspringgreen"

# PLOTS
PLOT_FONT_COLOR = "lavenderblush"
HISTOGRAM_BAR_COLOR = "steelblue"

# Hypothesetoetsen
H0_COLOR = "gold"
FILL_COLOR = css_to_rgba(H0_COLOR, alpha=0.4)
H1_COLOR = "magenta"
ACCEPTABLE_COLOR = "springgreen"
CRITICAL_COLOR = "tomato"

ALPHA_COLOR = CRITICAL_COLOR
BETA_COLOR = "lightblue"
P_VALUE_COLOR = css_to_rgba(BETA_COLOR, alpha=0.4) # "cyan"
CRITICAL_SHADE_COLOR = css_to_rgba(CRITICAL_COLOR, alpha=0.4)

# Lineaire regressie
POINT_COLOR      = BETA_COLOR
REGRESSION_COLOR = ACCEPTABLE_COLOR
RESIDUAL_COLOR   = CRITICAL_COLOR
CI_COLOR         = H0_COLOR
PI_COLOR         = H1_COLOR
CI_FILL_COLOR    = css_to_rgba(CI_COLOR, 0.4)
PI_FILL_COLOR    = css_to_rgba(PI_COLOR, 0.4)