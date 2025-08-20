"""Auto-generated stub for module: rpc."""
from typing import Any, Dict, Optional, Union

from datetime import datetime, timedelta, timezone
from importlib.metadata import version
from matrice_common.token_auth import AuthToken, RefreshToken
from matrice_common.utils import log_errors
import logging
import os
import requests

# Classes
class RPC:
    """
    RPC class for handling backend API requests with token-based authentication.
    """

    def __init__(self: Any, access_key: Optional[str] = None, secret_key: Optional[str] = None, project_id: Optional[str] = None) -> None: ...
        """
        Initialize the RPC client with optional project ID.
        
        Args:
            access_key (Optional[str]): Access key for authentication. Defaults to None.
            secret_key (Optional[str]): Secret key for authentication. Defaults to None.
            project_id (Optional[str]): Project ID for API requests. Defaults to None.
        
        Raises:
            ValueError: If access key or secret key is not provided.
        """

    def add_project_id(self: Any, url: str) -> str: ...
        """
        Add project ID to the URL if present and not already included.
        
        Args:
            url (str): The URL to modify.
        
        Returns:
            str: The modified URL with the project ID appended if applicable.
        """

    def delete(self: Any, path: str, payload: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, timeout: int = 60, raise_exception: bool = True) -> Optional[Dict[str, Any]]: ...
        """
        Send a DELETE request to the specified endpoint.
        
        Args:
            path (str): API endpoint path.
            payload (Optional[Dict[str, Any]]): JSON payload for the request. Defaults to None.
            headers (Optional[Dict[str, str]]): HTTP headers. Defaults to None.
            timeout (int): Timeout for the request in seconds. Defaults to 60.
            raise_exception (bool): Whether to raise an exception on failure. Defaults to True.
        
        Returns:
            Optional[Dict[str, Any]]: Parsed JSON response data, or None if an error occurs.
        """

    def get(self: Any, path: str, params: Optional[Dict[str, Any]] = None, timeout: int = 60, raise_exception: bool = True) -> Optional[Dict[str, Any]]: ...
        """
        Send a GET request to the specified endpoint.
        
        Args:
            path (str): API endpoint path.
            params (Optional[Dict[str, Any]]): Query parameters for the request. Defaults to None.
            timeout (int): Timeout for the request in seconds. Defaults to 60.
            raise_exception (bool): Whether to raise an exception on failure. Defaults to True.
        
        Returns:
            Optional[Dict[str, Any]]: Parsed JSON response data, or None if an error occurs.
        """

    def post(self: Any, path: str, payload: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, files: Optional[Dict[str, Any]] = None, data: Optional[Union[Dict[str, Any], str]] = None, timeout: int = 60, raise_exception: bool = True) -> Optional[Dict[str, Any]]: ...
        """
        Send a POST request to the specified endpoint.
        
        Args:
            path (str): API endpoint path.
            payload (Optional[Dict[str, Any]]): JSON payload for the request. Defaults to None.
            headers (Optional[Dict[str, str]]): HTTP headers. Defaults to None.
            files (Optional[Dict[str, Any]]): Files to upload. Defaults to None.
            data (Optional[Union[Dict[str, Any], str]]): Form data or raw data. Defaults to None.
            timeout (int): Timeout for the request in seconds. Defaults to 60.
            raise_exception (bool): Whether to raise an exception on failure. Defaults to True.
        
        Returns:
            Optional[Dict[str, Any]]: Parsed JSON response data, or None if an error occurs.
        """

    def put(self: Any, path: str, payload: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, timeout: int = 60, raise_exception: bool = True) -> Optional[Dict[str, Any]]: ...
        """
        Send a PUT request to the specified endpoint.
        
        Args:
            path (str): API endpoint path.
            payload (Optional[Dict[str, Any]]): JSON payload for the request. Defaults to None.
            headers (Optional[Dict[str, str]]): HTTP headers. Defaults to None.
            timeout (int): Timeout for the request in seconds. Defaults to 60.
            raise_exception (bool): Whether to raise an exception on failure. Defaults to True.
        
        Returns:
            Optional[Dict[str, Any]]: Parsed JSON response data, or None if an error occurs.
        """

    def refresh_token(self: Any) -> None: ...
        """
        Refresh the authentication token if expired.
        
        Raises:
            Exception: If an error occurs while refreshing the token.
        """

    def send_request(self: Any, method: str, path: str, headers: Optional[Dict[str, str]] = None, payload: Optional[Dict[str, Any]] = None, files: Optional[Dict[str, Any]] = None, data: Optional[Union[Dict[str, Any], str]] = None, timeout: int = 60, raise_exception: bool = True) -> Optional[Dict[str, Any]]: ...
        """
        Send an HTTP request to the specified endpoint.
        
        Args:
            method (str): HTTP method (e.g., 'GET', 'POST', 'PUT', 'DELETE').
            path (str): API endpoint path.
            headers (Optional[Dict[str, str]]): HTTP headers. Defaults to None.
            payload (Optional[Dict[str, Any]]): JSON payload for the request. Defaults to None.
            files (Optional[Dict[str, Any]]): Files to upload. Defaults to None.
            data (Optional[Union[Dict[str, Any], str]]): Form data or raw data. Defaults to None.
            timeout (int): Timeout for the request in seconds. Defaults to 60.
            raise_exception (bool): Whether to raise an exception on failure. Defaults to True.
        
        Returns:
            Optional[Dict[str, Any]]: Parsed JSON response data, or None if an error occurs.
        """

