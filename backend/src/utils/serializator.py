from typing import Union, Optional
import re


async def resolve_phone(phone: Union[int, str]) -> Optional[str]:
    """
    Validates and normalizes a Russian phone number.

    Args:
        phone: Phone number as int or string (supports various formats)

    Returns:
        Normalized phone number (12 characters starting with +7) or None if invalid
    """
    # Convert to string and remove all special characters
    phone_str = str(phone).strip()
    cleaned = re.sub(r"[\s\-\(\)]", "", phone_str)

    # Replace 8 to 7
    if cleaned.startswith("8"):
        cleaned = cleaned.replace("8", "7", 1)

    # Add '+' if missing for consistent format
    if not cleaned.startswith("+"):
        cleaned = "+" + cleaned

    # Remove all non-digit characters except '+'
    cleaned = re.sub(r"[^\d+]", "", cleaned)

    # Check if starts with +7 and has exactly 12 characters total
    if cleaned.startswith("+7") and len(cleaned) == 12:
        return str(cleaned)

    return None
