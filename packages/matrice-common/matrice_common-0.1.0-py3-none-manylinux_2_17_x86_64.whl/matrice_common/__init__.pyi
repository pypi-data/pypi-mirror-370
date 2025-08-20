"""Auto-generated stubs for package: matrice_common."""
from typing import Any, Dict, List, Optional, Tuple, Union

from confluent_kafka import Producer
from datetime import datetime
from datetime import datetime, timedelta, timezone
from datetime import datetime, timezone
from dateutil.parser import parse
from functools import lru_cache, wraps
from importlib.metadata import PackageNotFoundError, version
from importlib.metadata import version
from matrice.projects import Projects
from matrice_common.rpc import RPC
from matrice_common.token_auth import AuthToken, RefreshToken
from matrice_common.utils import handle_response
from matrice_common.utils import log_errors
from requests.auth import AuthBase
from urllib.parse import urlencode
import base64
import hashlib
import inspect
import json
import logging
import os
import requests
import subprocess
import sys
import traceback

# Constants
ERROR_TYPE_TO_MESSAGE: Dict[Any, Any] = ...  # From utils

# Functions
# From session
def create_session(account_number: Any, access_key: Any, secret_key: Any) -> Any: ...
    """
    Create and initialize a new session with specified credentials.
    
    Parameters
    ----------
    account_number : str
        The account number to associate with the new session.
    access_key : str
        The access key for authentication.
    secret_key : str
        The secret key for authentication.
    
    Returns
    -------
    Session
        An instance of the Session class initialized with the given credentials.
    
    Example
    -------
    >>> session = create_session("9625383462734064921642156", "HREDGFXB6KI0TWH6UZEYR",
    "UY8LP0GQRKLSFPZAW1AUF")
    >>> print(session)
    <Session object at 0x...>
    """

# From utils
def cacheable(f: Any) -> Any: ...
    """
    Wraps a function to make its args hashable before caching.
    """

# From utils
def check_for_duplicate(session: Any, service: Any, name: Any) -> Any: ...
    """
    Check if an item with the given name already exists for the specified service.
    """

# From utils
def dependencies_check(package_names: Any) -> Any: ...
    """
    Check and install required dependencies.
    """

# From utils
def get_summary(session: Any, project_id: Any, service_name: Any) -> Any: ...
    """
    Fetch a summary of the specified service in the project.
    """

# From utils
def handle_response(response: Any, success_message: Any, failure_message: Any) -> Any: ...
    """
    Handle API response and return appropriate result.
    """

# From utils
def log_errors(func: Any = None, default_return: Any = None, raise_exception: Any = False, log_error: Any = True) -> Any: ...
    """
    Decorator to automatically log exceptions raised in functions.
    
        This decorator catches any exceptions raised in the decorated function,
        logs them using the log_error function, and optionally re-raises the exception.
    
        Args:
            func: The function to decorate
            default_return: Value to return if an exception occurs (default: None)
            raise_exception: Whether to raise the exception (default: False)
            log_error: Whether to log the error (default: True)
        Returns:
            The wrapped function with error logging
    """

# From utils
def send_error_log(filename: str, function_name: str, error_message: str, traceback_str: Optional[str] = None, additional_info: Optional[dict] = None, error_type: str = ErrorType.INTERNAL, service_name: str = 'matrice-sdk', action_id: Optional[str] = None, session_id: Optional[str] = None, access_key: Optional[str] = None, secret_key: Optional[str] = None) -> Any: ...
    """
    Log error to the backend system, sending to Kafka.
    """

# Classes
# From rpc
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


