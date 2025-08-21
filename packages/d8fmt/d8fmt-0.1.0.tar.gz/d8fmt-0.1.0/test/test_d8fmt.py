import datetime
import locale

import pytest
from src.d8fmt import snap_fmt,CANONICAL,is_zone_free,datetime_snap


@pytest.mark.parametrize("input_format, expected_output", [

    # Day of Year
    ("305", "%j"),  # Day of the year (October 31 is the 304th day of 2004)

    # Year and month
    ("2004", "%Y"),  # Year
    ("10", "%m"),  # Month number
    ("October", "%B"),  # Full month name
    ("Oct", "%b"),  # Abbreviated month name

    # Day
    ("31", "%d"),  # Day of the month
    ("Sunday", "%A"),  # Full weekday name
    ("Sun", "%a"),  # Abbreviated weekday name

    # Time (hour, minute, second)
    ("13", "%H"),  # 24-hour format hour
    ("01", "%I"),  # 12-hour format hour
    ("12", "%M"),  # Minutes
    ("11", "%S"),  # Seconds
    ("PM", "%p"),  # AM/PM marker

    # Microseconds
    (".000000", ".%f"),  # Fractional seconds

    # Week numbers
    ("43", "%W"),  # Week of year (starting with Sunday)
    ("44", "%U"),  # Week of year (starting with Monday)
])
def test_snap_fmt(input_format, expected_output):
    actual_output = snap_fmt(input_format)
    assert actual_output == expected_output

    # Round-trip: format the CANONICAL date using the resulting format
    formatted_date = CANONICAL.strftime(actual_output)
    assert formatted_date == input_format

@pytest.mark.parametrize("input_format, expected_format", [

    # Week-based formats
    ("2004-W43-0", "%Y-W%W-%w"),  # ISO week-based format (Start Sunday 0-6 )
    ("2004-W44-7", "%Y-W%U-%u"),  # ISO week-based format (Start Monday 1-7 )

    # US-style date formats
    ("10-31-2004 13:12:11", "%m-%d-%Y %H:%M:%S"),  # Month-Day-Year + 24-hour time
    ("10/31/2004 01:12:11 PM", "%m/%d/%Y %I:%M:%S %p"),  # Month/Day/Year + 12-hour time with AM/PM

    # ISO-8601 full date and time
    ("2004-10-31 13:12:11", "%Y-%m-%d %H:%M:%S"),
    ("2004-10-31T13:12:11", "%Y-%m-%dT%H:%M:%S"),  # ISO format with 'T' separator

    # European-style date formats
    ("31/10/2004 13:12:11", "%d/%m/%Y %H:%M:%S"),  # Day/Month/Year + 24-hour time
    ("31-10-2004 01:12:11 PM", "%d-%m-%Y %I:%M:%S %p"),  # Day-Month-Year + 12-hour time with AM/PM

    # Long-form formats
    ("Sunday, October 31, 2004 13:12:11", "%A, %B %d, %Y %H:%M:%S"),  # Full weekday and month names
    ("Sun, Oct 31, 2004 01:12:11 PM", "%a, %b %d, %Y %I:%M:%S %p"),  # Abbreviated weekday and month names

    # Date only
    ("2004-10-31", "%Y-%m-%d"),  # Standard ISO-8601 date
    ("31/10/2004", "%d/%m/%Y"),  # European-style date

    # Time only
    ("13:12:11", "%H:%M:%S"),  # 24-hour time
    ("01:12:11 PM", "%I:%M:%S %p"),  # 12-hour time with AM/PM

])
def test_snap_fmt_full_dates(input_format, expected_format):
    actual_format = snap_fmt(input_format)
    formatted_date = CANONICAL.strftime(actual_format)

    assert actual_format == expected_format

    # Round-trip: format the CANONICAL date using the resulting format
    assert formatted_date == input_format


# List of test cases with invalid date strings
@pytest.mark.parametrize("invalid_date_string", [
    # Cases where the timezone doesn't start with " +" or " -"
    "2004-10-31T13:12:11 +0530",  # Missing leading space before timezone
    "2004-10-31T13:12:11 -0800",  # Missing leading space before timezone

    # Cases with invalid timezone abbreviations
    "2004-10-31T13:12:11 PST",  # Unsupported abbreviation (PST)
    "2004-10-31T13:12:11 EST",  # Unsupported abbreviation (EST)
    "2004-10-31T13:12:11 CDT",  # Unsupported abbreviation (CDT)
    "2004-10-31T13:12:11 GMT",  # Unsupported abbreviation (GMT)

    # Cases with both invalid patterns and abbreviations
    "2004-10-31T13:12:11 -0530",  # No "+" or "-" for timezone offset
    "2004-10-31T13:12:11 +PDT",  # Leading space but invalid timezone abbreviation (PDT)
])
def test_is_zone_free_invalid_cases(invalid_date_string):
    with pytest.raises(ValueError):
        is_zone_free(invalid_date_string)  # Function to validate format

