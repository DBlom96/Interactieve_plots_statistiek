import matplotlib.pyplot as plt
import mplcyberpunk

def set_plot_style(style_name: str = "cyberpunk") -> None:
    """Stelt de gewenste matplotlib stijl in."""
    plt.style.use(style_name)

def cyberpunk_color_cycle() -> list[str]:
    """Geeft een lijst van kleuren uit in cyberpunk stijl"""
    return [
        "#ff00ff", "#00ff00", "#00ffff", "#ff4500", "#ff1493",
        "#7fff00", "#ff6347", "#ffd700", "#ff69b4", "#ffff00"
    ]