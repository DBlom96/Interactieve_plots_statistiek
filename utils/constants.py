from utils.streamlit_utils import css_to_rgba

# ---------------------------------
# FONTS
# ---------------------------------
FONT_FAMILY = "JetBrains Mono, monospace"

TITLE_FONT_SIZE = 30
ANNOTATION_FONT_SIZE = 20
AXIS_FONT_SIZE = 25
TICK_FONT_SIZE = 20
BUTTON_FONT_SIZE = 20


# ---------------------------------
# COLORS
# ---------------------------------

# CONFIDENCE INTERVALS
OBSERVATION_COLOR = "lavenderblush"
SAMPLE_MEAN_COLOR = "paleturquoise"
INTERVAL_COLOR = "mediumspringgreen"

# PLOTS
PLOT_FONT_COLOR = "lavenderblush"
HISTOGRAM_BAR_COLOR = "steelblue"

# Hypothesetoetsen
H0_COLOR = "gold"
H1_COLOR = "magenta"
ACCEPTABLE_COLOR = "springgreen"
CRITICAL_COLOR = "tomato"

ALPHA_COLOR = CRITICAL_COLOR
BETA_COLOR = "lightblue"
P_VALUE_COLOR = css_to_rgba(BETA_COLOR, 0.4) # "cyan"
CRITICAL_SHADE_COLOR = css_to_rgba(CRITICAL_COLOR, 0.4)

# Lineaire regressie
POINT_COLOR      = BETA_COLOR
REGRESSION_COLOR = ACCEPTABLE_COLOR
RESIDUAL_COLOR   = CRITICAL_COLOR
CI_COLOR         = H0_COLOR
PI_COLOR         = H1_COLOR
CI_FILL_COLOR    = css_to_rgba(CI_COLOR, 0.4)
PI_FILL_COLOR    = css_to_rgba(PI_COLOR, 0.4)