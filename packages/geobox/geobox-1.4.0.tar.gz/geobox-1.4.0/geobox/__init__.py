"""
GeoBox SDK

This package provides classes and functions to interact with the GeoBox API.

Modules:
    api (module): Contains the Api class for making API requests.
    vectors (module): Contains classes for interacting with vector layers, fields, and features.
    exception (module): Contains custom exception classes for error handling.

Classes:
    Api: A class to interact with the GeoBox API.
    VectorLayers: A class to interact with vector layers in the GeoBox API.
    Fields: A class to interact with fields in a vector layer.
    Features: A class to interact with features in a vector layer.
    GeoboxError: Base class for all exceptions raised by the GeoBox SDK.
    AuthenticationError: Raised when there is an authentication error.
    AuthorizationError: Raised when there is an authorization error.
    ApiRequestError: Raised when there is an error with the API request.
    NotFoundError: Raised when a requested resource is not found.
    ValidationError: Raised when there is a validation error.
    ServerError: Raised when there is a server error.
"""
import logging, os, dotenv
from .api import GeoboxClient

from .exception import (
    GeoboxError,
    AuthenticationError,
    AuthorizationError,
    ApiRequestError,
    NotFoundError,
    ValidationError,
    ServerError
)

dotenv.load_dotenv()
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

logger = logging.getLogger(__name__)
if DEBUG:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger.info("Logging is set to DEBUG level.")
else:
    logging.basicConfig(level=logging.WARNING)


__all__ = [
    'GeoboxClient',
    'Feature',
    'VectorLayer',
    'GeoboxError',
    'AuthenticationError',
    'AuthorizationError',
    'ApiRequestError',
    'NotFoundError',
    'ValidationError',
    'ServerError'
]

