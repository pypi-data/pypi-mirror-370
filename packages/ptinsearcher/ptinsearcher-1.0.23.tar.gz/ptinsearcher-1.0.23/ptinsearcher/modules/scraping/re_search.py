# search_parser.py

import re
from requests import Response

def parse_search_regex(response: Response, search_regex: str) -> list[str]:
    """
    Searches the HTTP response using exactly the regex provided in `search_regex`.

    Args:
        response (Response): The HTTP response object from `requests`.
        search_regex (str): Regex pattern from args.search.

    Returns:
        list[str]: A list of unique matches found.
    """
    try:
        pattern = re.compile(search_regex)
    except re.error as e:
        raise ValueError(f"Invalid regex: {e}") from e

    matches = pattern.findall(response.text)

    # if the regex contains groups → tuples → flatten
    cleaned_matches = []
    for m in matches:
        if isinstance(m, tuple):
            cleaned_matches.extend([x for x in m if x])
        else:
            cleaned_matches.append(m)

    return sorted(set(cleaned_matches))
