"""
openBIS connection handler.
Manages authentication using keyring for secure PAT storage.
"""

from typing import Optional
from getpass import getpass, getuser
from utils.logging_config import get_logger
from config import Config

logger = get_logger()

# Cache password during session
_cached_password = None


def get_openbis_connection():
    """
    Connect to openBIS using secure PAT from keyring.
    
    - First run: prompts for password, stores PAT securely
    - Subsequent runs: uses stored PAT automatically
    
    Returns:
        pybis.Openbis object if successful, None otherwise
    """
    try:
        import keyring
        from pybis import Openbis
    except ImportError as e:
        logger.error(f"Required package missing: {e}")
        logger.error("Install with: pip install pybis keyring")
        return None
    
    config = Config()
    url = config.openbis_url
    username = config.openbis_username
    
    if not username:
        logger.error("openBIS username not configured in config/settings.json")
        return None
    
    logger.info(f"Connecting to openBIS: {url}")
    logger.info(f"User: {username}")
    
    try:
        # Try to retrieve PAT from keyring
        pat = keyring.get_password("openbis", username)
        
        if pat:
            logger.info("Using stored PAT from keyring")
            openbis = Openbis(url, username=username, password=pat, verify_ssl=False)
            openbis.login()
            logger.info("Successfully logged in to openBIS")
            return openbis
        else:
            # Prompt for password
            logger.info("No PAT found in keyring. Prompting for password...")
            password = getpass(f"Enter openBIS password for {username}: ")
            
            if not password:
                logger.error("No password provided")
                return None
            
            # Store in keyring
            try:
                keyring.set_password("openbis", username, password)
                logger.info("Password stored securely in keyring")
            except Exception as e:
                logger.warning(f"Could not store password in keyring: {e}")
            
            # Connect
            openbis = Openbis(url, username=username, password=password, verify_ssl=False)
            openbis.login()
            logger.info("Successfully logged in to openBIS")
            return openbis
            
    except Exception as e:
        logger.error(f"Failed to connect to openBIS: {e}")
        return None


class OpenBISConnection:
    """openBIS connection manager."""
    
    def __init__(self):
        """Initialize connection manager."""
        self.openbis = None
    
    def connect(self):
        """Establish connection to openBIS."""
        if self.openbis is None:
            self.openbis = get_openbis_connection()
        return self.openbis
    
    def disconnect(self):
        """Disconnect from openBIS."""
        if self.openbis:
            try:
                self.openbis.logout()
                logger.info("Disconnected from openBIS")
            except Exception as e:
                logger.warning(f"Error during logout: {e}")
            self.openbis = None
    
    def is_connected(self) -> bool:
        """Check if connected to openBIS."""
        return self.openbis is not None
