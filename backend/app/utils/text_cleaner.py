import re

def sanitize_text(text: str) -> str:
    """Basic text sanitization."""
    if not text:
        return ""
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def truncate_text(text: str, max_length: int = 10000) -> str:
    """Truncate text safely."""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length]
