"""
Excel parser for UV Sheet Protocol file.
Reads and validates UV-Sheets_protocol.xlsx data.
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
from utils.logging_config import get_logger

logger = get_logger()


class ExcelParser:
    """Parse UV Sheet protocol Excel file."""
    
    REQUIRED_COLUMNS = [
        "Code",
        "Person",
        "Date",
        "Resin Name",
        "Resin Perm-ID",
        "Instrument",
        "Perm ID",
        "Spacer",
        "Duration [s]",
        "Number of Sheets",
        "Uploaded"
    ]
    
    def __init__(self, file_path: Path):
        """
        Initialize Excel parser.
        
        Args:
            file_path: Path to UV-Sheets_protocol.xlsx
            
        Raises:
            FileNotFoundError: If Excel file not found
        """
        self.file_path = Path(file_path)
        
        if not self.file_path.exists():
            raise FileNotFoundError(f"Excel file not found: {self.file_path}")
        
        logger.info(f"Loading Excel file: {self.file_path}")
        self.df = pd.read_excel(self.file_path)
        self._validate_columns()
        logger.info(f"Loaded {len(self.df)} rows from Excel file")
    
    def _validate_columns(self) -> None:
        """Validate that all required columns exist."""
        missing = set(self.REQUIRED_COLUMNS) - set(self.df.columns)
        if missing:
            raise ValueError(
                f"Missing required columns: {missing}\n"
                f"Found columns: {list(self.df.columns)}"
            )
    
    def get_rows(self) -> List[Dict[str, Any]]:
        """
        Get all rows as list of dictionaries.
        
        Returns:
            List of row dictionaries
        """
        return self.df.to_dict('records')
    
    def get_pending_rows(self) -> List[Dict[str, Any]]:
        """
        Get only rows that haven't been uploaded yet.
        
        Returns:
            List of pending row dictionaries
        """
        # Rows are pending if Uploaded column is not "Yes" (case-insensitive)
        # This includes empty/NaN values
        uploaded_col = self.df["Uploaded"].fillna("").astype(str).str.strip().str.lower()
        pending = self.df[uploaded_col != "yes"].copy()
        
        logger.info(f"Found {len(pending)} pending rows (Uploaded != 'Yes')")
        return pending.to_dict('records')
    
    def update_uploaded(self, code: str) -> bool:
        """
        Mark a row as uploaded by Code.
        
        Args:
            code: Code value to find and update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            mask = self.df["Code"] == code
            if not mask.any():
                logger.warning(f"Code '{code}' not found in Excel file")
                return False
            
            self.df.loc[mask, "Uploaded"] = "Yes"
            logger.info(f"Marked '{code}' as Uploaded")
            return True
        except Exception as e:
            logger.error(f"Error updating Excel row for '{code}': {e}")
            return False
    
    def save(self) -> bool:
        """
        Save changes to Excel file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.df.to_excel(self.file_path, index=False, engine='openpyxl')
            logger.info(f"Saved Excel file: {self.file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving Excel file: {e}")
            return False
    
    def get_row_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific row by Code.
        
        Args:
            code: Code value to find
            
        Returns:
            Row dictionary or None if not found
        """
        mask = self.df["Code"] == code
        if mask.any():
            return self.df[mask].iloc[0].to_dict()
        return None
