# Project: UV Sheet Excel → openBIS Parser

## Overview

This project is a Python-based parser that reads experimental data from an Excel protocol file (`UV-Sheets_protocol.xlsx`) and registers the corresponding objects and relationships in openBIS using pybis.

The workflow corresponds to UV sheet experimental steps, where each Excel row represents one experimental step that creates:
1. **One main experimental step object** (UV_SHEET_STEP)
2. **N child sample objects** (UV_SHEET_SAMPLE) determined by the "Number of Sheets" column

The parser must:
- Read Excel protocol files
- Create experimental step objects in openBIS
- Create child sample objects (naming: `{Code}-1`, `{Code}-2`, ..., `{Code}-N`)
- Link parents (Resin and Instrument) using permIDs
- Avoid duplicate objects (check if Code already exists)
- Update the Excel file with "Yes" in the "Uploaded" column after successful creation
- Skip rows where "Uploaded" is already "Yes" (future enhancement)

## Excel File Structure

### Input: `UV-Sheets_protocol.xlsx`

| Column | Purpose | Usage |
|--------|---------|-------|
| Code | Unique identifier | Used as the object code in openBIS |
| Person | Responsible person | Set as the creator/responsible person in openBIS |
| Date | Experiment date | Stored in the object metadata |
| Resin Name | Human-readable name | For humans only (ignore in parsing) |
| Resin Perm-ID | Reference to parent Resin | Used to associate parent Resin object via permID |
| Instrument | Human-readable name | For humans only (ignore in parsing) |
| Perm ID | Parent experimental step/project | Used to link parent object via permID |
| Spacer | Experimental parameter | Write to description of experimental step |
| Duration [s] | Experimental parameter | Write to description of experimental step |
| Number of Sheets | Count of child samples | Determines N child objects to create (format: Code-1, Code-2, ..., Code-N) |
| Uploaded | Status indicator | After successful creation, update to "Yes" to avoid re-uploading |

## openBIS Data Model

### Existing Objects (Parents)

These objects already exist in openBIS and should **NOT** be created. Access using permID:

- **Resin** - Referenced via "Resin Perm-ID" column
- **Instrument** - Referenced via "Perm ID" column (or can be a project/collection)

### Objects Created by Parser

**Note:** All objects are created as generic **Sample** type in openBIS (following 2PP parser pattern for compatibility).

#### Object Hierarchy & Relationships

```
Resin (parent) ────┐
                    ├──→ UV Sheet Experimental Step (main object)
Instrument (parent)┘
                    └──→ UV Sheet Sample-1
                    └──→ UV Sheet Sample-2
                    ...
                    └──→ UV Sheet Sample-N
```

**Key points:**
- Main object code: Taken from "Code" column
- Child object codes: `{Code}-1`, `{Code}-2`, ..., `{Code}-{Number of Sheets}`
- All objects are Sample type
- Resin and Instrument are linked as parents using permIDs
- Description contains: Spacer and Duration [s] information
- Responsible person: From "Person" column
- Date: From "Date" column

## Technology Stack

**Python 3.10+**

**Libraries:**
- pandas
- openpyxl
- pybis
- pathlib
- logging

## Project Structure

```
UV sheet parser/
├── CLAUDE.md                          # (this file) Project documentation
├── README.md                          # User-facing documentation
├── UV-Sheets_protocol.xlsx            # Input Excel file (protocol)
├── requirements.txt                   # Python dependencies
├── .env                               # Environment variables (NOT in git)
├── .gitignore                         # Git ignore rules
├── main.py                            # Main orchestrator
├── config/
│   ├── __init__.py                    # Config class
│   └── settings.json                  # Configuration (Space, Project, openBIS URL)
├── excel/
│   └── excel_parser.py                # Excel file reader
├── openbis/
│   ├── __init__.py
│   ├── connection.py                  # Connection handler with keyring
│   └── object_manager.py              # Object creation and linking
├── utils/
│   ├── __init__.py
│   └── logging_config.py              # Logging setup
└── tests/
    ├── __init__.py
    └── test_*.py                      # Unit tests
```

## Configuration

Create `config/settings.json` with your openBIS credentials:

```json
{
    "openbis": {
        "api_url": "https://your-openbis-server/api/v3",
        "username": "your_username",
        "space": "YOUR_SPACE",
        "project_name": "YOUR_PROJECT"
    },
    "excel": {
        "file_path": "UV-Sheets_protocol.xlsx"
    }
}
```

The parser uses keyring for secure PAT (Personal Access Token) storage:
- **First run:** Prompts for password, stores it securely in system keyring
- **Subsequent runs:** Uses stored PAT automatically

## Workflow

1. **Initialize** → Connect to openBIS (with keyring-based authentication)
2. **Parse Excel** → Read all rows from `UV-Sheets_protocol.xlsx`
3. **For each row:**
   - Check if object with that Code already exists → Skip if found (display message)
   - Check if "Uploaded" column is "Yes" → Skip if already uploaded (future enhancement)
   - Create main experimental step object (Sample type) with Code from column A
   - Link parent Resin using "Resin Perm-ID"
   - Link parent Instrument/Project using "Perm ID"
   - Set description with Spacer and Duration info
   - Create N child sample objects (where N = "Number of Sheets")
   - Update Excel file: Set "Uploaded" to "Yes" for this row
4. **Report** → Display statistics (rows processed, successful, failed)

## Error Handling

- **Duplicate Code:** Display message "Object {Code} already exists - skipping"
- **Invalid permID:** Log error with row number and skip
- **Connection failure:** Log error and stop execution
- **Excel write error:** Log and continue (don't block parsing)

## Future Enhancements

1. Skip rows where "Uploaded" column is already "Yes"
2. Use "Resin Name" and "Instrument Name" as verification checks against retrieved permIDs
3. Add support for dataset uploads (if files are referenced in future Excel versions)
4. Implement dry-run mode to preview changes without uploading
5. Add web UI (Streamlit) similar to 2PP parser for easier operation
