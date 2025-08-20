"""
Streamlit Breadcrumbs Component

A customizable breadcrumb navigation component for Streamlit applications.

Example usage:
    breadcrumbs = [
        {"title": "HOME"},
        {"title": "DATA TOOLS HUB", "link": "data_tools_hub"},
        {"title": "MACHINE 360", "link": "machine_360"}
    ]
    
    clicked = st_breadcrumbs(breadcrumbs)
    if clicked:
        st.write(f"Navigated to: {clicked}")
"""

import os
import json
import streamlit.components.v1 as components
from typing import Optional, Callable, Any, List, Dict

# Create the _RELEASE constant
_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "st_breadcrumbs",
        url="http://localhost:3000",
    )
else:
    # When we're distributing a production version of the component.
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("st_breadcrumbs", path=build_dir)

def st_breadcrumbs(
    items,
    key=None,
    on_click: Optional[Callable[..., Any]] = None,
    args: Optional[List] = None,
    kwargs: Optional[Dict] = None,
):
    """
    Display a breadcrumb navigation component.
    
    Parameters
    ----------
    items : list of dict
        A list of dictionaries where each dictionary represents a breadcrumb item.
        Each item should have a 'title' key and an optional 'link' key.
        Example: [{"title": "HOME"}, {"title": "Page", "link": "page"}]
    key : str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    on_click : callable, optional
        A callback function that will be called when the tile is clicked.
        If provided, this will override the URL navigation.
    args : list, optional
        Additional arguments to pass to the on_click callback function.
    kwargs : dict, optional
        Additional keyword arguments to pass to the on_click callback function.
        
    Returns
    -------
    str or None
        The 'link' value of the clicked breadcrumb, or None if no breadcrumb
        with a link was clicked.
    """
    # Validate items
    if not isinstance(items, list):
        raise ValueError("'items' must be a list of dictionaries")
        
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("Each item in 'items' must be a dictionary")
        if 'title' not in item:
            raise ValueError("Each item must have a 'title' key")
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
    
    # Call through to the component.
    component_value = _component_func(
        items=items,
        key=key,
        default=None,
        on_change=on_click if callable(on_click) else None,
    )
    
    # Return the clicked link if any
    return component_value.get('clickedLink') if component_value else None

