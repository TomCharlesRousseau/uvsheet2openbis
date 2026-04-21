# UV Sheet Excel → openBIS Parser

A Python-based parser that reads experimental data from an Excel protocol file and registers UV sheet experimental steps and sample objects in openBIS.

## Quick Start

### Prerequisites
- Python 3.10+
- openBIS instance with appropriate access

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/uvsheet2openbis.git
   cd uvsheet2openbis
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure openBIS credentials**
   - Edit `config/settings.json` with your openBIS server details:
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

### Usage

Run the parser:
```bash
python main.py
```

**First run:** You'll be prompted to enter your openBIS password. It will be securely stored in your system keyring.

**Subsequent runs:** The stored password will be used automatically.

## Excel File Format

The input Excel file (`UV-Sheets_protocol.xlsx`) should contain these columns:

| Column | Purpose |
|--------|---------|
| Code | Unique identifier for the experimental step |
| Person | Responsible person |
| Date | Experiment date |
| Resin Name | Human-readable resin name (for reference only) |
| Resin Perm-ID | Parent resin object ID in openBIS |
| Instrument | Instrument name (for reference only) |
| Perm ID | Parent project/instrument object ID in openBIS |
| Spacer | Experimental parameter |
| Duration [s] | Experimental parameter (seconds) |
| Number of Sheets | Number of child sample objects to create |
| Uploaded | Status flag (set to "Yes" after successful creation) |

## How It Works

For each row in the Excel file:

1. Creates one **experimental step object** with code from column A
2. Creates N **child sample objects** (where N = "Number of Sheets")
   - Child names: `{Code}-1`, `{Code}-2`, ..., `{Code}-N`
3. Links parent Resin and Instrument using their permIDs
4. Adds Spacer and Duration information to description
5. Sets responsible person from "Person" column
6. Updates Excel file: marks "Uploaded" as "Yes"

## Documentation

See [CLAUDE.md](CLAUDE.md) for detailed project documentation and architecture.

## Error Handling

- **Duplicate objects:** Parser skips if object with same code already exists
- **Invalid permIDs:** Errors are logged; row is skipped
- **Connection issues:** Parser stops and logs the error
- **Excel errors:** Logged but don't block subsequent rows

## License

[Your License Here]

## Support

For issues or questions, please create an issue on GitHub.
