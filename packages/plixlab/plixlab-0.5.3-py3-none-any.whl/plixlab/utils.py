"""
PlixLab Utilities Module
"""


from typing import Any, Dict,Union,List
from bokeh.plotting import figure as bokeh_figure




def normalize_dict(data: Any) -> Any:
    """
    Recursively normalize a dictionary, list, or tuple for serialization.

    This function ensures that complex nested data structures can be properly
    serialized by converting them to basic Python types.

    Args:
        data: Data structure to normalize (dict, list, tuple, or other)

    Returns:
        Normalized data structure with the same content but serializable types
    """
    if isinstance(data, dict):
        return {k: normalize_dict(v) for k, v in data.items()}
    elif isinstance(data, (list, tuple)):
        return [normalize_dict(v) for v in data]
    else:
        return data


def process_bokeh(fig: bokeh_figure) -> None:
    """
    Apply PlixLab styling to a Bokeh figure for consistent presentation appearance.

    Configures the figure with white text on transparent background to match
    the PlixLab presentation theme.

    Args:
        fig: Bokeh figure object to style

    Note:
        Modifies the figure in-place
    """
    fig.xaxis.major_tick_line_color = "white"
    fig.xaxis.major_label_text_color = "white"
    fig.yaxis.major_tick_line_color = "white"
    fig.yaxis.major_label_text_color = "white"
    fig.xaxis.axis_label_text_color = "white"
    fig.yaxis.axis_label_text_color = "white"
    fig.background_fill_color = None
    fig.border_fill_color = None
    fig.sizing_mode = "stretch_both"

  


def process_plotly(fig: Any) -> Any:
    """
    Apply PlixLab styling to a Plotly figure for consistent presentation appearance.

    Configures the figure with white text on transparent background and disables
    interaction features to match the PlixLab presentation theme.

    Args:
        fig: Plotly figure object to style

    Returns:
        Plotly figure object: The styled figure
    """
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        autosize=True,
        legend=dict(font=dict(color="white")),
        xaxis=dict(title=dict(font=dict(color="white")), tickfont=dict(color="white")),
        yaxis=dict(title=dict(font=dict(color="white")), tickfont=dict(color="white")),
        dragmode=None,
    )

    return fig


def get_style(x: float, y: float, w: Union[float, str], h: Union[float, str],
              halign: str, valign: str) -> Dict[str, Any]:
    """Generate CSS style for a component based on its position and size."""

    # Translate factors (percent) for aligning the element's anchor at (x,y)
    if halign == "center":
        tx = -50
    elif halign == "left":
        tx = 0
    elif halign == "right":
        tx = -100
    else:
        raise ValueError(f"Invalid horizontal alignment: {halign}")

    if valign == "center":
        ty = -50
    elif valign == "top":
        ty = 0
    elif valign == "bottom":
        ty = -100
    else:
        raise ValueError(f"Invalid vertical alignment: {valign}")

    style: Dict[str, Any] = {
        'position':  'absolute',
        'left':      f'{x*100}%',
        'top':       f'{(1 - y)*100}%',   # use top for intuitive translateY
        'transform': f'translate({tx}%, {ty}%)',
        'display':   'flex'
    }

  
    # Flex alignment (content inside the box)
    if halign == "center":
        style.update({'justifyContent': 'center', 'textAlign': 'center'})
    elif halign == "left":
        style.update({'justifyContent': 'flex-start', 'textAlign': 'left'})
    else:  # right
        style.update({'justifyContent': 'flex-end', 'textAlign': 'right'})

    if valign == "center":
        style.update({'alignItems': 'center'})
    elif valign == "top":
        style.update({'alignItems': 'flex-start'})
    else:  # bottom
        style.update({'alignItems': 'flex-end'})

    # Width/height
    if w == 'auto' or w is None:
        style['width'] = 'auto'
    else:
        style['width'] = f'{float(w)*100}%'

    if h == 'auto' or h is None:
        style['height'] = 'auto'
    else:
        style['height'] = f'{float(h)*100}%'

    return style

