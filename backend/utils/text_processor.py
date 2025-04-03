import re
from nltk.tokenize import word_tokenize


def clean_text(text):
    """
    Clean and normalize text for processing

    Args:
        text (str): Text to clean

    Returns:
        str: Cleaned text
    """
    if not text:
        return ""

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    # Fix spacing around punctuation
    text = re.sub(r"\s+([.,;:!?)])", r"\1", text)
    text = re.sub(r"(\()\s+", r"\1", text)

    # Remove excessive punctuation
    text = re.sub(r"([.,!?]){2,}", r"\1", text)

    # Remove URL artifacts
    text = re.sub(r"https?://\S+", "", text)

    # Fix common spacing issues
    text = re.sub(r"\s+", " ", text)
    text = text.strip()

    return text


def count_words(text):
    """
    Count the number of words in text

    Args:
        text (str): Text to count words in

    Returns:
        int: Number of words
    """
    if not text:
        return 0

    # Tokenize text to get words
    words = word_tokenize(text)

    # Filter out punctuation and other non-word tokens
    words = [word for word in words if any(c.isalpha() for c in word)]

    return len(words)


def truncate_text(text, max_length, add_ellipsis=True):
    """
    Truncate text to max_length words

    Args:
        text (str): Text to truncate
        max_length (int): Maximum number of words
        add_ellipsis (bool): Whether to add ellipsis if truncated

    Returns:
        str: Truncated text
    """
    if not text:
        return ""

    words = text.split()

    if len(words) <= max_length:
        return text

    truncated = " ".join(words[:max_length])

    if add_ellipsis:
        truncated += "..."

    return truncated


def get_reading_time(text, wpm=200):
    """
    Calculate reading time in minutes

    Args:
        text (str): Text to calculate reading time for
        wpm (int): Words per minute reading speed

    Returns:
        float: Reading time in minutes
    """
    word_count = count_words(text)

    if word_count == 0:
        return 0

    reading_time = word_count / wpm

    return reading_time


def detect_language(text):
    """
    Detect the language of the text (simplified)
    This is just a basic placeholder - in a real app you would
    use a more sophisticated language detection library

    Args:
        text (str): Text to detect language for

    Returns:
        str: Detected language code
    """
    # Simple language detection based on common words
    # This is just a basic implementation
    english_common = ["the", "and", "is", "in", "to", "it", "of"]
    spanish_common = ["el", "la", "de", "en", "que", "y", "es"]
    french_common = ["le", "la", "de", "et", "en", "un", "une"]

    text_lower = text.lower()

    # Count occurrences of common words
    english_count = sum(
        1 for word in english_common if f" {word} " in f" {text_lower} "
    )
    spanish_count = sum(
        1 for word in spanish_common if f" {word} " in f" {text_lower} "
    )
    french_count = sum(1 for word in french_common if f" {word} " in f" {text_lower} ")

    # Determine language based on counts
    counts = {"en": english_count, "es": spanish_count, "fr": french_count}

    # Return the language with the highest count
    return max(counts, key=counts.get) if any(counts.values()) else "en"
