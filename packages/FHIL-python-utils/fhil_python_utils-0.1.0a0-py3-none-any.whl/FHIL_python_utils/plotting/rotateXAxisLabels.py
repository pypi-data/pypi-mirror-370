"""
Axis label rotation utilities for seaborn plots.
"""

from typing import Any

def rotateAxisLabels(
    plot_obj: Any, 
    rotation: float = 45, 
    rotation_mode: str = 'anchor', 
    ha: str = 'right'
) -> Any:
    """
    Rotate x-axis tick labels on a seaborn.objects plot
    
    Parameters
    ----------
    plot_obj : seaborn.objects.Plot
        The seaborn objects Plot instance to render.
    rotation : float, optional
        Rotation angle for x-axis tick labels in degrees. Default is 45.
    rotation_mode : str, optional
        Rotation mode for the labels. Default is 'anchor'.
    ha : str, optional
        Horizontal alignment for x-axis tick labels ('left', 'center', 'right'). Default is 'right'.

    Returns
    -------
    matplotlib.figure.Figure
        The matplotlib figure object with rotated x-axis labels.
    """
    fig = plot_obj.plot()
    ax = fig._figure.axes[0]
    ax.set_xticklabels(ax.get_xticklabels(), rotation=rotation, rotation_mode=rotation_mode, ha=ha)
    return fig