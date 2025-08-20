import re
from enum import Enum
from typing import Optional, Union, Callable, Tuple, Iterable


def _only_digits(s: str) -> str:
    return re.sub(r"\D", "", s)


def _normalize_raw_input(phone: Union[str, int, float]) -> str:
    """
    Normalize raw input to just digits, preserving leading zeros for strings.
    Reject floats because they lose leading zeros and can be formatted (e.g., 1e10).
    """
    if isinstance(phone, float):
        # Floats are unsafe for phone numbers; caller should pass string or int
        raise ValueError("Phone numbers as float are ambiguous; pass a string or int.")
    if isinstance(phone, int):
        # int loses leading zeros by definition, but this matches your original behavior
        return str(phone)
    if not isinstance(phone, str):
        raise TypeError("phone_number must be str|int")

    phone = phone.strip()
    # Allow leading '+' or '00' international format; we'll strip them before digit normalization
    if phone.startswith("+"):
        phone = phone[1:]
    elif phone.startswith("00"):
        phone = phone[2:]
    return _only_digits(phone)


class CountryCode(Enum):
    """
    Supported countries with:
      - dial_code: country calling code
      - nsn_length: expected National Significant Number length (no country code)
      - formatter: formats the national number
      - trunk_prefix: '0' for countries that commonly include a trunk code domestically (strip if present)
    """

    USA   = ("1",  10, lambda n: f"({n[:3]}) {n[3:6]}-{n[6:]}",  "")
    UK    = ("44", 10, lambda n: f"{n[:2]} {n[2:6]} {n[6:]}",   "0")
    FRANCE= ("33", 9,  lambda n: f"{n[:1]} {n[1:3]} {n[3:5]} {n[5:]}", "0")
    SPAIN = ("34", 9,  lambda n: f"{n[:2]} {n[2:5]} {n[5:]}",   "")
    # Default to Costa Rica in your original code
    DEFAULT = ("506", 8, lambda n: f"{n[:4]}-{n[4:]}", "")

    def __init__(self, dial_code: str, nsn_length: int, formatter: Callable[[str], str], trunk_prefix: str):
        self.dial_code = dial_code
        self.nsn_length = nsn_length
        self.formatter = formatter
        self.trunk_prefix = trunk_prefix

    def validate_length(self, nsn: str) -> bool:
        return len(nsn) == self.nsn_length

    def strip_trunk(self, nsn: str) -> str:
        if self.trunk_prefix and nsn.startswith(self.trunk_prefix) and len(nsn) > self.nsn_length:
            # If someone passed trunk + nsn (e.g., '0' + 10 digits for UK),
            # remove only a single leading trunk.
            return nsn[1:]
        return nsn

    def format_number(self, nsn: str) -> str:
        return self.formatter(nsn)


class PhoneNumberFormatter:
    """
    Validate and format a phone number into E.164-like string with country-specific formatting of the NSN.
    Keeps backward compatibility with your previous API.
    """

    def __init__(self, default_country_code: CountryCode = CountryCode.DEFAULT):
        self.default_country_code = default_country_code

    def format_phone_number(self, phone_number: Union[str, int, float]) -> Optional[str]:
        """
        Returns: "+<country_code> <pretty national format>" or None if invalid.
        """
        try:
            digits = _normalize_raw_input(phone_number)
        except (TypeError, ValueError):
            return None

        if not digits or len(digits) < 7:  # minimal sanity check
            return None

        country, nsn = self._detect_country_code(digits)

        # Strip a single trunk prefix if present (e.g., UK/FR leading '0' before the NSN)
        nsn = country.strip_trunk(nsn)

        if not country.validate_length(nsn):
            return None

        pretty = country.format_number(nsn)
        return f"+{country.dial_code} {pretty}"

    def _detect_country_code(self, digits: str) -> Tuple[CountryCode, str]:
        """
        Detect the country by trying the longest dial codes first to avoid prefix collisions.
        Falls back to default if none matches.
        """
        # Iterate members excluding DEFAULT for detection, sorted by dial_code length desc
        candidates: Iterable[CountryCode] = (
            c for c in sorted(
                (m for m in CountryCode if m is not CountryCode.DEFAULT),
                key=lambda m: len(m.dial_code),
                reverse=True,
            )
        )

        for country in candidates:
            if digits.startswith(country.dial_code):
                return country, digits[len(country.dial_code):]

        # No match → assume default country; entire string is NSN
        return self.default_country_code, digits