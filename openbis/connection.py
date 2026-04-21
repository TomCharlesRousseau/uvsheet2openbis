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


def pat_exists(username: str) -> bool:
    """
    Check if a valid PAT exists in keyring for the given user.
    
    Returns:
        bool: True if PAT exists, False otherwise
    """
    try:
        import keyring
        pat = keyring.get_password("openbis", username)
        return pat is not None
    except Exception:
        return False


def get_openbis_connection(force_password: bool = False) -> Optional[Tuple]:
    """
    Connect to openBIS using stored PAT from keyring.
    Fallback to interactive password login if no valid PAT exists.
    
    Parameters:
    -----------
    - force_password: If True, skip PAT check and prompt for password directly
    
    Behavior:
    - force_password=False: Try PAT first, fallback to password if PAT missing/expired
    - force_password=True: Skip PAT entirely, prompt for password directly
    
    Returns:
        Tuple: (Openbis object, username, space, pat_found) if successful, None otherwise
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
    space = config.openbis_space
    
    if not username:
        logger.error("openBIS username not configured in config/settings.json")
        return None
    
    logger.info(f"Connecting to openBIS: {url}")
    logger.info(f"User: {username}")
    
    try:
        # If force_password is True, skip PAT and go straight to password prompt
        if force_password:
            openbis = Openbis(url)
            _cached_password = None
            password = getpass(f"Enter openBIS password for {username} at {url}: ")
            openbis.login(username, password)
            logger.info(f"Connected using password for user {username}")
            
            # Store the new PAT securely in keyring for next run
            try:
                keyring.set_password("openbis", username, openbis.token)
                logger.info("PAT stored securely in keyring for future use")
            except Exception as e:
                logger.warning(f"Could not store PAT in keyring: {e}")
            
            return openbis, username, space, False
        
        # Try to retrieve PAT from keyring first
        pat = keyring.get_password("openbis", username)
        
        if pat:
            try:
                logger.info("Attempting to use stored PAT from keyring")
                openbis = Openbis(url, token=pat)
                logger.info("Successfully connected using stored PAT")
                return openbis, username, space, True
            except ValueError as e:
                logger.warning(f"Stored PAT expired or invalid: {e}")
                logger.info("Prompting for new password...")
        
        # Fallback: prompt for password login
        openbis = Openbis(url)
        password = getpass(f"Enter openBIS password for {username} at {url}: ")
        openbis.login(username, password)
        logger.info(f"Connected using password for user {username}")
        
        # Extract PAT from session and store in keyring for next run
        try:
            keyring.set_password("openbis", username, openbis.token)
            logger.info("PAT stored securely in keyring for future use")
        except Exception as e:
            logger.warning(f"Could not store PAT in keyring: {e}")
        
        return openbis, username, space, False
        
    except Exception as e:
        logger.error(f"Failed to connect to openBIS: {e}")
        return None


class OpenBISConnection:
    """openBIS connection manager."""
    
    def __init__(self):
        """Initialize connection manager."""
        self.openbis = None
        self.username = None
        self.space = None
        self.pat_found = False
    
    def connect(self, force_password: bool = False):
        """
        Establish connection to openBIS.
        
        Parameters:
        -----------
        - force_password: If True, skip PAT and force password prompt
        
        Returns: Openbis object if successful, None otherwise
        """
        result = get_openbis_connection(force_password=force_password)
        
        if result is None:
            return None
        
        self.openbis, self.username, self.space, self.pat_found = result
        return self.openbis
    
    def disconnect(self):
        """Disconnect from openBIS."""
        if self.openbis:
            try:
                self.openbis.logout()
                logger.info("Disconnected from openBIS")
            except Exception as e:
                logger.warning(f"Error during logout: {e}")
            finally:
                self.openbis = None
    
    def is_connected(self) -> bool:
        """Check if connected to openBIS."""
        return self.openbis is not None
