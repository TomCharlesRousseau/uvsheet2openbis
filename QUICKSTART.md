## Quick Start Guide

### 1. Setup Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure openBIS

Edit `config/settings.json`:
```json
{
    "openbis": {
        "api_url": "https://your-server/api/v3",
        "username": "your_username",
        "space": "YOUR_SPACE",
        "project_name": "YOUR_PROJECT"
    },
    "excel": {
        "file_path": "UV-Sheets_protocol.xlsx"
    }
}
```

### 3. Test Components

Run component tests:
```powershell
python -m pytest tests/test_components.py -v
```

Or run directly (without pytest):
```powershell
python tests/test_components.py
```

### 4. Preview with Dry-Run Demo

See what will be created **without** modifying openBIS:
```powershell
python demo_dry_run.py
```

This shows:
- Configuration loaded
- All Excel rows
- Pending rows (not yet uploaded)
- What the parser WOULD do

### 5. Run Full Parser

Create objects in openBIS:
```powershell
python main.py
```

**First run:** You'll be prompted for your openBIS password. It's stored securely in your system keyring.

**Subsequent runs:** Password is retrieved from keyring automatically.

### 6. Monitor Progress

Real-time output shows:
- Row-by-row progress
- Objects created with permIDs
- Child samples created
- Errors and warnings

Detailed logs saved to: `parser.log`

---

## Troubleshooting

### "Config file not found"
→ Create `config/settings.json` with your openBIS credentials

### "Excel file not found"
→ Check `config/settings.json` has correct `excel.file_path`

### "Column validation error"
→ Ensure Excel has all required columns (see CLAUDE.md)

### "Failed to connect to openBIS"
→ Check credentials in `config/settings.json` and network connectivity

### "Password prompt not showing"
→ Check terminal is not capturing input; try running with explicit stdin

---

## File Structure

```
├── main.py                    # Main entry point
├── demo_dry_run.py           # Preview mode (safe to run)
├── config/
│   ├── __init__.py
│   └── settings.json         # Your credentials (NOT in git)
├── excel/
│   └── excel_parser.py       # Read Excel file
├── openbis/
│   ├── connection.py         # Connect to openBIS
│   └── object_manager.py     # Create objects
├── utils/
│   └── logging_config.py     # Logging setup
├── tests/
│   └── test_components.py    # Unit tests
└── requirements.txt          # Python packages
```

---

## Next Steps

1. ✅ Setup config/settings.json
2. ✅ Run: `python demo_dry_run.py`
3. ✅ Verify preview looks correct
4. ✅ Run: `python main.py`
5. ✅ Verify objects created in openBIS
6. ✅ Check Excel "Uploaded" column is "Yes"
