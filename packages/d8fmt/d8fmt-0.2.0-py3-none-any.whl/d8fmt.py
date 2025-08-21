"""
This module converts a canonical datetime example into a deterministic format string
based on standard `strftime`/`strptime` directives, while imposing strict rules
for tokens, literals, fractional seconds, and time zones.

Canonical Instant (Fixed):
  - `2004-10-31 13:12:11` is used as a reference to validate and transform formats.

Rules:
  - Only tokens present in the canonical instant are allowed for formatting.
  - Literals in the format strings are preserved as is.
  - Time zones are strictly validated:
  - Timezone abbreviations (e.g., PST, GMT) are explicitly prohibited.
  - Fractional seconds:
    - Always render fractional seconds with zero padding.
  - The output format uses cross-platform `strftime`/`strptime` directives.
  - Token replacement uses an ordered mapping to ensure correctness.

Functions:
  - `is_zone_free(fmt: str) -> bool`:
    Validates the absence of unsupported timezone formats, offsets, or abbreviations.

  - `snap_fmt(fmt: str) -> str`:
    Converts a format string using token replacement based on the canonical instant.
    Enforces all rules, validates timezones, and maps tokens into corresponding strftime directives.

Mapping Example:
  - `"2004"` → `"%Y"`:  Year (4-digit)
  - `"31"` → `"%d"`: Day of the month
  - `"October"` → `"%B"`: Full month name
  - `"13"` → `"%H"`: Hour (24-hour clock)
  - `PM` -> '%p' AM/PM marker
  - `".000000"` → `"%f"`: Microseconds
  - `"0"` → `"%w"`: Day of the week (Sunday = 0, Saturday = 6 non-ISO)
  - `"7"` → `"%u"`: Day of the week (ISO, Monday = 1, Sunday = 7)
  - `"AM/PM"` → `"%p"`: AM/PM marker

Error Handling:
  - Raises a `ValueError` if invalid timezone formats or abbreviations are detected.
"""

import datetime as dt
import re



CANONICAL: dt.datetime = dt.datetime(
    2004, 10, 31, 13, 12, 11,tzinfo=dt.timezone.utc
)

# Replacement mapping.  Note we take advantage of
# the diction being order so as we iterate over these items
# they are going in the order we specifiy
MACRO_LOOKUP_TABLE = {
    "HOUR12": "%I",
    "HOUR24": "%H",
    'DOY': "%j",
    "YEAR2": "%y",
    "YEAR4": "%Y",
    "MONTH": "%B",
    "MONTH3": "%b",
    "MONTH#": "%m",
    "DAY": "%A",
    "DAY3": "%a",
    "DAY#": "%d",
    "HOUR": "%I",
    "MINUTE": "%M",
    "SECOND": "%S",
    "MICROSEC": "%f",
    "AM": "%p",
    "PM": "%p",
    "WOY": "%U",
    "WOYISO": "%W",
    "WDAY#ISO": "%u",
    "WDAY#": "%w",
    "TZ": "%Z",
    "UTCOFF": "%z",
    "LOCALE":"%x",
}

DATETIME_LOOKUP_TABLE = {
    ".000000": ".%f",  # Microseconds (truncated example)
    "2004": "%Y",  # Year (4-digit)
    "305": "%j",  # Day of the year
    "October": "%B",  # Full month name
    "OCTOBER": "%B",  # Full month name
    "October": "%B",  # Full month name
    "october": "%B",  # Full month name
    "Oct": "%b",  # Abbreviated month name
    "OCT": "%b",  # Abbreviated month name
    "oct": "%b",  # Abbreviated month name
    "Sunday": "%A",  # Full weekday name
    "SUNDAY": "%A",  # Full weekday name
    "sunday": "%A",  # Full weekday name
    "SUN": "%a",  # Abbreviated weekday name
    "Sun": "%a",  # Abbreviated weekday name
    "sun": "%a",  # Abbreviated weekday name
    "01": "%I",  # Hour (12-hour clock)
    "04": "%y",  # Year (last 2 digits)
    "10": "%m",  # Month number
    "11": "%S",  # Seconds
    "12": "%M",  # Minute
    "13": "%H",  # Hour (24-hour clock)
    "31": "%d",  # Day of the month
    "44": "%U",  # Week of the year (starting with Sunday)
    "43": "%W",  # Week of the year (starting with Monday)
    "AM": "%p",  # AM/PM marker
    "PM": "%p",  # AM/PM marker
    "am": "%p",  # AM/PM marker
    "pm": "%p",  # AM/PM marker
    # ".000000": ".%f",  # Microseconds (truncated example)
    # ".00000": ".%f" , # Microseconds (truncated example)
    # ".0000": ".%f",  # Microseconds (truncated example)
    # ".000": ".%f",  # Microseconds (truncated example)
    # ".00": ".%f",  # Microseconds (truncated example)
    # ".0": ".%f",  # Microseconds (truncated example)

    # These will be problematic
    "0": "%w",  # 0th day of week ( 0-6)
    "7": "%u",  # 7th day of week (ISO 1-7)
}

