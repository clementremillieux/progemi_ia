"""Utils for the app"""

import tiktoken


def token_counter(text: str) -> int:
    """Count the nb of token in a text"""

    encoding = tiktoken.get_encoding("cl100k_base")

    nb_token: int = len(encoding.encode(text))

    return nb_token


def reduce_until_token(text: str, max_token: int) -> str:
    """Cut text to match max_token size"""

    nb_token = token_counter(text=text)

    while nb_token > int(max_token - 10):
        pourcentage = 0.80

        new_limit = int(len(text) * pourcentage)

        text = text[:new_limit]

        nb_token = token_counter(text=text)

    return text
