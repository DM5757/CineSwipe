"""Gemini error detail extraction and logging."""

from typing import Any


def gemini_error_details(exc: Exception) -> dict[str, str]:
    """Extract safe error fields from a Gemini API exception."""
    details: dict[str, str] = {
        "error_type": type(exc).__name__,
        "error_message": str(exc),
    }

    status_code = getattr(exc, "status_code", None)
    if status_code is None:
        status_code = getattr(exc, "code", None)
    if status_code is not None:
        details["status_code"] = str(status_code)

    extra_details = getattr(exc, "details", None)
    if extra_details:
        details["details"] = str(extra_details)

    return details


def log_gemini_error(exc: Exception) -> None:
    """Print and log Gemini failure details without exposing secrets."""
    info = gemini_error_details(exc)
    lines = [
        "Gemini request failed.",
        f"Error type: {info['error_type']}",
        f"Error message: {info['error_message']}",
    ]
    if info.get("status_code"):
        lines.append(f"Status code: {info['status_code']}")
    if info.get("details"):
        lines.append(f"Details: {info['details']}")

    message = "\n".join(lines)
    print(message)

    import logging

    logging.getLogger(__name__).warning(message)
