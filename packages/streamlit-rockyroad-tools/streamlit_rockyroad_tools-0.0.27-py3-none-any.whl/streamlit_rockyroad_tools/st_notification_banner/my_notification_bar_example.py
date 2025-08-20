
import os
import sys
import streamlit as st

# Get the absolute path to the parent directory (rockyroad_tools)
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Insert the path to the rockyroad_tools directory into sys.path
sys.path.insert(0, parent_dir)


def run():
    from streamlit_rockyroad_tools import st_notification_bar
    st.set_page_config(page_title="Notification Bar Example", layout="wide")
    st.subheader("Component with constant args")

    st_notification_bar(
        message="<p>Our new&nbsp;<strong>Widgets Incentive Program</strong>&nbsp;has launched!</p>",
        learn_more="https://streamlit.io",
        open_learn_more_link_in_new_tab=True,
        display_always=True,
        key="notification_bar_test_2",
    )

    st_notification_bar(
        message='<p>Our new <strong>Widgets Incentive Program</strong> has <span style="text-decoration: underline;">launched </span>on June 1st! Visit the parts promotion page to get all the details.&nbsp; Email us at <a href="mailto:widgest@yourteam.com" rel="follow">widgest@yourteam.com</a> for more information.</p>',
        key="notification_bar_test_3",
        open_learn_more_link_in_new_tab=False,
        display_always=False,
    )


if __name__ == "__main__":
    run()
