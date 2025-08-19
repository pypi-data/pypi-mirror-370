import random


def get_random_avatar(gender: str = "other") -> str:
    """
    Returns a random cartoon avatar URL based on gender.
    All avatars come from https://github.com/Ashwinvalento/cartoon-avatar

    Args:
        gender (str): "male", "female", or "other". Defaults to "other".

    Returns:
        str: The URL of the random avatar image.
    """
    rand_num = random.randint(1, 114)
    mf = ["male", "female"]
    if gender == "male":
        gender_picture = "male"
    elif gender == "female":
        gender_picture = "female"
    else:
        gender_picture = random.choice(mf)
    return f"https://raw.githubusercontent.com/Ashwinvalento/cartoon-avatar/master/lib/images/{gender_picture}/{rand_num}.png"
