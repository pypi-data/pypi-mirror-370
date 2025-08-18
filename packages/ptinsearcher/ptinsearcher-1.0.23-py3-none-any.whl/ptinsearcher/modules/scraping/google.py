"""
This module provides a utility to extract Google-related identifiers from HTTP responses.

Supported identifiers include:
- Google Tag Manager ID (GTM-XXXXXX)
- Google Analytics Universal ID (UA-XXXXX-Y)
- Google Analytics 4 ID (G-XXXXXXXX)
- Google Ads Conversion ID (AW-XXXXXXXXX)
- Google Campaign Manager ID (DC-XXXXXX)
- Google AdSense Publisher ID (ca-pub-XXXXXXXXXXXXXXXX)
- Google API Keys (AIza...)

Intended for use in auditing or recon tools to collect telemetry or tracking IDs embedded in webpages.
"""

import re
from requests import Response
from ptlibs import ptprinthelper


def parse_google_identifiers(response: Response) -> None:
    """
    Parses an HTTP response for various Google-related tracking or service identifiers.

    Args:
        response (Response): The HTTP response object from the `requests` library.

    Scans the response body for the following patterns:
        - GTM (Google Tag Manager)
        - UA (Universal Analytics)
        - G- (Google Analytics 4)
        - AW- (Google Ads conversion ID)
        - DC- (Campaign Manager ID)
        - ca-pub / ca-ads (AdSense publisher ID)
        - API keys starting with "AIza"

    If found, prints the identifiers grouped by type.
    Relies on the `ptprinthelper.ptprint` function and `self.args.json` flag for conditional output.
    """

    #ptprinthelper.ptprint(f"Google identifiers", "TITLE", condition=not self.args.json, colortext=True, newline_above=True)

    regulars = {
        "Google Tag Manager ID": r"(GTM-[A-Z0-9]{6,9})",
        "Google Analytics Universal ID": r"(UA-\d{4,10}-\d+)",
        "Google Analytics 4": r"(G-[A-Z0-9]{8,12})",
        "Google Ads Conversion ID": r"(AW-\d{9,12})",
        "Google Campaign Manager ID": r"(DC-\d{6,10})",
        "Google AdSense Publisher ID" : r"(ca-pub-\d{16})|(ca-ads-\d{16})",
        "Google API Keys": r"AIza[0-9A-z_\-\\]{35}",
    }

    found_identifiers = {}
    for key, regex in regulars.items():
        matches = re.findall(regex, response.text)
        matches = [m[0] if isinstance(m, tuple) else m for m in matches]
        matches = sorted(set(matches))
        if matches:
            found_identifiers[key] = matches

    return found_identifiers