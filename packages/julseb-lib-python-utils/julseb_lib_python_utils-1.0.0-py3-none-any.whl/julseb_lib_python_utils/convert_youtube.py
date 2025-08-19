def convert_youtube(url: str) -> str:
    """
    Converts a standard YouTube video URL to its embeddable format.

    Args:
        url (str): The original YouTube video URL (e.g., "https://www.youtube.com/watch?v=VIDEO_ID").

    Returns:
        str: The YouTube URL in embed format (e.g., "https://www.youtube.com/embed/VIDEO_ID").

    Example:
        >>> convert_youtube("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        'https://www.youtube.com/embed/dQw4w9WgXcQ'
    """
    return url.replace("watch?v=", "embed/")
