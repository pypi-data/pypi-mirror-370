"""Auto-generated stub for module: token_auth."""
from typing import Any, Optional

from datetime import datetime, timezone
from dateutil.parser import parse
from requests.auth import AuthBase
import json
import os
import requests
import sys

# Classes
class AuthToken(AuthBase):
    """
    Implements a custom authentication scheme using a refresh token.
    """

    def __init__(self: Any, access_key: str, secret_key: str, refresh_token: Any) -> None: ...
        """
        Initialize the AuthToken instance.
        
        Args:
            access_key (str): Access key for authentication.
            secret_key (str): Secret key for authentication.
            refresh_token (RefreshToken): Instance of RefreshToken for obtaining bearer tokens.
        """

    def set_bearer_token(self: Any) -> None: ...
        """
        Obtain an authentication bearer token using the provided refresh token.
        
        Raises:
            SystemExit: If the request to the authentication server fails or the credentials are incorrect.
        """

class RefreshToken(AuthBase):
    """
    Implements a custom authentication scheme using access and secret keys.
    """

    def __init__(self: Any, access_key: str, secret_key: str) -> None: ...
        """
        Initialize the RefreshToken instance.
        
        Args:
            access_key (str): Access key for authentication.
            secret_key (str): Secret key for authentication.
        """

    def set_bearer_token(self: Any) -> None: ...
        """
        Obtain a bearer token using the provided access key and secret key.
        
        Raises:
            SystemExit: If the request to the authentication server fails or the credentials are incorrect.
        """

