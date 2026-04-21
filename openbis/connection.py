"""
openBIS connection handler.
Manages authentication using keyring for secure PAT/token storage.
"""

from typing import Optional, Tuple
from getpass import getpass, getuser
from utils.logging_config import get_logger
from config import Config

logger = get_logger()

# Cache password during session
_cached_password = None


def get_openbis_connection() -> Optional[object]:
    """
    Connect to openBIS using stored PAT from keyring.
    Fallback to interactive password login if no valid PAT exists.
    
    - First run: prompts for password, stores token securely
    - Subsequent runs: uses stored token automatically
    - If token expires: prompts for password again
    
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
    
    global _cached_password
    
    config = Config()
    url = config.openbis_url
    username = config.openbis_username
    
    if not username:
        logger.error("openBIS username not configured in config/settings.json")
        return None
    
    logger.info(f"Connecting to openBIS: {url}")
    logger.info(f"User: {username}")
    
    try:
        # Try to retrieve PAT/token from keyring
        pat = keyring.get_password("openbis", username)
        
        if pat:
            try:
                logger.info("Attempting to use stored PAT from keyring")
                openbis = Openbis(url, token=pat)
                logger.info("Successfully connected using stored PAT")
                return openbis
            except ValueError as e:
                logger.warning(f"Stored PAT expired or invalid: {e}")
                logger.info("Falling back to password login...")
        
        # Fallback: password login
        openbis = Openbis(url)
        
        if not _cached_password:
            _cached_password = getpass(f"Enter openBIS password for {username} at {url}: ")
        
        if not _cached_password:
            logger.error("No password provided")
            return None
        
        logger.info("Attempting to login with password...")
        openbis.login(username, _cached_password)
        logger.info("Successfully logged in with password")
        
        # Store the new token securely in keyring for next run
        try:
            keyring.set_password("openbis", username, openbis.token)
            logger.info("Token stored securely in keyring for future use")
        except Exception as e:
            logger.warning(f"Could not store token in keyring: {e}")
        
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
