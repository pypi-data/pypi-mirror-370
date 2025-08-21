# Format By Example for Datetime

A Python module designed to transform canonical datetime examples into deterministic and 
platform-independent format strings using `strftime`/`strptime` directives. 
Human readable "cannonical" dates, or human readable varaible substituions may be used
to create format strings that are better than the cryptic formats that look like
`%b. %d %Y %I-%M-%S %p`.

In order to make the format strings (mostly) readable I chose to pick a date-time that
has no ambiguity in any fields required by a datetime object.

The canonical date is:

```2004/10/31 13:12:11.000``` 

This datetime has unique values for all numeric quantities as shown in the table below. Because
they are all unique the values in the Canonical column may be used to build a format string,
or the {MACRO} versions in the Macro column.  This mapping allows you to make date format
strings that are readable.  Obviously it when you get to the day of year, day# of week things
get a little cryptic, but both forms are much easier to read than the standard names.


| **Canonical** | **Macro**    | **Description**                                  | **Format ID** |
|---------------|--------------|--------------------------------------------------|---------------|
| `01`          | `{HOUR12}`     | Hour in 12-hour clock (zero-padded)              | `%I`          |
| `13`          | `{HOUR24}`     | Hour in 24-hour clock (zero-padded)              | `%H`          |
| `305`         | `{DOY}`      | Day of the year (1–366, zero-padded)             | `%j`          |
| `04`          | `{YEAR2}`    | Year without century (last two digits)           | `%y`          |
| `2004`        | `{YEAR4}`    | Year with century                                | `%Y`          |
| `October`     | `{MONTH}`    | Full month name                                  | `%B`          |
| `Oct`         | `{MONTH3}`   | Abbreviated month name                           | `%b`          |
| `10`          | `{MONTH#}`   | Month as a number (zero-padded, 01–12)           | `%m`          |
| `Sunday`      | `{DAY}`      | Full weekday name                                | `%A`          |
| `Sun`         | `{DAY3}`     | Abbreviated weekday name                         | `%a`          |
| `31`          | `{DAY#}`     | Day of the month (zero-padded)                   | `%d`          |
| `12`          | `{MINUTE}`   | Minute (zero-padded)                             | `%M`          |
| `11`          | `{SECOND}`   | Second (zero-padded)                             | `%S`          |
| `.000000`     | `{MICROSEC}` | Microsecond (zero-padded, 6 digits)              | `%f`          |
| `AM`          | `{AM}`       | AM/PM marker                                     | `%p`          |
| `PM`          | `{PM}`       | AM/PM marker                                     | `%p`          |
| `44`          | `{WOY}`      | Week of the year (Sunday as first day)           | `%U`          |
| `43`          | `{WOYISO}`   | ISO week number of the year (Mon as first day)   | `%W`          |
| `7`           | `{WDAY#ISO}` | Day of the week (ISO, Monday=1 to Sunday=7)      | `%u`          |
| `0`           | `{WDAY#}`    | Day of the week (Sunday-based, 0=Sun to 6=Sat) | `%w`          |
| _N/A_         | `{TZ}`       | Timezone abbreviation                            | `%Z`          |
| _N/A_         | `{UTCOFF}`   | UTC offset in the form ±HHMM                     | `%z`          |

Here are some examples of converting these format strings into datetime ready format strings.

```shell
>>> d8fmt.snap_fmt("2004-10-31")
'%Y-%m-%d'
>>> d8fmt.snap_fmt("2004-10-31 13-12-11")
'%Y-%m-%d %H-%M-%S'
>>>d8fmt.snap_fmt("Oct. 31 2004 01-12-11 PM")
'%b. %d %Y %I-%M-%S %p'
>>d8fmt.snap_fmt("{YEAR4}-{MONTH#}-{DAY#}T{HOUR24}:{MINUTE}:{SECOND}")
'%Y-%m-%dT%H:%M:%S'
>>d8fmt.snap_fmt("{YEAR4}-{MONTH#}-{DAY#}T{HOUR24}:{MINUTE}:{SECOND}.{MICROSEC}")
'%Y-%m-%dT%H:%M:%S.%f'
```


