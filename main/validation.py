"""Validation shared by Django forms and the DRF input boundary."""
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
    parts = urlsplit(value)
    if value.startswith("/") and not value.startswith("//") and not parts.scheme and not parts.netloc:
        return value
    URLValidator(schemes=["http", "https"])(value)
    return value


def experience_dates(started_at, ended_at):
    if started_at and ended_at and ended_at < started_at:
        raise ValidationError("End date cannot be earlier than start date.")
