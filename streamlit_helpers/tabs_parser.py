"""
Streamlit UI tabs for UV Sheet Parser
Contains all tab implementations
"""

import streamlit as st
from pathlib import Path
import sys
from getpass import getuser
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from openbis.connection import OpenBISConnection
from config import Config


def tab_connection_parser():
    """
    Connection tab: Connect to openBIS server
    
    Features:
    - Tries PAT if available (instant login)
    - Falls back to password prompt if PAT missing or expired
    - Validates connection to openBIS
    """
    st.header("🔐 Connection")
    
    # Show configuration info
    st.info("""
    **Configuration:** openBIS connection details are configured in `config/settings.json`
    - Edit that file to change your server URL and username
    - Then click the button below to connect
    """)
    
    # Default values
    default_url = "https://main.datastore.bam.de"
    default_user = ""
    
    # --- Connection Status ---
    st.subheader("Status")
    if st.session_state.parser["connection"]["o"]:
        st.success(f"✅ Connected to openBIS")
        st.caption(f"Connected as: **{st.session_state.parser['connection']['connected_as']}**")
    else:
        st.warning("⚠️ Not connected")
    
    # --- Connection Inputs ---
    st.subheader("Login")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.text_input(
            "OpenBIS URL",
            value=default_url,
            disabled=True,
            help="Configure in config/settings.json"
        )
    
    with col2:
        st.text_input(
            "Username",
            value=default_user,
            disabled=True,
            help="Configure in config/settings.json or uses system user"
        )
    
    # --- Connection Button ---
    if st.button("🔐 Connect to openBIS", use_container_width=True, key="btn_connect"):
        try:
            with st.spinner("🔐 Connecting to openBIS..."):
                # Initialize connection manager and connect
                config = Config()
                conn_manager = OpenBISConnection()
                openbis = conn_manager.connect()
                
                if openbis:
                    st.session_state.parser["connection"]["o"] = openbis
                    st.session_state.parser["connection"]["connected_as"] = config.openbis_username
                    
                    st.success(f"✅ Connected to openBIS!")
                    st.info(f"Logged in as: **{config.openbis_username}**")
                    st.info(f"Server: `{config.openbis_url}`")
                    st.balloons()
                else:
                    st.error("❌ Failed to connect to openBIS")
        
        except ValueError as e:
            st.error(f"❌ Login failed: {e}")
            st.info("💡 Check your credentials and try again. Password prompts appear in the terminal.")
        except Exception as e:
            st.error(f"❌ Connection error: {e}")
            with st.expander("Error details"):
                st.code(str(e))


