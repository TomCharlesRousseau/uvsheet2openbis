"""
openBIS connection handler.
Manages authentication using keyring for secure PAT/token storage.
"""

import keyring
from pybis import Openbis
from getpass import getpass, getuser
from utils.logging_config import get_logger
from config import Config

logger = get_logger()

# Cache password during session
_cached_password = None


def pat_exists(userid):
    """Check if a valid PAT exists in keyring for the given user."""
    pat = keyring.get_password("openbis", userid)
    return pat is not None


def connect_openbis(url=None, userid=None, space=None, force_password=False):
    """
    Connect to OpenBIS with dual-authentication support.

    Parameters:
    -----------
    - url: OpenBIS server URL (uses config if None)
    - userid: Username (uses system user if None)
    - space: Optional space (uses config if None)
    - force_password: If True, skip PAT check and prompt for password directly

    Returns: (Openbis object, userid, space, pat_found)

    Behavior:
    - force_password=False: Try PAT first, fallback to password if PAT missing/expired
    - force_password=True: Skip PAT entirely, prompt for password directly
    """
    global _cached_password
    
    # Load config if not provided
    config = Config()
    url = url or config.openbis_url
    userid = userid or config.openbis_username
    space = space or config.openbis_space
    
    resolved_userid = userid or getuser()

    # If force_password is True, skip PAT and go straight to password prompt
    if force_password:
        o = Openbis(url)
        _cached_password = None
        password = getpass(f"Enter password for user {resolved_userid} at {url}: ")
        o.login(resolved_userid, password)
        logger.info(f"Connected using password for user {resolved_userid}")
        
        keyring.set_password("openbis", resolved_userid, o.token)
        logger.info("PAT stored securely in keyring for next run")
        return o, resolved_userid, space, False

    # Try to retrieve PAT from keyring (when force_password=False)
    pat = keyring.get_password("openbis", resolved_userid)

    if pat:
        try:
            o = Openbis(url, token=pat)
            logger.info(f"Connected using PAT for user {resolved_userid}")
            return o, resolved_userid, space, True
        except ValueError:
            logger.warning("Stored PAT expired or invalid, fallback to password login")

    # Fallback password login (PAT doesn't exist or is expired)
    o = Openbis(url)
    password = getpass(f"Enter password for user {resolved_userid} at {url}: ")
    o.login(resolved_userid, password)
    logger.info(f"Connected using password for user {resolved_userid}")

    # Store the new PAT securely in keyring for next run
    keyring.set_password("openbis", resolved_userid, o.token)
    logger.info("PAT stored securely in keyring for next run")
    return o, resolved_userid, space, False




class OpenBISConnection:
    """openBIS connection manager."""
    
    def __init__(self):
        """Initialize connection manager."""
        self.openbis = None
        self.username = None
        self.space = None
        self.pat_found = False
    
    def connect(self, force_password=False):
        """
        Establish connection to openBIS.
        
        Parameters:
        -----------
        - force_password: If True, skip PAT and force password prompt
        
        Returns: Openbis object if successful, None otherwise
        """
        result = connect_openbis(force_password=force_password)
        
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
    
    def is_connected(self):
        """Check if connected to openBIS."""
        return self.openbis is not None
