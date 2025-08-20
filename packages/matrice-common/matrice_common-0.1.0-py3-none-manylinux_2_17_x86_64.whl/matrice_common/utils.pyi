"""Auto-generated stub for module: utils."""
from typing import Any, Dict, List, Optional

from confluent_kafka import Producer
from datetime import datetime, timezone
from functools import lru_cache, wraps
from importlib.metadata import PackageNotFoundError, version
from matrice_common.rpc import RPC
import base64
import hashlib
import inspect
import json
import logging
import os
import subprocess
import traceback

# Constants
ERROR_TYPE_TO_MESSAGE: Dict[Any, Any]

# Functions
def cacheable(f: Any) -> Any: ...
    """
    Wraps a function to make its args hashable before caching.
    """
def check_for_duplicate(session: Any, service: Any, name: Any) -> Any: ...
    """
    Check if an item with the given name already exists for the specified service.
    """
def dependencies_check(package_names: Any) -> Any: ...
    """
    Check and install required dependencies.
    """
def get_summary(session: Any, project_id: Any, service_name: Any) -> Any: ...
    """
    Fetch a summary of the specified service in the project.
    """
def handle_response(response: Any, success_message: Any, failure_message: Any) -> Any: ...
    """
    Handle API response and return appropriate result.
    """
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
def send_error_log(filename: str, function_name: str, error_message: str, traceback_str: Optional[str] = None, additional_info: Optional[dict] = None, error_type: str = ErrorType.INTERNAL, service_name: str = 'matrice-sdk', action_id: Optional[str] = None, session_id: Optional[str] = None, access_key: Optional[str] = None, secret_key: Optional[str] = None) -> Any: ...
    """
    Log error to the backend system, sending to Kafka.
    """

# Classes
class AppError(Exception):
    def __init__(self: Any, error_type: str, error: Any, service_name: str, details: Optional[List[Any]] = None, action_id: Optional[str] = None, session_id: Optional[str] = None) -> None: ...

    def append(self: Any, *details: Any) -> Any: ...

    def generate_hash(self: Any) -> str: ...

class ErrorLog:
    def __init__(self: Any, service_name: str, stack_trace: str, error_type: str, description: str, file_name: str, function_name: str, hash: str, action_record_id: str = None, created_at: Any = None, is_resolved: bool = False, more_info: Optional[Any] = None) -> None: ...

    def to_dict(self: Any) -> dict: ...

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
