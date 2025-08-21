from typing import Optional

from pydantic import BaseModel, field_validator


def extract_twitter_username(twitter_link):
    """
    Extracts the Twitter username from a given input, which can be a URL or just the username itself.

    Args:
        twitter_link (str): The input containing a Twitter URL or just the username.

    Returns:
        str or None: The extracted Twitter username if found, otherwise None.
    """

    start_index = None
    is_valid_url = False
    is_url = False

    if twitter_link.startswith("https://") or twitter_link.startswith("http://"):
        is_url = True
    # Strip off "https://" or "http://" if present
    twitter_link = twitter_link.replace("https://", "").replace("http://", "")

    if "twitter.com" in twitter_link:
        if any(sub in twitter_link for sub in ["/i/", "/status/", "/search?", "/intent/"]):
            return twitter_link.split("twitter.com/")[-1]

        # Find the start index of the username
        is_valid_url = False
        str_find = twitter_link.find("twitter.com/")
        if str_find != -1:
            start_index = str_find + len("twitter.com/")

    elif "x.com" in twitter_link:
        if any(sub in twitter_link for sub in ["/i/", "/status/", "/search?", "/intent/"]):
            return twitter_link.split("x.com/")[-1]

        # Find the start index of the username
        is_valid_url = False
        str_find = twitter_link.find("x.com/")
        if str_find != -1:
            start_index = str_find + len("x.com/")

    if start_index :
        # Extract the substring containing the username
        username = twitter_link[start_index:].split("/")[0].split("?")[0]
    else:
        if not is_valid_url and is_url:
            return None
        else:
            username = twitter_link.split("/")[0].split("?")[0]

    return username if username else None


def extract_telegram_channel_name(telegram_link):
    """
    Extracts the Telegram username from a given input, which can be a URL or just the username itself.

    Args:
        telegram_link (str): The input containing a telegram URL or just the username.

    Returns:
        str or None: The extracted telegram username if found, otherwise None.
    """

    start_index = None
    valid_url = False
    is_url = False
    if telegram_link.startswith("https://") or telegram_link.startswith("http://"):
        is_url = True

    # Strip off "https://" or "http://" if present
    telegram_link = telegram_link.replace("https://", "").replace("http://", "")

    if "t.me" in telegram_link:
        valid_url = True
        # Find the start index of the username
        str_find = telegram_link.find("t.me/")
        if str_find != -1:
            start_index = str_find + len("t.me/")
    elif "telegram.me" in telegram_link:
        valid_url = True
        # Find the start index of the username
        str_find = telegram_link.find("telegram.me/")
        if str_find != -1:
            start_index = str_find + len("telegram.me/")

    if start_index:
        # Extract the substring containing the username
        username = telegram_link[start_index:].split("/")[0].split("?")[0]
    else:
        if not valid_url and is_url:
            return None
        else:
            username = telegram_link.split("/")[0].split("?")[0]

    return username if username else None


class AuthorHandleModel(BaseModel):
    author_handle: Optional[str]

    @field_validator("author_handle", mode="before")
    def validate_author_handle(cls, value):
        if not value or len(value) > 16:
            raise ValueError("not a valid author_handle")
        return value


def is_valid_author_handle(author_handle):
    try:
        AuthorHandleModel(author_handle=author_handle)
        return True
    except ValueError:
        pass
