import os
import streamlit.components.v1 as components
from typing import Optional, Callable, Any, List, Dict

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
# (This is, of course, optional - there are innumerable ways to manage your
# release process.)
_RELEASE = True

# Declare a Streamlit component. `declare_component` returns a function
# that is used to create instances of the component. We're naming this
# function "_component_func", with an underscore prefix, because we don't want
# to expose it directly to users. Instead, we will create a custom wrapper
# function, below, that will serve as our component's public API.

# It's worth noting that this call to `declare_component` is the
# *only thing* you need to do to create the binding between Streamlit and
# your component frontend. Everything else we do in this file is simply a
# best practice.

if not _RELEASE:
    _component_func = components.declare_component(
        # We give the component a simple, descriptive name ("my_component"
        # does not fit this bill, so please choose something better for your
        # own component :)
        "st_notification_banner",
        # Pass `url` here to tell Streamlit that the component will be served
        # by the local dev server that you run via `npm run start`.
        # (This is useful while your component is in development.)
        url="http://localhost:3000",
    )
else:
    # When we're distributing a production version of the component, we'll
    # replace the `url` param with `path`, and point it to the component's
    # build directory:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend", "build")
    _component_func = components.declare_component(
        "st_notification_banner", path=build_dir)


# Create a wrapper function for the component. This is an optional
# best practice - we could simply expose the component function returned by
# `declare_component` and call it done. The wrapper allows us to customize
# our component's API: we can pre-process its input args, post-process its
# output value, and add a docstring for users.


def st_notification_banner(
        message: str,
        learn_more: Optional[str] = None,
        open_learn_more_link_in_new_tab: bool = False,
        key: Optional[str] = None,
        on_change: Optional[Callable] = None,
        args: Optional[List] = None,
        kwargs: Optional[Dict] = None,
):
    """
    A streamlit component that displays a notification banner with a message, learn more link and a close button.

    Parameters
    ----------
    message: str
        The message to display in the notification banner. Supports HTML content including
        tags like <strong>, <em>, <p>, etc. HTML entities like &nbsp; are also supported.
    learn_more: str, optional
        The URL to the learn more page. If not provided, the Learn More button will not appear.
    open_learn_more_link_in_new_tab: bool, optional
        Whether to open the learn more link in a new tab. Defaults to False.
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    on_change: callable or None
        An optional callback function that will be called when the Close button
        is clicked.
    args: list or None
        An optional list of arguments to pass to the callback function.
    kwargs: dict or None
        An optional dictionary of keyword arguments to pass to the callback function.

    Returns
    -------
    dict or None
        Returns a dictionary with 'closed': True when the Close button is clicked,
        otherwise returns None.
    """

    if callable(on_change):
        args = args or []
        kwargs = kwargs or {}
        
        # Create a callback that accepts Streamlit's argument but ignores it
        def create_callback(callback, *cb_args, **cb_kwargs):
            def wrapper(_=None):
                return callback(*cb_args, **cb_kwargs)
            return wrapper
        on_change_callback = create_callback(on_change, *args, **kwargs)
    
    component_value = _component_func(
        message=message,
        learn_more=learn_more,
        open_learn_more_link_in_new_tab=open_learn_more_link_in_new_tab,
        key=key,
        on_change=on_change_callback,
    )
    return component_value
