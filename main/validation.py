"""Validation shared by Django forms and the DRF input boundary."""
import re
from urllib.parse import urlsplit

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.html import strip_tags


def plain_text(value):
    value = strip_tags(value).strip()
    if not value:
        raise ValidationError("This field must contain readable text.")
    return value


def image_url(value):
    value = value.strip()
    # Existing portfolio assets use root-relative static paths.
    if any(char.isspace() or ord(char) < 32 for char in value) or "\\" in value:
        raise ValidationError("Use an HTTP(S) image URL or a root-relative asset path.")
    try:
        parts = urlsplit(value)
    except ValueError as error:
        raise ValidationError("Enter a valid image URL.") from error
    if value.startswith("/") and not value.startswith("//") and not parts.scheme and not parts.netloc:
        return value
    URLValidator(schemes=["http", "https"])(value)
    return value


def experience_dates(started_at, ended_at):
    if started_at and ended_at and ended_at < started_at:
        raise ValidationError("End date cannot be earlier than start date.")


def clean_experience_description(value):
    """Convert legacy list markup to readable plain text before JSON serialization."""
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"<\s*/\s*li\s*>", "\n", value, flags=re.IGNORECASE)
    value = re.sub(r"<\s*li\b[^>]*>", "- ", value, flags=re.IGNORECASE)
    return strip_tags(value).strip()
