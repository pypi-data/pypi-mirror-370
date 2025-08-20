import os
import streamlit.components.v1 as components
from typing import Optional, Callable, Any, List, Dict

# Create a _RELEASE constant to switch between development and production modes
_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "st_navigation_tile",
        url="http://localhost:3000",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend", "build")
    _component_func = components.declare_component("st_navigation_tile", path=build_dir)

def st_navigation_tile(
    title: str,
    body: str,
    image_url: Optional[str] = None,
    key: Optional[str] = None,
    on_click: Optional[Callable[..., Any]] = None,
    args: Optional[List] = None,
    kwargs: Optional[Dict] = None,
) -> Optional[dict]:
    """
    A Streamlit component that displays a clickable navigation tile with a title, body, and optional image.
    
    Parameters
    ----------
    title : str
        The title text to display in the tile.
    body : str
        The body text to display in the tile. Supports HTML content.
    image_url : str, optional
        The URL of an image to display at the top of the tile.
    key : str, optional
        An optional key that uniquely identifies this component.
    on_click : callable, optional
        A callback function that will be called when the tile is clicked.
    args : list, optional
        Additional arguments to pass to the on_click callback function.
    kwargs : dict, optional
        Additional keyword arguments to pass to the on_click callback function.
        
    Returns
    -------
    dict or None
        Returns a dictionary with 'clicked': True when the tile is clicked,
        otherwise returns None.
    """
    # Handle the on_click callback
    if callable(on_click):
        args = args or []
        kwargs = kwargs or {}
        
        # Create a callback that accepts Streamlit's argument but ignores it
        def create_callback(callback, *cb_args, **cb_kwargs):
            def wrapper(_=None):
                return callback(*cb_args, **cb_kwargs)
            return wrapper
        on_click = create_callback(on_click, *args, **kwargs)
    
    # Call the component function
    component_value = _component_func(
        title=title,
        body=body,
        image_url=image_url,
        key=key,
        on_change=on_click if callable(on_click) else None,
    )
    
    return component_value
