import os
import streamlit.components.v1 as components

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
        "st_folder_navigator",
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
        "st_folder_navigator", path=build_dir)


# Create a wrapper function for the component. This is an optional
# best practice - we could simply expose the component function returned by
# `declare_component` and call it done. The wrapper allows us to customize
# our component's API: we can pre-process its input args, post-process its
# output value, and add a docstring for users.


def st_folder_navigator(
        folders,
        key=None,
        on_change=None,
        *args,
        **kwargs,
):
    """
    A streamlit component that displays a folder navigator.

    Parameters
    ----------
    folders: list(tuple(str, str)) or list(str)
        A list of tuples where the first element is the folder name and the second element is an identifier.
        Alternatively, a list of strings where each string is a folder name.
    key: str
        A key that uniquely identifies this component.
    on_change: callable, optional
        A callback function that is called when the folder navigator is changed.
    *args, **kwargs: optional
        Additional arguments and keyword arguments to pass to the callback function.

    Returns
    -------
    str or None
        Returns the folder name (if a list of strings is provided) or the identifier (if a list of tuples is provided) of the selected folder when the folder name is clicked,
        otherwise returns None.
    """

    on_change_callback = None
    if callable(on_change):
        args = args if args else []
        kwargs = kwargs if kwargs else {}

        def callback_function(*args, **kwargs):
            return lambda: on_change(*args, **kwargs)
        on_change_callback = callback_function(*args, **kwargs)
    
    component_value = _component_func(
        folders=folders,
        key=key,
        on_change=on_change_callback,
    )
    return component_value
