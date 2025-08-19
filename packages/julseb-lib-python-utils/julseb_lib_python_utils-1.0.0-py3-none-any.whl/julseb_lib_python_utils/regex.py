import re

# Password regex: at least one digit, one lowercase, one uppercase, and at least 6 characters
password_regex = re.compile(r"(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{6,}")
"""
Compiled regex pattern to validate passwords with at least one digit, one lowercase, one uppercase, and at least 6 characters.
"""

# Email regex: matches most valid email addresses
email_regex = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$")
"""
Compiled regex pattern to validate most email addresses.
"""
