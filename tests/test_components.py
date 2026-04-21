"""
Unit tests for UV Sheet Parser components.
Tests Excel parsing, configuration, and object manager logic.
"""

import unittest
from pathlib import Path
import tempfile
import sys

from config import Config
from excel.excel_parser import ExcelParser
from utils.logging_config import get_logger

logger = get_logger("test_components")


class TestExcelParser(unittest.TestCase):
    """Test ExcelParser component."""
    
    def test_config_loading(self):
        """Test that config loads without errors."""
        try:
            config = Config()
            self.assertIsNotNone(config.openbis_url)
            self.assertIsNotNone(config.openbis_username)
            self.assertIsNotNone(config.openbis_space)
            self.assertIsNotNone(config.project_name)
            logger.info("✓ Config loaded successfully")
        except FileNotFoundError as e:
            logger.error(f"✗ Config not found: {e}")
            self.fail("config/settings.json not found")
    
    def test_excel_file_exists(self):
        """Test that Excel file exists."""
        config = Config()
        excel_file = Path(config.excel_file_path)
        
        if excel_file.exists():
            logger.info(f"✓ Excel file found: {excel_file}")
            self.assertTrue(excel_file.exists())
        else:
            logger.warning(f"✗ Excel file not found: {excel_file}")
            self.skipTest(f"Excel file not found: {excel_file}")
    
    def test_excel_parser_initialization(self):
        """Test ExcelParser initialization."""
        config = Config()
        excel_file = Path(config.excel_file_path)
        
        if not excel_file.exists():
            self.skipTest(f"Excel file not found: {excel_file}")
        
        try:
            parser = ExcelParser(excel_file)
            self.assertIsNotNone(parser.df)
            logger.info(f"✓ Excel parser initialized successfully")
            logger.info(f"  Loaded {len(parser.df)} rows")
            logger.info(f"  Columns: {list(parser.df.columns)}")
        except Exception as e:
            logger.error(f"✗ Error initializing parser: {e}")
            self.fail(f"Failed to initialize parser: {e}")
    
    def test_excel_columns_validation(self):
        """Test that Excel has all required columns."""
        config = Config()
        excel_file = Path(config.excel_file_path)
        
        if not excel_file.exists():
            self.skipTest(f"Excel file not found: {excel_file}")
        
        try:
            parser = ExcelParser(excel_file)
            logger.info("✓ All required columns present")
        except ValueError as e:
            logger.error(f"✗ Column validation failed: {e}")
            self.fail(f"Column validation error: {e}")
    
    def test_get_rows(self):
        """Test getting rows from Excel."""
        config = Config()
        excel_file = Path(config.excel_file_path)
        
        if not excel_file.exists():
            self.skipTest(f"Excel file not found: {excel_file}")
        
        try:
            parser = ExcelParser(excel_file)
            rows = parser.get_rows()
            self.assertIsInstance(rows, list)
            if rows:
                logger.info(f"✓ Retrieved {len(rows)} rows from Excel")
                first_row = rows[0]
                logger.info(f"  First row Code: {first_row.get('Code')}")
            else:
                logger.warning("✗ Excel file is empty")
        except Exception as e:
            logger.error(f"✗ Error getting rows: {e}")
            self.fail(f"Failed to get rows: {e}")
    
    def test_get_pending_rows(self):
        """Test getting pending (not yet uploaded) rows."""
        config = Config()
        excel_file = Path(config.excel_file_path)
        
        if not excel_file.exists():
            self.skipTest(f"Excel file not found: {excel_file}")
        
        try:
            parser = ExcelParser(excel_file)
            rows = parser.get_rows()
            pending = parser.get_pending_rows()
            
            logger.info(f"✓ Retrieved {len(pending)} pending rows out of {len(rows)}")
            
            # Show pending rows
            for row in pending:
                code = row.get('Code')
                uploaded = row.get('Uploaded', '')
                logger.info(f"  - {code} (Uploaded: {uploaded})")
        except Exception as e:
            logger.error(f"✗ Error getting pending rows: {e}")
            self.fail(f"Failed to get pending rows: {e}")


if __name__ == '__main__':
    logger.info("=" * 80)
    logger.info("UV Sheet Parser - Component Tests")
    logger.info("=" * 80)
    
    # Run tests
    unittest.main(verbosity=2)
