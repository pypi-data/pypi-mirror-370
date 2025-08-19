"""Computer Split Screen Cross-Platform (Mac & Windows) MCP Server"""

__version__ = "1.2.0"
__author__ = "Beta"

from .window_actions import (
    left_half_window, right_half_window,
    top_half_window, bottom_half_window,
    top_left_quadrant_window, top_right_quadrant_window,
    bottom_left_quadrant_window, bottom_right_quadrant_window,
    left_third_window, middle_third_window, right_third_window,
    left_two_thirds_window, right_two_thirds_window,
    maximise_window, minimise_window, fullscreen_window,
)

__all__ = [
    "__version__",
    "__author__",
    "left_half_window", "right_half_window",
    "top_half_window", "bottom_half_window",
    "top_left_quadrant_window", "top_right_quadrant_window",
    "bottom_left_quadrant_window", "bottom_right_quadrant_window",
    "left_third_window", "middle_third_window", "right_third_window",
    "left_two_thirds_window", "right_two_thirds_window",
    "maximise_window", "minimise_window", "fullscreen_window",
]
