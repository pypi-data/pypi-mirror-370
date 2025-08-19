from julseb_lib_python_utils.slugify import slugify


def convert_to_email(name: str, domain: str = "email.com") -> str:
    """
    Converts a name to an email address using slugify logic, replacing dashes and spaces with dots.
    """
    slug = slugify(name)
    email = slug.replace("-", ".").replace(" ", ".")
    return f"{email}@{domain}"