@pytest.mark.parametrize("canonical, template", [
    # Basic full date formats
    ("2004-10-31", "{YEAR4}-{MONTH#}-{DAY#}"),  # Basic ISO full date
    ("31-10-2004", "{DAY#}-{MONTH#}-{YEAR4}"),  # European-style date
    ("10/31/2004", "{MONTH#}/{DAY#}/{YEAR4}"),  # US-style date

    # Date with full and short names
    ("31 October 2004", "{DAY#} {MONTH} {YEAR4}"),  # Full month name
    ("Oct 31, 2004", "{MONTH3} {DAY#}, {YEAR4}"),  # Abbreviated month with comma
    ("Sunday, October 31, 2004", "{DAY}, {MONTH} {DAY#}, {YEAR4}"),  # Full weekday + full month
    ("Sun, Oct 31, 2004", "{DAY3}, {MONTH3} {DAY#}, {YEAR4}"),  # Abbreviated weekday + month

    # Time formats (24-hour and 12-hour)
    ("13:12:11", "{HOUR24}:{MINUTE}:{SECOND}"),  # 24-hour time
    ("01:12:11 PM", "{HOUR12}:{MINUTE}:{SECOND} {PM}"),  # 12-hour time with PM

    # Combined date and time formats
    ("2004-10-31 13:12:11", "{YEAR4}-{MONTH#}-{DAY#} {HOUR24}:{MINUTE}:{SECOND}"),  # ISO 8601 with 24-hour time
    ("10/31/2004 01:12:11 PM", "{MONTH#}/{DAY#}/{YEAR4} {HOUR12}:{MINUTE}:{SECOND} {PM}"),  # US format with 12-hour time
    ("31-10-2004 13:12", "{DAY#}-{MONTH#}-{YEAR4} {HOUR24}:{MINUTE}"),  # European date with truncated time
    ("31 October 2004 01:12 PM", "{DAY#} {MONTH} {YEAR4} {HOUR12}:{MINUTE} {PM}"),  # Full month with 12-hour time

    # Date and time with alternate separators
    ("2004.10.31 13:12:11", "{YEAR4}.{MONTH#}.{DAY#} {HOUR24}:{MINUTE}:{SECOND}"),  # Dot-separated date
    ("10-31-2004 01:12 PM", "{MONTH#}-{DAY#}-{YEAR4} {HOUR12}:{MINUTE} {PM}"),  # US date with dashes and 12-hour time
    ("2004/10/31/13/12", "{YEAR4}/{MONTH#}/{DAY#}/{HOUR24}/{MINUTE}"),  # Mixed slash format

    # Day of the year and week formats
    ("305", "{DOY}"),  # Day of the year for Oct 31
    ("44", "{WOY}"),  # Week of year (Sunday-start)
    ("43", "{WOYISO}"),  # Week of year (ISO, Monday-start)
    ("0", "{WDAY#}"),  # Day of the week (Sunday-based, Oct 31 is a Sunday)
    ("7", "{WDAY#ISO}"),  # Day of the week (ISO standard, Monday-based, Oct 31 is Sunday=7)

    # ISO-specific datetime formats
    ("2004-10-31T13:12:11", "{YEAR4}-{MONTH#}-{DAY#}T{HOUR24}:{MINUTE}:{SECOND}"),  # ISO 8601 datetime
    ("2004-10-31T01:12:11 PM", "{YEAR4}-{MONTH#}-{DAY#}T{HOUR12}:{MINUTE}:{SECOND} {PM}"),  # ISO with 12-hour time

    # Truncated and partial formats
    ("2004-10", "{YEAR4}-{MONTH#}"),  # Month and year only
    ("2004", "{YEAR4}"),  # Year only
    ("13:12", "{HOUR24}:{MINUTE}"),  # Time without seconds
    ("01:12 PM", "{HOUR12}:{MINUTE} {PM}"),  # Time without seconds in 12-hour format
    ("Sunday, 31 October", "{DAY}, {DAY#} {MONTH}"),  # Weekday with day and month

    # Various delimited and international formats
    ("2004/10/31", "{YEAR4}/{MONTH#}/{DAY#}"),  # Slash-separated
    ("2004-31-10", "{YEAR4}-{DAY#}-{MONTH#}"),  # Non-standard order
    ("31-Oct-2004", "{DAY#}-{MONTH3}-{YEAR4}"),  # European format with abbreviated month
    ("2004.October/31", "{YEAR4}.{MONTH}/{DAY#}"),  # Mixed format using dot and slash
    ("31/Oct/2004", "{DAY#}/{MONTH3}/{YEAR4}"),  # Day/Month/Year slash format
    ("31-October-2004", "{DAY#}-{MONTH}-{YEAR4}"),  # Non-English month name (e.g., German format)

    # Just time formats
    ("13:12:11.000000", "{HOUR24}:{MINUTE}:{SECOND}.{MICROSEC}"),  # 24-hour
    ("13:12:11", "{HOUR24}:{MINUTE}:{SECOND}"),  # 24-hour
    ("01:12 PM", "{HOUR12}:{MINUTE} {PM}"),  # 12-hour without seconds
    ("13:12", "{HOUR24}:{MINUTE}"),  # 24-hour without seconds
    ("01:12:11 PM", "{HOUR12}:{MINUTE}:{SECOND} {PM}"),  # 12-hour with seconds

    # Escaped text (constant strings)
    ("Today is Sunday", "Today is {DAY}"),  # Text with replacement
    ("Year: 2004", "Year: {YEAR4}"),  # Text with constant string
    ("Time: 13:12:11", "Time: {HOUR24}:{MINUTE}:{SECOND}"),  # Prefix with text
    ("It's 01:12 PM!", "It's {HOUR12}:{MINUTE} {PM}!"),  # Suffix with text
    ("12:11 on October 31", "{MINUTE}:{SECOND} on {MONTH} {DAY#}"),  # Mixed text and replacements

    # Abbreviated/flexible cases
    ("04", "{YEAR2}"),  # Two-digit year
    ("13-12", "{HOUR24}-{MINUTE}"),  # Hour and minute
    ("Oct. 31, 2004", "{MONTH3}. {DAY#}, {YEAR4}"),  # Abbreviated month with period
    ("October-31st", "{MONTH}-{DAY#}st"),  # Month with ordinal suffix (hardcoded)
    ("31/10/04", "{DAY#}/{MONTH#}/{YEAR2}"),  # European style with two-digit year
    ("10/31/04", "{MONTH#}/{DAY#}/{YEAR2}"),  # US style with two-digit year
]
)
def test_macro_replacements_equivalence(canonical, template):
    # Apply the transformation for both canonical and template formats
    fmt_canonical = snap_fmt(canonical)
    fmt_template = snap_fmt(template)
    # Assert that they produce the same result
    assert fmt_canonical == fmt_template, (
        f"Expected canonical '{canonical}' and template '{template}' "
        f"to produce the same format, but got '{fmt_canonical}' and '{fmt_template}'"
    )

