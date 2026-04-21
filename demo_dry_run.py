"""
Demo script for UV Sheet Parser.
Tests the parser with dry-run mode before actual execution.
Useful for verifying Excel parsing and configuration.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from main import UVSheetParser
from utils.logging_config import get_logger

logger = get_logger()


def print_header(title):
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80 + "\n")


def demo_dry_run():
    """Run parser in dry-run mode to preview what will be created."""
    print_header("UV SHEET PARSER - DRY RUN DEMO")
    
    try:
        parser = UVSheetParser()
        
        # Show configuration
        print("Configuration loaded:")
        print(f"  - openBIS URL: {parser.config.openbis_url}")
        print(f"  - Username: {parser.config.openbis_username}")
        print(f"  - Space: {parser.config.openbis_space}")
        print(f"  - Project: {parser.config.project_name}")
        print(f"  - Excel file: {parser.excel_file}\n")
        
        # Show rows
        print_header("EXCEL DATA PREVIEW")
        rows = parser.excel_parser.get_rows()
        print(f"Total rows in Excel: {len(rows)}\n")
        
        if rows:
            print("First 5 rows summary:")
            for i, row in enumerate(rows[:5], 1):
                code = row.get('Code', 'N/A')
                person = row.get('Person', 'N/A')
                num_sheets = row.get('Number of Sheets', 'N/A')
                uploaded = row.get('Uploaded', '')
                status = "[DONE] Already uploaded" if str(uploaded).lower() == 'yes' else "[TODO] Pending"
                
                print(f"\n  Row {i}: {code} ({status})")
                print(f"    - Person: {person}")
                print(f"    - Number of Sheets: {num_sheets}")
        
        # Show pending rows
        print_header("PENDING ROWS")
        pending = parser.excel_parser.get_pending_rows()
        print(f"Rows to be processed: {len(pending)}\n")
        
        if pending:
            print("Pending rows:")
            for i, row in enumerate(pending[:10], 1):
                code = row.get('Code', 'N/A')
                person = row.get('Person', 'N/A')
                resin_perm = row.get('Resin Perm-ID', 'N/A')
                instrument_perm = row.get('Perm ID', 'N/A')
                num_sheets = row.get('Number of Sheets', 'N/A')
                spacer = row.get('Spacer', 'N/A')
                duration = row.get('Duration [s]', 'N/A')
                
                # Format num_sheets for display
                sheets_str = f"{int(num_sheets)} sheets" if isinstance(num_sheets, (int, float)) and not str(num_sheets).lower() == 'nan' else "n/a"
                
                print(f"\n  {i}. Code: {code}")
                print(f"     Person: {person}")
                print(f"     Resin Perm-ID: {resin_perm}")
                print(f"     Instrument Perm-ID: {instrument_perm}")
                print(f"     Number of Sheets: {num_sheets}")
                print(f"     Spacer: {spacer}")
                print(f"     Duration [s]: {duration}")
                print(f"     Will create: 1 main object + {sheets_str}")
            
            if len(pending) > 10:
                print(f"\n  ... and {len(pending) - 10} more rows")
        else:
            print("No pending rows found.")
        
        print_header("DRY-RUN EXECUTION")
        print("Running parser in DRY-RUN mode (no objects will be created)...\n")
        
        success = parser.run(dry_run=True)
        
        print_header("DRY-RUN COMPLETE")
        if success:
            print("[OK] Dry-run completed successfully!")
            print(f"\nSummary:")
            print(f"  - Rows processed: {parser.rows_processed}")
            print(f"  - Would be successful: {parser.rows_successful}")
            print(f"  - Would be failed: {parser.rows_failed}")
            print(f"  - Skipped: {parser.rows_skipped}")
            print("\nWhen ready, run: python main.py")
        else:
            print("[ERROR] Dry-run completed with errors")
        
        return success
    
    except Exception as e:
        logger.error(f"Error during demo: {e}", exc_info=True)
        print(f"\n[ERROR] {e}")
        return False


if __name__ == "__main__":
    success = demo_dry_run()
    sys.exit(0 if success else 1)
