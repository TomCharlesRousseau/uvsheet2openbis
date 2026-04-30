"""
Streamlit UI for UV Sheet Parser
Main application entry point
"""

import streamlit as st
from datetime import datetime
from pathlib import Path
from typing import Optional

# Initialize session state
def init_parser_state():
    """Initialize parser application state"""
    return {
        "connection": {"o": None, "connected_as": None},
        "excel_file": None,
        "parser_config": {
            "dry_run": False,
            "auto_skip_uploaded": True,
            "batch_size": 50,
        },
        "parser_results": {
            "status": None,  # "idle", "running", "completed", "failed"
            "total_rows": 0,
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "messages": [],
            "start_time": None,
            "end_time": None,
        },
    }


# Page configuration
st.set_page_config(
    page_title="UV Sheet Parser",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "parser" not in st.session_state:
    st.session_state.parser = init_parser_state()

# Main title
st.title("UV Sheet Parser")
st.write("Parse UV sheet experimental data from Excel and register objects in openBIS.")

# Import tab modules
from streamlit_helpers.tabs_parser import (
    tab_settings,
    tab_connection_parser,
    tab_upload_excel,
    tab_configure_parser,
    tab_run_parser,
    tab_view_results,
)

# Create tabs
tabs = st.tabs([
    "⚙️ Settings",
    "🔐 Connection",
    "📄 Upload Excel",
    "⚙️ Configure",
    "▶️ Run Parser",
    "📊 Results",
])

# Render tabs
with tabs[0]:
    tab_settings()

with tabs[1]:
    tab_connection_parser()

with tabs[2]:
    tab_upload_excel()

with tabs[3]:
    tab_configure_parser()

with tabs[4]:
    tab_run_parser()

with tabs[5]:
    tab_view_results()

# Sidebar info
with st.sidebar:
    st.divider()
    st.subheader("📊 Parser Status")
    
    if st.session_state.parser["connection"]["o"]:
        st.success(f"✅ Connected as {st.session_state.parser['connection']['connected_as']}")
    else:
        st.warning("⚠️ Not connected")
    
    # Show results summary if available
    results = st.session_state.parser["parser_results"]
    if results["status"] in ["completed", "failed"]:
        st.divider()
        st.subheader("Last Run")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Successful", results["successful"])
            st.metric("Skipped", results["skipped"])
        with col2:
            st.metric("Failed", results["failed"])
            st.metric("Total", results["total_rows"])
