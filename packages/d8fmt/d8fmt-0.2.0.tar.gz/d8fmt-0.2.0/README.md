# Format By Example for Datetime

A Python module designed to transform canonical datetime examples into deterministic and 
platform-independent format strings using `strftime`/`strptime` directives. 
Human-readable "canonical" dates, or human-readable variable substitutions may be used
to create format strings that are better than the cryptic formats that look like
`%b. %d %Y %I-%M-%S %p`. While these strings are efficient they are not readable. 
The letters have little connection to the actual meaning.

`d8fmt` gives two ways to format dates that are readable a canonical date where all parts
of the date are unique and a deterministic date time can be created.

```2004/10/31 13:12:11.000000``` to generate ```2004/10/31 13:12:11.000000```

This datetime has unique values for all numeric quantities as shown in the table below. So
every time you want a date fomratted you give an example for the date 10/31/2004 13:12:11.00000
which was a Sunday, in October, in the 43rd ISO Week and the 44 Week, ws the 7th ISO day-of-week
and the 0th iso-day-of-week...and was the 305th day of the year.  Those numbers are all unique, 
just format that day the way you want it with those values and the correct format string will
be created.

The second way is through English label substitutions that are far more verbose but more readable
that the canonical form.

`{YEAR4}/{MONTH#}/{DAY#} {HOUR24}:{MINUTE}:{SECOND}.{MICROSEC}` to generate  ```2004/10/31 13:12:11.000000```

This creates strings that are readable but quite verobose, ensuring you will know the values are correct
but you won't have a sense of what the string looks like.

Alternatively you can create dates with "macros" that have english names rather than the numbers 
from the fixed date.  These macros use the builtin `str.format`

`{YEAR4}/{MONTH#}/{DAY#} {HOUR24}:{MINUTE}:{SECOND}.{MICROSEC}` to generate  ```2004/10/31 13:12:11.000000```

Here is a table showing how the two systems relate.  As it is now you can use any of the format strings,
and it should "just work" since all 3 systems are unique and there is no overlap between them.  It can
get complicated if you put a lot of non date text in your format string.

| **Canonical** | **Macro**    | **Description**                                  | **%Format** |
|---------------|--------------|--------------------------------------------------|------------------|
| `01`          | `{HOUR12}`     | Hour in 12-hour clock (zero-padded)              | `%I`             |
| `13`          | `{HOUR24}`     | Hour in 24-hour clock (zero-padded)              | `%H`             |
| `305`         | `{DOY}`      | Day of the year (1–366, zero-padded)             | `%j`             |
| `04`          | `{YEAR2}`    | Year without century (last two digits)           | `%y`             |
| `2004`        | `{YEAR4}`    | Year with century                                | `%Y`             |
| `October`     | `{MONTH}`    | Full month name                                  | `%B`             |
| `Oct`         | `{MONTH3}`   | Abbreviated month name                           | `%b`             |
| `10`          | `{MONTH#}`   | Month as a number (zero-padded, 01–12)           | `%m`             |
| `Sunday`      | `{DAY}`      | Full weekday name                                | `%A`             |
| `Sun`         | `{DAY3}`     | Abbreviated weekday name                         | `%a`             |
| `31`          | `{DAY#}`     | Day of the month (zero-padded)                   | `%d`             |
| `12`          | `{MINUTE}`   | Minute (zero-padded)                             | `%M`             |
| `11`          | `{SECOND}`   | Second (zero-padded)                             | `%S`             |
| `.000000`     | `{MICROSEC}` | Microsecond (zero-padded, 6 digits)              | `%f`             |
| `AM`          | `{AM}`       | AM/PM marker                                     | `%p`             |
| `PM`          | `{PM}`       | AM/PM marker                                     | `%p`             |
| `44`          | `{WOY}`      | Week of the year (Sunday as first day)           | `%U`             |
| `43`          | `{WOYISO}`   | ISO week number of the year (Mon as first day)   | `%W`             |
| `7`           | `{WDAY#ISO}` | Day of the week (ISO, Monday=1 to Sunday=7)      | `%u`             |
| `0`           | `{WDAY#}`    | Day of the week (Sunday-based, 0=Sun to 6=Sat) | `%w`             |
| _N/A_         | `{TZ}`       | Timezone abbreviation                            | `%Z`             |
| _N/A_         | `{UTCOFF}`   | UTC offset in the form ±HHMM                     | `%z`             |

Here are some examples of converting these format strings into datetime ready format strings.

```shell
>>>d.stezftime("{DAY} {DAY#}-{MONTH#}-{YEAR4}" )
'Friday 15-08-2025'
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
from d8fmt import snap_fmt, is_zone_free, datetime_snap
```

### Override datetime object

There is a simple override of the datatime class that adds the `stezftime` method that supports
both styles of formatting.

```shell
>>d = d8fmt.datetime_snap(year=2025,month=8,day=15,hour=13,minute=12,second=11)
>>d.stezftime("{DAY}-{DAY#}-{MONTH}-{YEAR2}")
'Friday-15-August-25'
>>d.stezftime("{DAY}-{MONTH}-{YEAR2} {HOUR12}:{MINUTE}:{SECOND} {PM}")
'Friday-August-15 01:12:11 PM'
>>d.stezftime("{DAY3}-{MONTH3}-{YEAR2} {HOUR24}:{MINUTE}:{SECOND} {PM}")
'Fri-Aug-25 13:12:11 PM'
>>d.stezftime("Sunday Oct 31 2004  13:12:11.000000")
'Friday Aug 15 2025  13:12:11.000000'
````

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


## Contribution

Feel free to submit issues or propose enhancements via pull requests. Be sure to follow the existing code structure and guidelines.

---

## License

[MIT License](LICENSE)

---

## Acknowledgments

This module adheres to strict rules for datetime handling with influences from ISO 8601 standards.
