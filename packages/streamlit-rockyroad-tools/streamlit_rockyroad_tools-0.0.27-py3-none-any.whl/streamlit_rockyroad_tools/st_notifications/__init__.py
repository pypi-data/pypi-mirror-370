import os
import streamlit.components.v1 as components

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
_RELEASE = True

# Declare a Streamlit component for notifications
if not _RELEASE:
    _component_func = components.declare_component(
        "st_notifications",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend", "build")
    _component_func = components.declare_component(
        "st_notifications", path=build_dir)


def _st_notification_base(
    body,
    notification_type,
    key=None,
    icon=None,
    width="stretch",
    on_change=None,
    *args,
    **kwargs,
):
    """
    Base function for all notification types.
    
    Parameters
    ----------
    body : str
        The text to display as GitHub-flavored Markdown. Supports the same
        Markdown directives as st.markdown.
    notification_type : str
        The type of notification: 'info', 'success', 'warning', or 'error'
    key : str or None
        An optional key that uniquely identifies this component.
    icon : str or None
        An optional emoji or Material Symbol icon to display next to the notification.
        Can be a single-character emoji (e.g., "🚨") or a Material Symbol in the
        format ":material/icon_name:" (e.g., ":material/thumb_up:").
    width : str or int
        The width of the notification element. Can be "stretch" (default) to match
        the parent container width, or an integer specifying width in pixels.
    on_change : callable or None
        An optional callback function that will be called when the close button
        is clicked.

    Returns
    -------
    dict or None
        Returns a dictionary with 'closed': True when the Close button is clicked,
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
        body=body,
        notification_type=notification_type,
        icon=icon,
        width=width,
        key=key,
        on_change=on_change_callback,
    )
    return component_value


def st_info(body, *, key=None, icon=None, width="stretch", on_change=None):
    """
    Display an info notification.

    Parameters
    ----------
    body : str
        The text to display as GitHub-flavored Markdown. Syntax information can be found at:
        https://github.github.com/gfm.

        See the body parameter of st.markdown for additional, supported Markdown directives.
    key : str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    icon : str or None
        An optional emoji or icon to display next to the notification. If icon is None (default),
        no icon is displayed. If icon is a string, the following options are valid:

        * A single-character emoji. For example, you can set icon="🚨" or icon="🔥".
          Emoji short codes are not supported.

        * An icon from the Material Symbols library (rounded style) in the format
          ":material/icon_name:" where "icon_name" is the name of the icon in snake case.

          For example, icon=":material/thumb_up:" will display the Thumb Up icon.
          Find additional icons in the Material Symbols font library.
    width : str or int
        The width of the info element. This can be one of the following:

        * "stretch" (default): The width of the element matches the width of the parent container.
        * An integer specifying the width in pixels: The element has a fixed width.
          If the specified width is greater than the width of the parent container,
          the width of the element matches the width of the parent container.
    on_change : callable or None
        An optional callback function that will be called when the close button is clicked.

    Returns
    -------
    dict or None
        Returns a dictionary with 'closed': True when the Close button is clicked,
        otherwise returns None.

    Example
    -------
    >>> import streamlit as st
    >>> from streamlit_rockyroad_tools import st_info
    >>> 
    >>> if 'show_info' not in st.session_state:
    ...     st.session_state.show_info = True
    >>> 
    >>> if st.session_state.show_info:
    ...     result = st_info("This is an **info** notification with [link](https://example.com)", 
    ...                      icon="ℹ️", key="info_notification")
    ...     if result and result.get('closed'):
    ...         st.session_state.show_info = False
    ...         st.rerun()
    """
    return _st_notification_base(body, "info", key=key, icon=icon, width=width, on_change=on_change)


def st_success(body, *, key=None, icon=None, width="stretch", on_change=None):
    """
    Display a success notification.

    Parameters
    ----------
    body : str
        The text to display as GitHub-flavored Markdown. Syntax information can be found at:
        https://github.github.com/gfm.

        See the body parameter of st.markdown for additional, supported Markdown directives.
    key : str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    icon : str or None
        An optional emoji or icon to display next to the notification. If icon is None (default),
        no icon is displayed. If icon is a string, the following options are valid:

        * A single-character emoji. For example, you can set icon="🚨" or icon="🔥".
          Emoji short codes are not supported.

        * An icon from the Material Symbols library (rounded style) in the format
          ":material/icon_name:" where "icon_name" is the name of the icon in snake case.

          For example, icon=":material/thumb_up:" will display the Thumb Up icon.
          Find additional icons in the Material Symbols font library.
    width : str or int
        The width of the success element. This can be one of the following:

        * "stretch" (default): The width of the element matches the width of the parent container.
        * An integer specifying the width in pixels: The element has a fixed width.
          If the specified width is greater than the width of the parent container,
          the width of the element matches the width of the parent container.
    on_change : callable or None
        An optional callback function that will be called when the close button is clicked.

    Returns
    -------
    dict or None
        Returns a dictionary with 'closed': True when the Close button is clicked,
        otherwise returns None.

    Example
    -------
    >>> import streamlit as st
    >>> from streamlit_rockyroad_tools import st_success
    >>> 
    >>> if 'show_success' not in st.session_state:
    ...     st.session_state.show_success = True
    >>> 
    >>> if st.session_state.show_success:
    ...     result = st_success("Operation completed **successfully**!", 
    ...                         icon="✅", key="success_notification")
    ...     if result and result.get('closed'):
    ...         st.session_state.show_success = False
    ...         st.rerun()
    """
    return _st_notification_base(body, "success", key=key, icon=icon, width=width, on_change=on_change)


def st_warning(body, *, key=None, icon=None, width="stretch", on_change=None):
    """
    Display a warning notification.

    Parameters
    ----------
    body : str
        The text to display as GitHub-flavored Markdown. Syntax information can be found at:
        https://github.github.com/gfm.

        See the body parameter of st.markdown for additional, supported Markdown directives.
    key : str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    icon : str or None
        An optional emoji or icon to display next to the notification. If icon is None (default),
        no icon is displayed. If icon is a string, the following options are valid:

        * A single-character emoji. For example, you can set icon="🚨" or icon="🔥".
          Emoji short codes are not supported.

        * An icon from the Material Symbols library (rounded style) in the format
          ":material/icon_name:" where "icon_name" is the name of the icon in snake case.

          For example, icon=":material/thumb_up:" will display the Thumb Up icon.
          Find additional icons in the Material Symbols font library.
    width : str or int
        The width of the warning element. This can be one of the following:

        * "stretch" (default): The width of the element matches the width of the parent container.
        * An integer specifying the width in pixels: The element has a fixed width.
          If the specified width is greater than the width of the parent container,
          the width of the element matches the width of the parent container.
    on_change : callable or None
        An optional callback function that will be called when the close button is clicked.

    Returns
    -------
    dict or None
        Returns a dictionary with 'closed': True when the Close button is clicked,
        otherwise returns None.

    Example
    -------
    >>> import streamlit as st
    >>> from streamlit_rockyroad_tools import st_warning
    >>> 
    >>> if 'show_warning' not in st.session_state:
    ...     st.session_state.show_warning = True
    >>> 
    >>> if st.session_state.show_warning:
    ...     result = st_warning("**Warning:** Your password strength is too low", 
    ...                         icon="⚠️", key="warning_notification")
    ...     if result and result.get('closed'):
    ...         st.session_state.show_warning = False
    ...         st.rerun()
    """
    return _st_notification_base(body, "warning", key=key, icon=icon, width=width, on_change=on_change)


def st_error(body, *, key=None, icon=None, width="stretch", on_change=None):
    """
    Display an error notification.

    Parameters
    ----------
    body : str
        The text to display as GitHub-flavored Markdown. Syntax information can be found at:
        https://github.github.com/gfm.

        See the body parameter of st.markdown for additional, supported Markdown directives.
    key : str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    icon : str or None
        An optional emoji or icon to display next to the notification. If icon is None (default),
        no icon is displayed. If icon is a string, the following options are valid:

        * A single-character emoji. For example, you can set icon="🚨" or icon="🔥".
          Emoji short codes are not supported.

        * An icon from the Material Symbols library (rounded style) in the format
          ":material/icon_name:" where "icon_name" is the name of the icon in snake case.

          For example, icon=":material/thumb_up:" will display the Thumb Up icon.
          Find additional icons in the Material Symbols font library.
    width : str or int
        The width of the error element. This can be one of the following:

        * "stretch" (default): The width of the element matches the width of the parent container.
        * An integer specifying the width in pixels: The element has a fixed width.
          If the specified width is greater than the width of the parent container,
          the width of the element matches the width of the parent container.
    on_change : callable or None
        An optional callback function that will be called when the close button is clicked.

    Returns
    -------
    dict or None
        Returns a dictionary with 'closed': True when the Close button is clicked,
        otherwise returns None.

    Example
    -------
    >>> import streamlit as st
    >>> from streamlit_rockyroad_tools import st_error
    >>> 
    >>> if 'show_error' not in st.session_state:
    ...     st.session_state.show_error = True
    >>> 
    >>> if st.session_state.show_error:
    ...     result = st_error("**Error:** Failed to upload file. Please try again.", 
    ...                       icon="❌", key="error_notification")
    ...     if result and result.get('closed'):
    ...         st.session_state.show_error = False
    ...         st.rerun()
    """
    return _st_notification_base(body, "error", key=key, icon=icon, width=width, on_change=on_change)
