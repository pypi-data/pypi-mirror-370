from functools import lru_cache

from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@lru_cache(maxsize=128)
def create_session_with_retries() -> Session:
    """
    Creates a requests Session with retry capabilities for improved resilience.

    Returns:
        Session: A requests Session configured with retry capabilities.
    """
    # Import get_settings lazily to avoid circular imports
    from apheris_utils.data.primitives._settings import get_settings

    session = Session()
    retry = Retry(
        total=5,  # Total number of retries
        backoff_factor=2,  # Exponential backoff factor
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
    )
    adapter = HTTPAdapter(max_retries=retry, pool_maxsize=get_settings().max_workers)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session
