"""
Custom exception handlers for DRF.
"""
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # Handle Django validation errors
    if isinstance(exc, DjangoValidationError):
        response = Response(
            {
                'error': 'Validation error',
                'details': exc.message_dict if hasattr(exc, 'message_dict') else str(exc)
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Handle database integrity errors
    if isinstance(exc, IntegrityError):
        logger.error(f"Integrity error: {exc}", exc_info=True)
        response = Response(
            {
                'error': 'Database integrity error',
                'details': 'This operation violates database constraints.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Log unexpected errors
    if response is None:
        logger.error(f"Unhandled exception: {exc}", exc_info=True, extra={'context': context})
        response = Response(
            {
                'error': 'Internal server error',
                'details': 'An unexpected error occurred. Please try again later.'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Add request ID or other context if needed
    if response is not None:
        # Ensure consistent error format
        if 'error' not in response.data:
            if isinstance(response.data, dict):
                response.data = {'error': 'Request failed', 'details': response.data}
            else:
                response.data = {'error': 'Request failed', 'details': str(response.data)}

    return response

