# Streamlit UI for UV Sheet Parser

A modern web-based user interface for the UV Sheet Parser that makes it easy to register experimental data from Excel to openBIS.

## Features

### 🔐 Connection
- **PAT-based Authentication**: Automatically uses saved tokens for quick login
- **Password Fallback**: Prompts for password if token not available
- **Visual Status**: See your connection status and username at a glance

### 📄 Upload Excel
- **Drag & Drop Upload**: Simply upload your `UV-Sheets_protocol.xlsx` file
- **File Preview**: Automatic preview of the first 10 rows
- **Summary Statistics**:
  - Total number of rows
  - Count of pending uploads
  - Count of already uploaded rows

### ⚙️ Parser Configuration
- **🏜️ Dry Run Mode**: Preview what would be created without actually creating objects
- **⏭️ Auto-skip Already Uploaded**: Skip rows where 'Uploaded' column is 'Yes'
- **Batch Size Control**: Adjust batch size for optimal performance
- **Configuration Preview**: Clear explanation of what will happen in each mode

### ▶️ Run Parser
- **Live Progress Tracking**: Watch real-time progress with metrics
- **Detailed Logging**: See each row being processed as it happens
- **Progress Bar**: Visual indication of completion status
- **Cancel Option**: Stop the parser at any time

### 📊 Results
- **Summary Metrics**: Total rows, successful, skipped, and failed counts
- **Execution Timing**: See how long the processing took
- **Detailed Messages**: Review what happened with each row
- **Log Download**: Export the full log for documentation

## Getting Started

### Prerequisites
```bash
pip install streamlit pandas openpyxl keyring pybis
```

### Installation & Setup

1. **Install Streamlit** (if not already installed):
   ```bash
   pip install streamlit
   ```

2. **Ensure all dependencies are installed**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the UI

#### Windows (Easy)
Double-click: `run_streamlit.bat`

Or run in PowerShell/Command Prompt:
```bash
streamlit run streamlit_app.py
```

#### Linux/Mac
```bash
streamlit run streamlit_app.py
```

The app will open in your default browser at:
```
http://localhost:8501
```

## Workflow

### 1️⃣ Connect to openBIS
- Go to the **Connection** tab
- Enter your openBIS URL (default: `https://main.datastore.bam.de`)
- Optionally enter your username (defaults to system user)
- Click **🔐 Connect to openBIS**
- Wait for the PAT prompt (appears in terminal, not in browser)

### 2️⃣ Upload Protocol File
- Go to the **Upload Excel** tab
- Click the upload area or drag & drop your `UV-Sheets_protocol.xlsx` file
- Review the preview to ensure the file is correct
- Check the summary statistics

### 3️⃣ Configure Parser
- Go to the **Configure** tab
- Choose your mode:
  - **🏜️ Dry Run**: Test without creating objects
  - **🔴 Live Mode**: Actually create objects in openBIS
- Adjust batch size if needed (default: 50 rows)
- Review the expected behavior

### 4️⃣ Run Parser
- Go to the **Run Parser** tab
- Review the configuration summary
- Click **▶️ START PARSER**
- Watch the progress bar and metrics update in real-time
- Review detailed messages as each row is processed

### 5️⃣ View Results
- Go to the **Results** tab (automatically shows after completion)
- Review the summary metrics
- Read detailed messages about each row
- Download the log if needed for documentation

## Excel File Format

Your protocol file should have these columns:

| Column | Purpose | Format |
|--------|---------|--------|
| Code | Unique identifier | Text (e.g., "EXP001") |
| Person | Responsible person | Text |
| Date | Experiment date | Date (YYYY-MM-DD) |
| Resin Name | Human-readable name | Text |
| Resin Perm-ID | Reference to parent Resin | PermID string |
| Instrument | Human-readable name | Text |
| Perm ID | Parent experimental step | PermID string |
| Spacer | Experimental parameter | Numeric |
| Duration [s] | Experimental parameter | Numeric |
| Number of Sheets | Count of child samples | Integer (1, 2, 3, ...) |
| Uploaded | Status indicator | Boolean (True/False) or Text (yes/no) |

