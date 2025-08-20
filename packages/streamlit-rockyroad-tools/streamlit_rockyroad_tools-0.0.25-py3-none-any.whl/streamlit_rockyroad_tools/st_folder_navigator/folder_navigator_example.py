import streamlit as st
import sys
import os

# Add parent directory to path to import the package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from st_folder_navigator import st_folder_navigator

st.title("Folder Navigator Component Example")

st.write("This example demonstrates the st_folder_navigator component with different data formats.")

# Example 1: List of strings
st.subheader("Example 1: Simple folder names")
folders_simple = ["Home", "Documents", "Projects", "Streamlit Apps"]

result1 = st_folder_navigator(
    folders=folders_simple,
    key="simple_folders"
)

if result1:
    st.write(f"Selected folder: **{result1}**")

st.write("---")

# Example 2: List of tuples with IDs
st.subheader("Example 2: Folders with IDs (SharePoint-style)")
folders_with_ids = [
    ("Root", "root_id_123"),
    ("Product Improvement Program", "pip_folder_456"),
    ("CMS PIPs", "cms_pips_789"),
    ("Terminated", "terminated_abc"),
    ("PIP-QIT-F0003 CP85 Planetary Failures", "specific_pip_def")
]

result2 = st_folder_navigator(
    folders=folders_with_ids,
    key="folders_with_ids"
)

if result2:
    st.write(f"Selected folder ID: **{result2}**")

st.write("---")

# Example 3: Dynamic navigation simulation
st.subheader("Example 3: Dynamic Navigation Simulation")

# Initialize session state for navigation
if 'current_path' not in st.session_state:
    st.session_state.current_path = ["Home"]

# Define a simple folder structure
folder_structure = {
    "Home": ["Documents", "Pictures", "Downloads"],
    "Documents": ["Work", "Personal", "Archive"],
    "Pictures": ["Vacation", "Family", "Screenshots"],
    "Downloads": ["Software", "PDFs", "Media"],
    "Work": ["Projects", "Reports", "Meetings"],
    "Personal": ["Notes", "Recipes", "Hobbies"]
}

# Display current navigation
result3 = st_folder_navigator(
    folders=st.session_state.current_path,
    key="dynamic_navigation"
)

# Handle folder selection
if result3:
    # Find the index of the selected folder
    if result3 in st.session_state.current_path:
        selected_index = st.session_state.current_path.index(result3)
        # Navigate to that level (truncate path)
        st.session_state.current_path = st.session_state.current_path[:selected_index + 1]
        st.rerun()

# Show available subfolders
current_folder = st.session_state.current_path[-1]
if current_folder in folder_structure:
    st.write(f"**Subfolders in '{current_folder}':**")
    
    cols = st.columns(len(folder_structure[current_folder]))
    for i, subfolder in enumerate(folder_structure[current_folder]):
        with cols[i]:
            if st.button(f"📁 {subfolder}", key=f"nav_{subfolder}"):
                st.session_state.current_path.append(subfolder)
                st.rerun()
else:
    st.write(f"**'{current_folder}'** is a leaf folder (no subfolders)")

# Reset button
if st.button("🏠 Reset to Home"):
    st.session_state.current_path = ["Home"]
    st.rerun()

st.write("---")

# Example 4: Long folder names (responsive test)
st.subheader("Example 4: Long folder names (responsive test)")
long_folders = [
    "Very Long Folder Name That Should Truncate",
    "Another Extremely Long Folder Name",
    "Short",
    "Medium Length Folder",
    "This Is An Exceptionally Long Folder Name That Tests Responsive Design"
]

result4 = st_folder_navigator(
    folders=long_folders,
    key="long_folders"
)

if result4:
    st.write(f"Selected: **{result4}**")

st.write("---")

st.markdown("""
### Component Features:
- **Flexible input**: Accepts list of strings or list of tuples (name, id)
- **Clickable navigation**: Click any folder to navigate to that level
- **Responsive design**: Adapts to mobile and desktop screens
- **Visual hierarchy**: Uses folder icons and chevron separators
- **Return values**: Returns folder name (strings) or ID (tuples)
- **Hover effects**: Interactive feedback on hover
""")
