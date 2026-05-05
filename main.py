"""
Main orchestrator for UV Sheet Parser.
Coordinates all parsing, object creation, and Excel updates.
"""

import sys
from pathlib import Path
from typing import Optional

from utils.logging_config import get_logger
from config import Config
from excel.excel_parser import ExcelParser
from openbis.connection import OpenBISConnection
from openbis.object_manager import ObjectManager

logger = get_logger()


class UVSheetParser:
    """Main UV Sheet Parser orchestrator."""

    def __init__(self, excel_file: Optional[Path] = None):
        """
        Initialize parser.

        Args:
            excel_file: Path to Excel file (uses config default if not provided)
        """
        self.config = Config()

        # Use provided Excel file or fall back to config
        if excel_file is None:
            excel_file = Path(self.config.excel_file_path)

        self.excel_file = Path(excel_file)
        self.excel_parser = ExcelParser(self.excel_file)
        self.conn_manager = OpenBISConnection()
        self.object_manager: Optional[ObjectManager] = None

        # Statistics
        self.rows_processed = 0
        self.rows_successful = 0
        self.rows_failed = 0
        self.rows_skipped = 0

    def run(self, dry_run: bool = False) -> bool:
        """
        Execute full parsing and upload workflow.

        Args:
            dry_run: If True, don't create objects or update Excel

        Returns:
            True if overall execution successful, False otherwise
        """
        logger.info("=" * 80)
        logger.info("UV Sheet Parser Starting")
        logger.info("=" * 80)

        try:
            # Connect to openBIS
            logger.info("Connecting to openBIS...")
            openbis = self.conn_manager.connect()
            if not openbis:
                logger.error("Failed to connect to openBIS")
                return False

            self.object_manager = ObjectManager(openbis)
            logger.info("Successfully connected to openBIS")

            # Get pending rows
            rows = self.excel_parser.get_pending_rows()

            if not rows:
                logger.info("No pending rows to process")
                return True

            logger.info(f"Processing {len(rows)} rows...")

            # Process each row
            for idx, row in enumerate(rows, 1):
                logger.info("-" * 80)
                logger.info(f"Row {idx}/{len(rows)}")

                status = self._process_row(row, dry_run)
                self.rows_processed += 1

                if status == "success":
                    self.rows_successful += 1
                elif status == "failed":
                    self.rows_failed += 1
                elif status == "skipped":
                    self.rows_skipped += 1

            # Save Excel file if not dry-run
            if not dry_run:
                logger.info("Saving Excel file...")
                self.excel_parser.save()

            # Print summary
            self._print_summary()

            return True

        except Exception as e:
            logger.error(f"Fatal error during parsing: {e}", exc_info=True)
            return False

        finally:
            self.conn_manager.disconnect()

    def _process_row(self, row: dict, dry_run: bool = False) -> str:
        """
        Process a single row from Excel.

        Args:
            row: Row data dictionary
            dry_run: If True, don't create objects or update Excel

        Returns:
            'success' if created, 'failed' if creation error, 'skipped' if validation prevented creation
        """
        try:
            code = row.get("Code")
            if not code or str(code).lower() in ["nan", "none", ""]:
                logger.warning("Row has no Code - skipping")
                return "skipped"

            code = str(code).strip()
            logger.info(f"Processing: {code}")

            # Check if already uploaded
            uploaded = row.get("Uploaded", False)
            # Handle both boolean True and string "yes" for backward compatibility
            if uploaded is True or str(uploaded).lower() in ["yes", "true"]:
                logger.info(f"Code {code} already uploaded - skipping")
                return "skipped"

            # Check if object already exists
            if self.object_manager.object_exists(code):
                logger.warning(f"Object {code} already exists in openBIS - skipping")
                return "skipped"

            # Extract data
            person = row.get("Person", "Unknown")
            date = row.get("Date", "")
            resin_perm_id = row.get("Resin Perm-ID", "")
            instrument_perm_id = row.get("Perm ID", "")  # This is actually Instrument
            spacer = row.get("Spacer", "")
            duration = row.get("Duration [s]", "")
            num_sheets = row.get("Number of Sheets", 0)

            # Ensure num_sheets is int and valid
            try:
                # Convert to string first to handle NaN values
                num_sheets_str = str(num_sheets).strip().lower()
                if num_sheets_str in ["", "nan", "none", "n/a"]:
                    logger.warning(
                        f"No 'Number of Sheets' specified for {code} - skipping"
                    )
                    return "skipped"

                num_sheets = int(float(num_sheets_str))
            except (ValueError, TypeError) as e:
                logger.error(f"Invalid 'Number of Sheets' value: {num_sheets} - {e}")
                return "skipped"

            if num_sheets <= 0:
                logger.error(f"Number of Sheets must be > 0, got: {num_sheets}")
                return "skipped"

            if dry_run:
                logger.info(
                    "[DRY RUN] Would create experimental step and child samples"
                )
                logger.info(f"  Code: {code}")
                logger.info(f"  Person: {person}")
                logger.info(f"  Resin: {resin_perm_id}")
                logger.info(f"  Instrument: {instrument_perm_id}")
                logger.info(f"  Child samples: {num_sheets}")
                return True

            # Create main experimental step
            logger.info(f"Creating experimental step: {code}")
            parent_perm_id = self.object_manager.create_experimental_step(
                code=code,
                person=person,
                date=date,
                resin_perm_id=resin_perm_id,
                instrument_perm_id=instrument_perm_id,
                spacer=spacer,
                duration=duration,
            )

            if not parent_perm_id:
                logger.error(f"Failed to create experimental step '{code}'")
                return "failed"

            # Create child samples
            logger.info(f"Creating {num_sheets} child samples for {code}")
            children = self.object_manager.create_child_samples(
                parent_code=code, parent_perm_id=parent_perm_id, num_sheets=num_sheets, person=person
            )

            if len(children) < num_sheets:
                logger.warning(
                    f"Only created {len(children)}/{num_sheets} child samples"
                )

            # Update Excel
            logger.info(f"Marking {code} as Uploaded in Excel")
            self.excel_parser.update_uploaded(code)

            logger.info(f"Successfully processed: {code}")
            return "success"

        except Exception as e:
            logger.error(f"Error processing row: {e}", exc_info=True)
            return "failed"

    def _print_summary(self) -> None:
        """Print execution summary."""
        logger.info("=" * 80)
        logger.info("EXECUTION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Rows processed:  {self.rows_processed}")
        logger.info(f"Successful:      {self.rows_successful}")
        logger.info(f"Failed:          {self.rows_failed}")
        logger.info(f"Skipped:         {self.rows_skipped}")
        logger.info("=" * 80)


def main():
    """Main entry point."""
    try:
        parser = UVSheetParser()
        success = parser.run(dry_run=False)

        if success:
            logger.info("Parser completed successfully")
            sys.exit(0)
        else:
            logger.error("Parser completed with errors")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