def is_zone_free(fmt: str):
    """
    This is a placeholder. It will be replaced when timezones are supported.

    Throws exception if timezone formatting is detected.
    """
    # Regex to detect the pattern +/-dddd
    tz_offset_pattern = r" [+-]\d{4}"
    # List of invalid timezone strings
    invalid_timezones = ["PST", "EST", "CST", "MST", "AST", "HST", "AKST", "PDT", "EDT", "CDT", "MDT", "ADT", "HADT",
                         "AKDT","GMT"]

    # Check for +/-dddd offset
    if re.search(tz_offset_pattern, fmt):
        raise ValueError(f"Invalid format string: '{fmt}' contains unsupported +/-dddd patterns.")

    # Check for invalid timezone abbreviations
    for tz in invalid_timezones:
        if tz in fmt:
            raise ValueError(f"Invalid format string: '{fmt}' contains unsupported timezone abbreviation '{tz}'.")
    return True


def snap_fmt(fmt: str,
             macros: dict[str, str] | None = None,
             dt_replacements: [str, str] = None) -> str:
    """
    Formats a string by replacing placeholder macros with their corresponding values
    and applying additional datetime-based replacements.

    This function processes the input string `fmt` by performing a series of
    replacements:
      1. Replaces `{xxx}` macros using a provided or default mapping (`macros`).
      2. Applies further datetime-related replacements (`dt_replacements`) to
         format-specific placeholders.

    Args:
        fmt (str):
            The input format string containing placeholders to be replaced.
            Placeholders should match the keys in the mappings provided.

        macros (dict[str, str] | None, optional):
            A dictionary where keys represent macro placeholders (e.g., "{HOUR12}")
            and values represent their corresponding format tokens. If not provided,
            a default macro lookup table (`MACRO_LOOKUP_TABLE`) is used.

        dt_replacements ([str, str], optional):
            A dictionary of additional replacements for datetime format-specific
            placeholders (e.g., "%H", "%M"). If not provided, a default datetime
            lookup table (`DATETIME_LOOKUP_TABLE`) is used.

    Returns:
        str:
            The fully formatted string with all placeholder macros and datetime
            tokens replaced.

    Raises:
        ValueError: If the input string `fmt` contains invalid or unsupported
                    macros or formatting tokens not handled by the mappings.

    Examples:
        >>> snap_fmt("The time is {HOUR12}:{MINUTE} {AM}.",
                     macros={"HOUR12": "%I", "MINUTE": "%M", "AM": "%p"})
        'The time is %I:%M %p.'

        >>> snap_fmt("{YEAR4}-{MONTH#}-{DAY#}",
                     macros={"YEAR4": "%Y", "MONTH#": "%m", "DAY#": "%d"})
        '%Y-%m-%d'

        # With datetime replacements
        >>> snap_fmt("Today is {DAY}, {MONTH} {DAY#}, {YEAR4}.",
                     macros={"DAY": "%A", "MONTH": "%B", "DAY#": "%d", "YEAR4": "%Y"},
                     dt_replacements={"%A": "Monday", "%B": "October", "%d": "09", "%Y": "2023"})
        'Today is Monday, October 09, 2023.'

    Note:
        - The macro lookup table (`MACRO_LOOKUP_TABLE`) is expected to map keys like
          `"{HOUR12}"` to standard Python datetime format specifiers.
        - The order of operations ensures that all `{xxx}` macros are replaced first
          (via `format()` or manual replacement), followed by datetime token replacements.
    """

    macros = macros or MACRO_LOOKUP_TABLE
    dt_replacements = dt_replacements or DATETIME_LOOKUP_TABLE

    is_zone_free(fmt)

    # Use the .format to lookup {xxx} macros and replace them with format tokens.
    fmt = fmt.format(**macros)

    # These need to use the slow way
    for key, value in macros.items():
        fmt = fmt.replace(key, value)

    # Perform replacements using the mapping
    for key, value in dt_replacements.items():
        fmt = fmt.replace(key, value)

    return fmt


