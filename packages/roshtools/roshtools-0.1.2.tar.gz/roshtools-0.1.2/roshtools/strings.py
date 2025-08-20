def slugify(text: str) -> str:
    """Convert text into a URL-friendly slug."""
    import re
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text).strip('-')
    return text

def camel_to_snake(name: str) -> str:
    """Convert CamelCase to snake_case."""
    import re
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