# From session
class Session:
    """
    Class to manage sessions.
    
        Initialize a new session instance.
    
        Parameters
        ----------
        account_number : str
            The account number associated with the session.
        project_id : str, optional
            The ID of the project for this session.
        Example
        -------
        >>> session = Session(account_number="9625383462734064921642156")
    """

    def __init__(self: Any, account_number: Any, access_key: Any = None, secret_key: Any = None, project_id: Any = None, project_name: Any = None) -> None: ...

    def close(self: Any) -> Any: ...
        """
        Close the current session by resetting the RPC and project details.
        
        Example
        -------
        >>> session.close()
        """

    def create_classification_project(self: Any, project_name: Any, industries: Any = ['general'], tags: Any = [], computeType: Any = 'matrice', storageType: Any = 'matrice', supportedDevices: Any = 'nvidia_gpu', deploymentSupportedDevices: Any = 'nvidia_gpu') -> Any: ...
        """
        Create a classification project.
        
        Parameters
        ----------
        project_name : str
            The name of the classification project to be created.
        
        Returns
        -------
        Projects
            An instance of the Projects class for the created project, or None if an error occurred.
        
        Example
        -------
        >>> project = session.create_classification_project("Image Classification Project")
        >>> if project:
        >>>     print(f"Created project: {project}")
        >>> else:
        >>>     print("Could not create project.")
        """

    def create_detection_project(self: Any, project_name: Any) -> Any: ...
        """
        Create a detection project.
        
        Parameters
        ----------
        project_name : str
            The name of the detection project to be created.
        
        Returns
        -------
        Projects
            An instance of the Projects class for the created project, or None if an error occurred.
        
        Example
        -------
        >>> project = session.create_detection_project("Object Detection Project")
        >>> if project:
        >>>     print(f"Created project: {project}")
        >>> else:
        >>>     print("Could not create project.")
        """

    def create_segmentation_project(self: Any, project_name: Any) -> Any: ...
        """
        Create a segmentation project.
        
        Parameters
        ----------
        project_name : str
            The name of the segmentation project to be created.
        
        Returns
        -------
        Projects
            An instance of the Projects class for the created project, or None if an error occurred.
        
        Example
        -------
        >>> project = session.create_segmentation_project("Instance Segmentation Project")
        >>> if project:
        >>>     print(f"Created project: {project}")
        >>> else:
        >>>     print("Could not create project.")
        """

    def get_project_type_summary(self: Any) -> Any: ...
        """
        Get the count of different types of projects.
        
        Returns
        -------
        tuple
            A tuple containing:
            - A dictionary with project types as keys and their counts as values if the request is
                successful.
            - An error message if the request fails.
        
        Example
        -------
        >>> project_summary, error = session.get_project_type_summary()
        >>> if error:
        >>>     print(f"Error: {error}")
        >>> else:
        >>>     print(f"Project type summary: {project_summary}")
        """

    def list_projects(self: Any, project_type: Any = '', page_size: Any = 10, page_number: Any = 0) -> Any: ...
        """
        List projects based on the specified type.
        
        Parameters
        ----------
        project_type : str, optional
            The type of projects to list (e.g., 'classification', 'detection'). If empty,
            all projects are listed.
        
        Returns
        -------
        tuple
            A tuple containing the dictionary of projects and a message indicating the result of
                the fetch operation.
        
        Example
        -------
        >>> projects, message = session.list_projects("classification")
        >>> print(message)
        Projects fetched successfully
        >>> for project_name, project_instance in projects.items():
        >>>     print(project_name, project_instance)
        """

    def refresh(self: Any) -> Any: ...
        """
        Refresh the instance by reinstantiating it with the previous values.
        """

    def update(self: Any, project_id: Any) -> Any: ...
        """
        Update the session with new project details.
        
        Parameters
        ----------
        project_id : str, optional
            The new ID of the project.
        
        
        Example
        -------
        >>> session.update(project_id="660b96fc019dd5321fd4f8c7")
        """


# From token_auth
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


# From token_auth
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


# From utils
class AppError(Exception):
    def __init__(self: Any, error_type: str, error: Any, service_name: str, details: Optional[List[Any]] = None, action_id: Optional[str] = None, session_id: Optional[str] = None) -> None: ...

    def append(self: Any, *details: Any) -> Any: ...

    def generate_hash(self: Any) -> str: ...


# From utils
class ErrorLog:
    def __init__(self: Any, service_name: str, stack_trace: str, error_type: str, description: str, file_name: str, function_name: str, hash: str, action_record_id: str = None, created_at: Any = None, is_resolved: bool = False, more_info: Optional[Any] = None) -> None: ...

    def to_dict(self: Any) -> dict: ...


# From utils
class ErrorType:
    ASSERTION_ERROR: str
    ATTRIBUTE_ERROR: str
    CONNECTION_ERROR: str
    FILE_NOT_FOUND: str
    IMPORT_ERROR: str
    INDEX_ERROR: str
    INTERNAL: str
    JSON_DECODE_ERROR: str
    KEY_ERROR: str
    MEMORY_ERROR: str
    NOT_FOUND: str
    OS_ERROR: str
    PERMISSION_DENIED: str
    PRECONDITION_FAILED: str
    RUNTIME_ERROR: str
    STOP_ITERATION: str
    TIMEOUT: str
    TYPE_ERROR: str
    UNAUTHENTICATED: str
    UNAUTHORIZED: str
    UNKNOWN: str
    VALIDATION_ERROR: str
    VALUE_ERROR: str

    pass

from . import rpc, session, token_auth, utils

def __getattr__(name: str) -> Any: ...