class datetime_snap(dt.datetime):
    def stezftime(self, fmt: str) -> str:
        """
        Format a datetime object into a custom string using an enhanced set of macros for
        datetime components.

        ### Key Features:
        - You can use **standard Python datetime format strings** (e.g., `%Y`, `%m`, `%d`).
        - Additional **macros** such as `{HOUR12}`, `{MONTH}`, `{DAY}` offer flexibility
          and leverage a user-friendly style.
        - You can mix arbitrary text with datetime parts to create custom formats, but
          avoid conflicts where text resembles the placeholders.

        **Examples:**
        Quickly create beautifully formatted datetime strings with intuitive macros:
        - `"Today is {DAY}, {MONTH} {DAY#}, {YEAR4} at {HOUR12}:{MINUTE}:{SECOND} {AM}."`
          → `Sunday, October 31, 2004 at 01:12:11 PM`

        - `"Date: {MONTH#}/{DAY#}/{YEAR4}, Time: {HOUR24}:{MINUTE}."`
          → `Date: 10/31/2004, Time: 13:12`

        - `"Day {DOY} of the year {YEAR4}, Week {WOY}."`
          → `Day 305 of the year 2004, Week 44`



        ### Example Placeholders and Mappings:
        Here are some basic example mappings supported by this method:
        - `{YEAR4}` → `2004`
        - `{MONTH#}` → `10`
        - `{DAY}` → `Sunday`
        - `{HOUR24}` → `13`
        - `{HOUR12}` → `01`
        - `{SECOND}` → `11`
        - `{MICROSEC}` → `000000`
        - `{DOY}` → `305` (Day of the year)
        - `{WOY}` → `44` (Week of the year starting Sunday)

        ### Examples:
        Use these format strings to generate desired outputs:
        - `"Today is {DAY}, {MONTH} {DAY#}, {YEAR4} at {HOUR12}:{MINUTE}:{SECOND} {AM}."`
          → `Sunday, October 31, 2004 at 01:12:11 PM`

        - `"Date: {MONTH#}/{DAY#}/{YEAR4}, Time: {HOUR24}:{MINUTE}."`
          → `10/31/2004, Time: 13:12.`

        - `"Day {DOY} of the year {YEAR4}, Week {WOY}."`
          → `Day 305 of the year 2004, Week 44.`

        - `"Custom: <{YEAR4}-{MONTH#}-{DAY#} @ {HOUR24}:{MINUTE}>"`
          → `<2004-10-31 @ 13:12>`

        ### Supported Common Placeholders:
        - `{YEAR4}`: Four-digit year (e.g., `2004`).
        - `{YEAR2}`: Two-digit year (e.g., `04`).
        - `{MONTH}`: Full month (e.g., `October`).
        - `{MONTH3}`: Abbreviated month (e.g., `Oct`).
        - `{MONTH#}`: Month as a two-digit number (e.g., `10`).
        - `{DAY}`: Full day of the week (e.g., `Sunday`).
        - `{DAY3}`: Abbreviated day of the week (e.g., `Sun`).
        - `{DAY#}`: Day of the month as a two-digit number (e.g., `31`).
        - `{HOUR24}`: Hour in 24-hour format (e.g., `13`).
        - `{HOUR12}`: Hour in 12-hour format (e.g., `01`).
        - `{MINUTE}`: Minutes (e.g., `12`).
        - `{SECOND}`: Seconds (e.g., `11`).
        - `{MICROSEC}`: Microseconds (e.g., `000000`).
        - `{DOY}`: Day of the year (1-365 or 1-366 for leap years).
        - `{WOY}`: Week of the year starting on Sunday.

        ### Note to Users:
        To avoid conflicts, use simple text that does not overlap with placeholders
        (e.g., `{HOUR12}` or `%Y`). If you need to embed a datetime string into a
        larger text block, it’s recommended to format your date string separately
        before combining it with additional text.

        Returns:
            str: A fully formatted string containing the requested datetime.

        Examples:
        ```python
        snap = datetime_snap(2004, 10, 31, 13, 12, 11)

        # Example with macros
        snap.stezftime("Today is {DAY}, {MONTH} {DAY#}, {YEAR4} at {HOUR12}:{MINUTE}:{SECOND} {AM}.")
        # Output: "Today is Sunday, October 31, 2004 at 01:12:11 PM."

        # Traditional datetime formatting (no macros)
        snap.stezftime("%A, %B %d, %Y %H:%M:%S")
        # Output: "Sunday, October 31, 2004 13:12:11."

        # Mixing macros and datetime tokens (Not that you should do this)
        snap.stezftime("{YEAR4}-{MONTH#}-{DAY#} %H:%M")
        # Output: "2004-10-31 13:12"
        ```
        """
        return self.strftime(snap_fmt(fmt))

