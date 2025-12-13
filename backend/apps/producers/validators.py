"""
Validators for producer-related models and serializers.
"""
import os
from django.core.exceptions import ValidationError
from django.conf import settings
from PIL import Image


def validate_image_file(value):
    """
    Validate uploaded image file.
    """
    # Check file size
    max_size = settings.FILE_UPLOAD_MAX_MEMORY_SIZE
    if value.size > max_size:
        raise ValidationError(
            f'File size exceeds maximum allowed size of {max_size / (1024 * 1024):.1f} MB'
        )

    # Check file extension
    ext = os.path.splitext(value.name)[1][1:].lower()
    if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            f'File extension "{ext}" is not allowed. Allowed extensions: {", ".join(settings.ALLOWED_IMAGE_EXTENSIONS)}'
        )

    # Validate image format
    try:
        img = Image.open(value)
        img.verify()
    except Exception as e:
        raise ValidationError(f'Invalid image file: {str(e)}')

    return value


def validate_coordinates(latitude, longitude):
    """
    Validate geographic coordinates.
    """
    if not (-90 <= float(latitude) <= 90):
        raise ValidationError('Latitude must be between -90 and 90')
    if not (-180 <= float(longitude) <= 180):
        raise ValidationError('Longitude must be between -180 and 180')
    return True

