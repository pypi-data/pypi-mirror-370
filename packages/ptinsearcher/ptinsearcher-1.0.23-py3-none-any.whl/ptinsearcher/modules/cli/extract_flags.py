from collections.abc import Callable

def parse_extract_flags(args, extract_str: str, on_error: Callable[[str], None]) -> dict:
    """
    Parses a short extract string (e.g., "ESCF") and returns a dictionary
    indicating which extraction types are enabled.

    Args:
        extract_str (str): String containing one or more valid extract type characters.
        on_error (Callable[[str], None]): Function to call on error with the
            error message as argument. Must be provided.

    Returns:
        dict: Dictionary with extraction type keys and `True` or `None` as values.
    """

    allowed_letters = {
        "E": "emails",
        "S": "subdomains",
        "C": "comments",
        "F": "forms",
        "U": "internal_urls",
        "X": "external_urls",
        "P": "phone_numbers",
        "M": "metadata",
        "N": "insecure_sources",
        "I": "ip_addresses",
        "Q": "internal_urls_with_parameters",
        "K": "google_keys",
        "A": "all"
    }

    extract_types = {value: None for value in allowed_letters.values()}
    extract_str = extract_str.upper()

    invalid = set([c for c in extract_str if c not in allowed_letters])
    if invalid:
        msg = (
            f"Invalid parameter(s) '{''.join(invalid)}' in --extract argument.\n"
            f"Allowed characters:\n" +
            "\n".join([f"  {k} - {v}" for k, v in allowed_letters.items()])
        )
        on_error(msg)
        return extract_types  # or raise, pokud chceš proces ukončit v on_error

    if "A" in extract_str:
        for key in extract_types:
            extract_types[key] = True
    else:
        for char in extract_str:
            key = allowed_letters[char]
            extract_types[key] = True

    extract_types["regex_search"] = None
    if args.search is not None:
        extract_types["regex_search"] = True

    return extract_types