def tab_upload_excel():
    """
    Upload Excel tab: Select and validate the protocol Excel file
    """
    st.header("📄 Upload Protocol File")
    
    st.markdown("""
    Upload your UV sheet protocol Excel file (`UV-Sheets_protocol.xlsx`).
    The file should contain columns for:
    - Code, Person, Date, Resin Name, Resin Perm-ID, Instrument, Perm ID
    - Spacer, Duration [s], Number of Sheets, Uploaded
    """)
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose Excel file",
        type=["xlsx", "xls"],
        help="Upload UV-Sheets_protocol.xlsx"
    )
    
    if uploaded_file is not None:
        # Save uploaded file to temp location
        temp_dir = Path(".temp")
        temp_dir.mkdir(exist_ok=True)
        
        file_path = temp_dir / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.session_state.parser["excel_file"] = str(file_path)
        
        st.success(f"✅ File uploaded: **{uploaded_file.name}**")
        
        # Show file info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")
        with col2:
            st.metric("File Type", uploaded_file.name.split(".")[-1].upper())
        with col3:
            st.metric("Upload Time", datetime.now().strftime("%H:%M:%S"))
        
        # Preview data
        try:
            import pandas as pd
            df = pd.read_excel(file_path, sheet_name=0)
            
            st.subheader("📊 Preview")
            st.info(f"Found {len(df)} rows in the Excel file")
            
            # Show first few rows
            st.dataframe(df.head(10), use_container_width=True)
            
            # Show columns
            with st.expander("View all columns"):
                st.write(df.columns.tolist())
            
            # Summary stats
            with st.expander("📈 Summary Information"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Rows", len(df))
                with col2:
                    pending_rows = len(df[df.get('Uploaded', False) != True])
                    st.metric("Pending Upload", pending_rows)
                with col3:
                    uploaded_rows = len(df[df.get('Uploaded', False) == True])
                    st.metric("Already Uploaded", uploaded_rows)
        
        except Exception as e:
            st.error(f"❌ Error reading Excel file: {e}")
    
    else:
        st.info("👆 Upload an Excel file to get started")


def tab_configure_parser():
    """
    Configure Parser tab: Set parser options before running
    """
    st.header("⚙️ Parser Configuration")
    
    # Check connection
    if not st.session_state.parser["connection"]["o"]:
        st.warning("⚠️ Please connect to openBIS first in the Connection tab")
        return
    
    st.subheader("Run Options")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        dry_run = st.checkbox(
            "🏜️ Dry Run Mode",
            value=st.session_state.parser["parser_config"]["dry_run"],
            help="Preview what would be created without actually creating objects"
        )
        st.session_state.parser["parser_config"]["dry_run"] = dry_run
    
    with col2:
        auto_skip = st.checkbox(
            "⏭️ Auto-skip Already Uploaded",
            value=st.session_state.parser["parser_config"]["auto_skip_uploaded"],
            help="Skip rows where 'Uploaded' column is already 'Yes'"
        )
        st.session_state.parser["parser_config"]["auto_skip_uploaded"] = auto_skip
    
    st.divider()
    st.subheader("Parser Settings")
    
    batch_size = st.slider(
        "Batch Size (rows to process before updating Excel)",
        min_value=1,
        max_value=500,
        value=st.session_state.parser["parser_config"]["batch_size"],
        step=10,
        help="Large batches are faster but may use more memory"
    )
    st.session_state.parser["parser_config"]["batch_size"] = batch_size
    
    st.divider()
    st.subheader("Expected Behavior")
    
    if dry_run:
        st.info("""
        **Dry Run Mode:** The parser will:
        - ✓ Read rows from Excel
        - ✓ Validate data
        - ✓ Show what would be created
        - ✗ NOT create any objects in openBIS
        - ✗ NOT update the Excel file
        """)
    else:
        st.warning("""
        **Live Mode:** The parser will:
        - ✓ Read rows from Excel
        - ✓ Validate data
        - ✓ Create objects in openBIS
        - ✓ Update the Excel file with "Yes" in Uploaded column
        
        **This is a REAL operation** - objects will be created!
        """)


def tab_run_parser():
    """
    Run Parser tab: Execute the parser with progress tracking
    """
    st.header("▶️ Run Parser")
    
    # Check prerequisites
    if not st.session_state.parser["connection"]["o"]:
        st.error("❌ Not connected to openBIS. Go to Connection tab first.")
        return
    
    if not st.session_state.parser["excel_file"]:
        st.error("❌ No Excel file uploaded. Go to Upload Excel tab first.")
        return
    
    # Show configuration summary
    st.subheader("📋 Configuration Summary")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        mode = "🏜️ DRY RUN" if st.session_state.parser["parser_config"]["dry_run"] else "🔴 LIVE MODE"
        st.metric("Mode", mode)
    
    with col2:
        st.metric("Excel File", Path(st.session_state.parser["excel_file"]).name)
    
    with col3:
        st.metric("Connected As", st.session_state.parser["connection"]["connected_as"])
    
    st.divider()
    
    # Run button
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("▶️ START PARSER", use_container_width=True):
            _run_parser_execution()
    
    with col2:
        if st.button("❌ CANCEL", use_container_width=True, key="btn_cancel"):
            st.session_state.parser["parser_results"]["status"] = "idle"
            st.info("Parser cancelled.")
    
    # Show running status
    if st.session_state.parser["parser_results"]["status"] == "running":
        st.info("Parser is running in the background...")
        
        # Show progress so far
        results = st.session_state.parser["parser_results"]
        progress_total = results["total_rows"] if results["total_rows"] > 0 else 1
        progress_current = results["successful"] + results["failed"] + results["skipped"]
        progress_pct = progress_current / progress_total if progress_total > 0 else 0
        
        st.progress(progress_pct)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total", results["total_rows"])
        with col2:
            st.metric("✅ Successful", results["successful"])
        with col3:
            st.metric("⚠️ Skipped", results["skipped"])
        with col4:
            st.metric("❌ Failed", results["failed"])


def _run_parser_execution():
    """Execute the parser with progress tracking"""
    import pandas as pd
    from excel.excel_parser import ExcelParser
    from openbis.object_manager import ObjectManager
    
    st.session_state.parser["parser_results"]["status"] = "running"
    st.session_state.parser["parser_results"]["start_time"] = datetime.now()
    st.session_state.parser["parser_results"]["messages"] = []
    
    results = st.session_state.parser["parser_results"]
    
    try:
        # Initialize parser
        excel_file = Path(st.session_state.parser["excel_file"])
        excel_parser = ExcelParser(excel_file)
        openbis = st.session_state.parser["connection"]["o"]
        object_manager = ObjectManager(openbis)
        
        # Get pending rows
        rows = excel_parser.get_pending_rows()
        
        if not rows:
            st.warning("No pending rows to process")
            results["status"] = "completed"
            return
        
        results["total_rows"] = len(rows)
        
        # Create progress placeholders
        progress_bar = st.progress(0)
        status_text = st.empty()
        metrics_placeholders = st.columns(4)
        messages_container = st.container()
        
        dry_run = st.session_state.parser["parser_config"]["dry_run"]
        
        with messages_container:
            with st.expander("📋 Detailed Messages", expanded=False):
                messages_area = st.empty()
        
        messages = []
        
        # Process each row
        for idx, row in enumerate(rows, 1):
            code = row.get("Code", f"Row {idx}")
            
            # Update status
            status_text.info(f"Processing: {code} ({idx}/{len(rows)})")
            
            try:
                # Extract row data
                person = row.get("Person", "Unknown")
                date = row.get("Date", "")
                resin_perm_id = row.get("Resin Perm-ID", "")
                instrument_perm_id = row.get("Perm ID", "")
                spacer = row.get("Spacer", "")
                duration = row.get("Duration [s]", "")
                num_sheets = row.get("Number of Sheets", 0)
                
                # Validate
                try:
                    num_sheets_str = str(num_sheets).strip().lower()
                    if num_sheets_str in ["", "nan", "none", "n/a"]:
                        results["skipped"] += 1
                        messages.append(f"⏭️  Row {idx} ({code}): No 'Number of Sheets' - skipped")
                        continue
                    
                    num_sheets = int(float(num_sheets_str))
                except (ValueError, TypeError):
                    results["failed"] += 1
                    messages.append(f"❌ Row {idx} ({code}): Invalid 'Number of Sheets' value")
                    continue
                
                if num_sheets <= 0:
                    results["skipped"] += 1
                    messages.append(f"⏭️  Row {idx} ({code}): Number of Sheets must be > 0")
                    continue
                
                # Check if already exists
                if object_manager.object_exists(code):
                    results["skipped"] += 1
                    messages.append(f"⏭️  Row {idx} ({code}): Object already exists in openBIS - skipped")
                    continue
                
                # Create objects
                if not dry_run:
                    try:
                        parent_perm_id = object_manager.create_experimental_step(
                            code=code,
                            person=person,
                            date=date,
                            resin_perm_id=resin_perm_id,
                            instrument_perm_id=instrument_perm_id,
                            spacer=spacer,
                            duration=duration,
                        )
                        
                        if parent_perm_id:
                            object_manager.create_child_samples(
                                parent_code=code,
                                parent_perm_id=parent_perm_id,
                                num_sheets=num_sheets,
                            )
                            
                            results["successful"] += 1
                            messages.append(f"✅ Row {idx} ({code}): Created successfully with {num_sheets} child samples")
                        else:
                            results["failed"] += 1
                            messages.append(f"❌ Row {idx} ({code}): Failed to create experimental step")
                    
                    except Exception as e:
                        results["failed"] += 1
                        messages.append(f"❌ Row {idx} ({code}): {str(e)}")
                
                else:  # Dry run
                    results["successful"] += 1
                    messages.append(f"🏜️  Row {idx} ({code}): [DRY RUN] Would create {num_sheets} samples")
            
            except Exception as e:
                results["failed"] += 1
                messages.append(f"❌ Row {idx}: Unexpected error: {str(e)}")
            
            # Update progress
            progress = idx / len(rows)
            progress_bar.progress(progress)
            
            # Update metrics
            with metrics_placeholders[0]:
                st.metric("Processed", idx)
            with metrics_placeholders[1]:
                st.metric("✅ Success", results["successful"])
            with metrics_placeholders[2]:
                st.metric("⚠️ Skipped", results["skipped"])
            with metrics_placeholders[3]:
                st.metric("❌ Failed", results["failed"])
            
            # Update messages
            messages_area.text_area("Messages", value="\n".join(messages[-50:]), height=200, disabled=True)
        
        # Save Excel if not dry run
        if not dry_run:
            excel_parser.save()
            messages.append("💾 Excel file updated")
        
        results["status"] = "completed"
        results["end_time"] = datetime.now()
        results["messages"] = messages
        
        st.success("✅ Parser completed!")
        st.balloons()
    
    except Exception as e:
        results["status"] = "failed"
        results["messages"].append(f"FATAL ERROR: {str(e)}")
        st.error(f"❌ Parser failed: {e}")
        with st.expander("Error details"):
            import traceback
            st.code(traceback.format_exc())


def tab_view_results():
    """
    Results tab: View parser execution results
    """
    st.header("📊 Results")
    
    results = st.session_state.parser["parser_results"]
    
    if results["status"] is None or results["status"] == "idle":
        st.info("Run the parser to see results here. Go to the 'Run Parser' tab.")
        return
    
    # Show status
    if results["status"] == "completed":
        st.success("✅ Parser execution completed")
    elif results["status"] == "failed":
        st.error("❌ Parser execution failed")
    elif results["status"] == "running":
        st.warning("⏳ Parser is still running...")
    
    # Show timing
    if results["start_time"]:
        st.caption(f"Started: {results['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    if results["end_time"]:
        st.caption(f"Completed: {results['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        duration = (results["end_time"] - results["start_time"]).total_seconds()
        st.caption(f"Duration: {duration:.1f} seconds")
    
    st.divider()
    
    # Summary metrics
    st.subheader("Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Rows", results["total_rows"])
    with col2:
        st.metric("✅ Successful", results["successful"])
    with col3:
        st.metric("⚠️ Skipped", results["skipped"])
    with col4:
        st.metric("❌ Failed", results["failed"])
    
    st.divider()
    
    # Detailed messages
    if results["messages"]:
        st.subheader("Detailed Messages")
        messages_text = "\n".join(results["messages"])
        st.text_area(
            "Parser output",
            value=messages_text,
            height=400,
            disabled=True
        )
        
        # Download log
        st.download_button(
            label="📥 Download Log",
            data=messages_text,
            file_name=f"parser_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
