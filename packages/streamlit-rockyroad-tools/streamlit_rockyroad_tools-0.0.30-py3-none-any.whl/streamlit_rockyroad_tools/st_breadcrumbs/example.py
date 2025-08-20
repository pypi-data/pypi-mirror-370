"""
Breadcrumbs Component Example

This example demonstrates how to use the st_breadcrumbs component.
"""

import os
import sys
import streamlit as st

# Get the absolute path to the parent directory (rockyroad_tools)
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Insert the path to the rockyroad_tools directory into sys.path
sys.path.insert(0, parent_dir)

def main():
    from streamlit_rockyroad_tools import st_breadcrumbs
    st.set_page_config(page_title="Breadcrumbs Example", layout="wide")
    
    st.title("Breadcrumbs Navigation Example")
    
    # Example 1: Basic usage
    st.header("Basic Usage")
    
    breadcrumbs = [
        {"title": "HOME"},
        {"title": "DATA TOOLS HUB", "link": "data_tools_hub"},
        {"title": "MACHINE 360", "link": "machine_360"}
    ]

    def on_click(key):
        if key in st.session_state:
            st.write(f"You clicked on: {st.session_state[key]}")
    
    clicked = st_breadcrumbs(breadcrumbs, key="example1", on_click=on_click, args=["example1"])
    
    if clicked:
        st.success(f"You clicked on: {clicked}")
    

if __name__ == "__main__":
    main()