Note: `d8fmt` does NOT support timezones or offsets as those seem to already only sort of work.
Note: `d8fmt` does NOT (yet) extend the `strftime` functionality even though there are many opportunities.
---

## Features

- **Token Conversion**: Converts canonical components (e.g., `2004`, `31`, `October`) into matching `strftime` directives (e.g., `%Y`, `%d`, `%B`).
- **Time Zone Validation**:
  - Prohibits timezone abbreviations (e.g., `PST`, `GMT`).
  - Enforces offsets like `+/-dddd` to have a leading space.
- **Fractional Seconds Support**: Encodes fractional seconds via `%<N>f`, where `N` determines the number of zeros in the example.
- **Error Handling**: Raises a `ValueError` for unsupported formats or invalid tokens.
- **Round-Trip Validation**: Ensures that transformed formats can accurately round-trip the `canonical` example.

---

## Canonical Instant Reference

The module uses a fixed canonical datetime example:

`2004-10-31 13:12:11 (Sunday, October 31)

All transformations and validations are based on this fixed time reference.  By using this known
time the code can determinstically create the needed format.  The date time was selected so there
are no overlaps.  Just format this date the way you want and under the hood it will figure out
the right format string.  While you can argue that having to know the format time is the same
as having to remember all the format tags, I argue that I can read the above format in the source
code without having to look it up or "sort of know what it does"

---

## Installation

Clone the repository and ensure you have Python 3.x installed along with required libraries like `pytest` for testing.

```bash
git clone <repository-link>
cd <project-folder>
```

---

## Usage

### Import the Module
```python
from d8fmt import snap_fmt, is_zone_free
```

### Transform a Format String
Convert a canonical string representation into a proper `strftime` format:
```python
from d8fmt import snap_fmt

output_format = snap_fmt("2004-10-31")  # Example input
print(output_format)  # Output: '%Y-%m-%d'
```

### Validate Time Zones
Check if a format string is free from unsupported time zone abbreviations or patterns:
```python
from d8fmt import is_zone_free

is_zone_free("2004-10-31T13:12:11 +0530")  # Raises ValueError
```

---

## Testing

Run tests to confirm functionality and validation.  

```bash
pytest test_d8fmt.py
```

Example Output:
```plaintext
========================== test session starts =========================
collected 28 items

test_d8fmt.py ........................                                    [100%]

=========================== 14 passed in 0.02s =========================
```

---

## Examples

### Token Transformations

| Input          | Output        | Explanation                                           |
|----------------|---------------|-------------------------------------------------------|
| `2004`         | `%Y`          | Year (4-digit)                                        |
| `04`           | `%y`          | Year (last 2 digits)                                  |
| `305`          | `%j`          | Day of the year (1 to 366)                            |
| `31`           | `%d`          | Day of the month (01 to 31)                           |
| `October`      | `%B`          | Full month name                                       |
| `Oct`          | `%b`          | Abbreviated month name                                |
| `10`           | `%m`          | Month number (01 to 12)                               |
| `Sunday`       | `%A`          | Full weekday name                                     |
| `Sun`          | `%a`          | Abbreviated weekday name                              |
| `0`            | `%w`          | Day of the week (Sunday = 0)                          |
| `7`            | `%u`          | Day of the week (ISO, Monday = 1, Sunday = 7)         |
| `13`           | `%H`          | Hour (24-hour clock, 00 to 23)                        |
| `01`           | `%I`          | Hour (12-hour clock, 01 to 12)                        |
| `12`           | `%M`          | Minutes (00 to 59)                                    |
| `11`           | `%S`          | Seconds (00 to 59)                                    |
| `PM` or `AM`   | `%p`          | AM/PM marker (case insensitive)                       |
| `.000000`      | `.%f`         | Fractional seconds (microseconds)                     |
| `43`           | `%W`          | Week of the year (Monday as the first day of the week)|
| `44`           | `%U`          | Week of the year (Sunday as the first day of the week)|

---


## Contribution

Feel free to submit issues or propose enhancements via pull requests. Be sure to follow the existing code structure and guidelines.

---

## License

[MIT License](LICENSE)

---

## Acknowledgments

This module adheres to strict rules for datetime handling with influences from ISO 8601 standards.
