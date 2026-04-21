"""
openBIS connection handler.
Supports PAT (Personal Access Token) with keyring caching and password fallback.
"""

from getpass import getpass
from utils.logging_config import get_logger
from config import Config

logger = get_logger()

# Optional keyring import for secure credential storage
try:
    import keyring

    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False
    logger.warning("keyring not available. Install with: pip install keyring")


def _get_cached_pat(username: str) -> str:
    """
    Retrieve cached PAT from system keyring.

    Args:
        username: openBIS username

    Returns:
        Cached PAT or empty string if not found
    """
    if not KEYRING_AVAILABLE:
        logger.info("⚠ Keyring not available - will use password login")
        return ""

    try:
        pat = keyring.get_password("openbis", username)
        if pat:
            logger.debug(f"Retrieved cached PAT for {username}")
            return pat
        else:
            logger.info(f"ℹ No cached PAT found in keyring for {username}")
            return ""
    except Exception as e:
        logger.warning(f"⚠ Error retrieving PAT from keyring: {e}")
        return ""


def _cache_pat(username: str, pat: str) -> bool:
    """
    Cache PAT in system keyring.

    Args:
        username: openBIS username
        pat: Personal Access Token

    Returns:
        True if cached successfully, False otherwise
    """
    if not KEYRING_AVAILABLE:
        logger.debug("Keyring not available. PAT not cached.")
        return False

    try:
        keyring.set_password("openbis", username, pat)
        logger.debug(f"Cached PAT for {username}")
        return True
    except Exception as e:
        logger.warning(f"Could not cache PAT: {e}")
        return False


def _generate_pat(openbis, username: str, password: str):
    """
    Extract the PAT token from openbis object after successful login.

    Args:
        openbis: Connected pybis.Openbis instance (already logged in)
        username: openBIS username
        password: openBIS password (not used, just for signature)

    Returns:
        PAT token string or None if not available
    """
    try:
        # After successful login, pybis sets o.token with the actual PAT
        if hasattr(openbis, 'token') and openbis.token:
            logger.debug(f"Extracted PAT token for {username}")
            return openbis.token
        else:
            logger.warning(f"No token available in openbis object for {username}")
            return None
    except Exception as e:
        logger.debug(f"Could not extract PAT: {e}")
        return None


def get_openbis_connection():
    """
    Connect to openBIS using PAT-first authentication strategy.

    Attempts:
    1. Cached PAT from keyring (fast)
    2. Password login with PAT generation and caching

    Returns:
        pybis.Openbis object if successful, None otherwise
    """
    try:
        from pybis import Openbis
    except ImportError as e:
        logger.error(f"Required package missing: {e}")
        logger.error("Install with: pip install pybis")
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
        # Try cached PAT first
        cached_pat = _get_cached_pat(username)
        if cached_pat:
            logger.info("Attempting login with cached PAT...")
            try:
                openbis = Openbis(url, token=cached_pat)
                logger.info("Successfully logged in with cached PAT")
                return openbis
            except Exception as e:
                logger.debug(f"Cached PAT expired or invalid: {e}")
                logger.info("Falling back to password authentication...")

        # Fall back to password authentication
        logger.info("Attempting login with password...")
        openbis = Openbis(url)
        password = getpass(f"Enter openBIS password for {username}: ")

        if not password:
            logger.error("No password provided")
            return None

        openbis.login(username, password)
        logger.info("Successfully logged in with password")

        # Try to extract and cache PAT
        pat = _generate_pat(openbis, username, password)
        if pat:
            if _cache_pat(username, pat):
                logger.info(f"✓ PAT cached successfully for {username} (will be used next time)")
            else:
                logger.warning("Failed to cache PAT - password will be used next time")
        else:
            logger.warning("No PAT token available to cache - password will be used next time")

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