# Fixture to set and restore locale
@pytest.fixture
def set_locale():
    # Store the current locale
    original_locale = locale.setlocale(locale.LC_TIME)

    # Define the new locale you want to set for the test
    new_locale = "en_US.UTF-8"  # Example: US English

    try:
        # Set the desired locale
        locale.setlocale(locale.LC_TIME, new_locale)
        yield  # Test executes here
    finally:
        # Restore the original locale after the test
        locale.setlocale(locale.LC_TIME, original_locale)


# Example test using the fixture
def test_locale_date_format(set_locale):
    date1 = CANONICAL.strftime("%x")
    date2 =CANONICAL.strftime(snap_fmt("{LOCALE}"))

    # %x should use the US locale format (MM/DD/YYYY)
    assert date1 == "10/31/2004"
    assert date1 == date2


@pytest.mark.parametrize(
    "format_string, expected_output",
    [
        ("{YEAR4}-{MONTH#}-{DAY#}", "2004-10-31"),  # Basic year-month-day format
        ("{MONTH#}/{DAY#}/{YEAR2} at {HOUR24}:{MINUTE}:{SECOND}", "10/31/04 at 13:12:00"),  # Month/Day/Year
        ("{DAY}, {MONTH} {DAY#}, {YEAR4} {HOUR12}:{MINUTE}:{SECOND} {PM}","Sunday, October 31, 2004 01:12:00 PM",
        ),  # Full verbose date
        ("Canonical datetime", "Canonical datetime"),  # Edge case with raw text
    ],
)
def test_datetime_snap_formatting(format_string, expected_output):
    # Create a `datetime_snap` object for the canonical datetime
    d = datetime_snap(year=2004, month=10, day=31, hour=13, minute=12, second=0)
    formatted_date = d.stezftime(format_string)
    # Apply the custom stezftime method and verify the output
    assert formatted_date == expected_output