## Understanding the Results

### Status Indicators
- ✅ **Successful**: Object was created in openBIS
- ⚠️ **Skipped**: Row was skipped (already uploaded, missing data, etc.)
- ❌ **Failed**: Error occurred during creation

### Common Messages

```
✅ Row 1 (EXP001): Created successfully with 3 child samples
   → Experimental step was created with 3 child sample objects

⏭️  Row 2 (EXP002): Object already exists in openBIS - skipped
   → Code already exists; use a different code or update manually

❌ Row 3 (EXP003): Invalid 'Number of Sheets' value
   → Check the 'Number of Sheets' column for valid integer values

⏳ Dry Run: Would create 5 samples
   → In dry-run mode; no objects were actually created
```

## Tips & Tricks

### 💡 Best Practices

1. **Start with Dry Run**
   - Always test with dry-run mode first
   - Verify the log output matches your expectations
   - Then switch to live mode

2. **Batch Processing**
   - For large files (>500 rows), use a batch size of 100-200
   - Smaller batches = more frequent Excel updates but slower
   - Larger batches = faster but more work if interrupted

3. **Error Recovery**
   - If the parser fails midway, it's safe to re-run
   - Rows already marked as "Uploaded" will be skipped
   - Check the "Already Uploaded" count before re-running

4. **Validating Data**
   - Use the file preview to double-check data
   - Especially verify:
     - PermID format (should be proper UUID/code format)
     - Number of Sheets (must be positive integer)
     - Person names and dates

### 🔧 Troubleshooting

#### Connection Issues
- **"❌ Connection error: Permission denied"**
  - Check username and password
  - Verify openBIS server is running
  - Try entering username explicitly

- **"⚠️ CHECK THE TERMINAL! Password prompt will appear there"**
  - This is normal - look in the terminal window for the password prompt
  - Type your password and press Enter
  - The browser will continue automatically

#### Parser Issues
- **"⏭️ No 'Number of Sheets' specified"**
  - Check that this column has a valid integer value
  - Empty cells or text values will be skipped

- **"❌ Object already exists"**
  - This code was already created in a previous run
  - Either use a unique code or manually update in openBIS

#### File Upload Issues
- **"❌ Error reading Excel file"**
  - Ensure file is a valid Excel file (.xlsx or .xls)
  - File should not be corrupted
  - Try opening it in Excel first to verify

### 📊 Monitoring Execution
- **Progress bar**: Shows % of rows processed
- **Live metrics**: Updated after each row
- **Message log**: Detailed output for each row
- **Sidebar status**: Shows current connection and last run results

## Advanced Features

### Environment Variables
Set these in your environment or `.env` file:

```bash
OPENBIS_URL=https://your-server/api/v3
OPENBIS_SPACE=YOUR_SPACE
OPENBIS_PROJECT=YOUR_PROJECT
```

### Custom Configuration
Edit `config/settings.json` to set defaults:

```json
{
    "openbis": {
        "api_url": "https://your-server/api/v3",
        "space": "YOUR_SPACE",
        "project_name": "YOUR_PROJECT"
    }
}
```

### Debugging
Enable debug logging in the parser configuration:

```bash
streamlit run streamlit_app.py --logger.level=debug
```

## Support & Issues

### Useful Links
- [Parser Documentation](README.md)
- [Project Overview](CLAUDE.md)
- [OpenBIS Documentation](https://wiki.openbis.ethz.ch/)

### Getting Help
1. Check the parser log for error messages
2. Review the "Error details" expender in the Results tab
3. Check the terminal output for connection errors
4. Verify Excel file format matches requirements

## Version Info

- **UI Framework**: Streamlit 1.28+
- **Python**: 3.10+
- **Last Updated**: 2026-04-22

## License

See [LICENSE](LICENSE) file
