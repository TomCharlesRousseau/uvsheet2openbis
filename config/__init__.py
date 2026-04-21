"""
Configuration management for UV Sheet Parser.
Loads settings from config/settings.json and provides centralized access.
"""

import json
from pathlib import Path
from typing import Dict, Any

CONFIG_FILE = Path(__file__).parent / "settings.json"


class Config:
    """Centralized configuration class."""
    
    _instance = None
    _settings: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self) -> None:
        """Load configuration from settings.json"""
        if not CONFIG_FILE.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {CONFIG_FILE}\n"
                "Please create config/settings.json with your openBIS credentials."
            )
        
        try:
            with open(CONFIG_FILE, "r") as f:
                self._settings = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in settings.json: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key.split(".")
        value = self._settings
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    @property
    def openbis_url(self) -> str:
        """openBIS API URL."""
        return self.get("openbis.api_url")
    
    @property
    def openbis_username(self) -> str:
        """openBIS username."""
        return self.get("openbis.username")
    
    @property
    def openbis_space(self) -> str:
        """openBIS space name."""
        return self.get("openbis.space")
    
    @property
    def project_name(self) -> str:
        """openBIS project name."""
        return self.get("openbis.project_name")
    
    @property
    def openbis_project_path(self) -> str:
        """Full openBIS project path (Space/Project)."""
        return f"{self.openbis_space}/{self.project_name}"
    
    @property
    def excel_file_path(self) -> str:
        """Excel file path."""
        return self.get("excel.file_path", "UV-Sheets_protocol.xlsx")


__all__ = ['Config']
