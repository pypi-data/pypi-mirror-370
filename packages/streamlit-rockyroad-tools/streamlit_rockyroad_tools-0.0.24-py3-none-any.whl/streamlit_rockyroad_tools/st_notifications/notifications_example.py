import streamlit as st
import sys
import os

# Add parent directory to path to import the package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from st_notifications import st_info, st_success, st_warning, st_error

st.set_page_config(page_title="Streamlit Notifications Example", layout="wide")

st.title("🔔 Streamlit Notifications Example")
st.markdown("This example demonstrates the four notification types: **info**, **success**, **warning**, and **error**.")

st.markdown("---")

# Initialize session state for each notification type
if 'show_info' not in st.session_state:
    st.session_state.show_info = True
if 'show_success' not in st.session_state:
    st.session_state.show_success = True
if 'show_warning' not in st.session_state:
    st.session_state.show_warning = True
if 'show_error' not in st.session_state:
    st.session_state.show_error = True

# Control buttons
st.subheader("Controls")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("Show All"):
        st.session_state.show_info = True
        st.session_state.show_success = True
        st.session_state.show_warning = True
        st.session_state.show_error = True
        st.rerun()

with col2:
    if st.button("Hide All"):
        st.session_state.show_info = False
        st.session_state.show_success = False
        st.session_state.show_warning = False
        st.session_state.show_error = False
        st.rerun()

with col3:
    if st.button("Toggle Info"):
        st.session_state.show_info = not st.session_state.show_info
        st.rerun()

with col4:
    if st.button("Toggle Success"):
        st.session_state.show_success = not st.session_state.show_success
        st.rerun()

with col5:
    if st.button("Toggle Warning"):
        st.session_state.show_warning = not st.session_state.show_warning
        st.rerun()

st.markdown("---")

# Info notification
st.subheader("📘 Info Notification")
if st.session_state.show_info:
    result = st_info(
        "This is a **Streamlit info message**. Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
        "Aenean commodo ligula eget dolor. [Learn more](https://streamlit.io) about Streamlit.",
        icon="ℹ️",
        key="info_notification"
    )
    if result and result.get('closed'):
        st.session_state.show_info = False
        st.rerun()

st.markdown("---")

# Success notification
st.subheader("✅ Success Notification")
if st.session_state.show_success:
    result = st_success(
        "**Successfully uploaded!** Your file has been processed and is ready for analysis. "
        "You can now proceed to the next step.",
        icon=":material/check_circle:",
        key="success_notification"
    )
    if result and result.get('closed'):
        st.session_state.show_success = False
        st.rerun()

st.markdown("---")

# Warning notification
st.subheader("⚠️ Warning Notification")
if st.session_state.show_warning:
    result = st_warning(
        "**Warning:** Your password strength is too low. Please consider using a stronger password "
        "with at least 8 characters, including `uppercase`, `lowercase`, numbers, and special characters.",
        icon="⚠️",
        key="warning_notification"
    )
    if result and result.get('closed'):
        st.session_state.show_warning = False
        st.rerun()

st.markdown("---")

# Error notification
st.subheader("❌ Error Notification")
if st.session_state.show_error:
    result = st_error(
        "**Error:** Failed to connect to the database. Please check your connection settings and try again. "
        "If the problem persists, contact support at support@example.com.",
        icon=":material/error:",
        key="error_notification"
    )
    if result and result.get('closed'):
        st.session_state.show_error = False
        st.rerun()

st.markdown("---")

# Additional examples
st.subheader("🎨 Additional Examples")

# Width examples
st.markdown("### Width Examples")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Fixed Width (400px):**")
    st_info(
        "This notification has a **fixed width** of 400 pixels.",
        width=400,
        key="fixed_width_info"
    )

with col2:
    st.markdown("**Stretch Width (default):**")
    st_info(
        "This notification **stretches** to fill the available width.",
        width="stretch",
        key="stretch_width_info"
    )

# Icon examples
st.markdown("### Icon Examples")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Emoji Icons:**")
    st_success("🎉 Celebration with emoji!", icon="🎉", key="emoji_success")
    st_warning("🔥 Fire warning!", icon="🔥", key="emoji_warning")

with col2:
    st.markdown("**Material Symbol Icons:**")
    st_info("Thumbs up!", icon=":material/thumb_up:", key="material_info")
    st_error("Delete warning!", icon=":material/delete:", key="material_error")

# No icon examples
st.markdown("### No Icon Examples")
st_info("This info notification has **no icon** displayed.", key="no_icon_info")
st_success("This success notification also has **no icon**.", key="no_icon_success")

st.markdown("---")
st.markdown("### 📝 Notes")
st.markdown("""
- **Markdown Support**: All notifications support GitHub-flavored Markdown including **bold**, *italic*, `code`, and [links](https://example.com).
- **Icons**: Support both emoji (🚨) and Material Symbols (:material/icon_name:).
- **Width**: Can be "stretch" (default) or integer pixels.
- **Close Button**: Click the × to close any notification.
- **Responsive**: Notifications adapt to mobile and tablet screens.
- **Session State**: Use Streamlit session state to control notification visibility.
""")
