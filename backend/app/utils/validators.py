import re

def validate_file_extension(filename: str, allowed: list[str] = ['.pdf']) -> bool:
    """Validate file extension."""
    if not filename:
        return False
    return any(filename.lower().endswith(ext) for ext in allowed)

def validate_file_size(file_size: int, max_size_mb: int = 10) -> bool:
    """Validate file size."""
    return file_size <= max_size_mb * 1024 * 1024

def is_valid_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return bool(re.match(pattern, email))

def is_valid_phone(phone: str) -> bool:
    """Validate phone format."""
    pattern = r'^\+?[0-9\-\s()]{7,15}$'
    return bool(re.match(pattern, phone))
