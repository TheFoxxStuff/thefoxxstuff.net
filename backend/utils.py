"""Shared utility functions"""
import re


# Cyrillic to Latin transliteration map
CYRILLIC_MAP = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
    'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
    'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
    'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
    'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
}


def transliterate(text: str) -> str:
    """Transliterate Cyrillic characters to Latin"""
    result = []
    for char in text:
        result.append(CYRILLIC_MAP.get(char, char))
    return ''.join(result)


def generate_slug(title: str) -> str:
    """
    Generate URL-friendly slug from title with Cyrillic support.

    Examples:
        "Hello World" -> "hello-world"
        "Привет Мир" -> "privet-mir"
        "Test 123!" -> "test-123"
    """
    # First transliterate Cyrillic to Latin
    slug = transliterate(title)

    # Convert to lowercase and strip
    slug = slug.lower().strip()

    # Remove non-alphanumeric characters except spaces and hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)

    # Replace spaces and underscores with hyphens
    slug = re.sub(r'[\s_]+', '-', slug)

    # Remove duplicate hyphens
    slug = re.sub(r'-+', '-', slug)

    # Strip leading/trailing hyphens
    return slug.strip('-')


def slugify_filename(text: str) -> str:
    """
    Convert text to filename-friendly slug (uses underscores instead of hyphens).
    Used for file uploads to maintain consistency.
    """
    # Transliterate Cyrillic
    text = transliterate(text)

    # Convert to lowercase and strip
    text = text.lower().strip()

    # Remove non-alphanumeric characters except spaces, underscores and hyphens
    text = re.sub(r'[^\w\s-]', '', text)

    # Replace whitespace with underscores
    text = re.sub(r'[\s]+', '_', text)

    # Remove duplicate underscores
    text = re.sub(r'_+', '_', text)

    return text.strip('_')
