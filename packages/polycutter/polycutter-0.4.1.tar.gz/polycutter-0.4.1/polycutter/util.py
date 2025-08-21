from fractions import Fraction
from decimal import Decimal, ROUND_HALF_UP


def humanize_bytes(n_bytes: int) -> str:
    """
    convert a byte count into a human-readable string using binary prefixes.

    binary prefixes (kibibyte, mebibyte, etc., powers of 1024) are used instead
    of decimal prefixes (kilobyte, megabyte, etc., powers of 1000) because
    file sizes and memory are typically measured in powers of two in computing.
    this provides a more accurate representation of the actual storage size.

    args:
        n_bytes: the number of bytes.

    returns:
        a string representing the size in a human-readable format (e.g., "1.23 MiB").
        returns "0 B" if the input is zero or negative.
    """
    if n_bytes <= 0:
        # Handle zero or negative sizes gracefully.
        return "0 B"

    # Define the units using standard binary prefixes (IEC standard).
    units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB"]
    size = float(n_bytes)
    unit_index = 0

    # Iteratively divide by 1024 to find the most appropriate unit.
    # Stop when the size is less than 1024 or we run out of units.
    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1

    # Format the output string.
    if unit_index == 0:
        # Display bytes as a whole number (no decimals).
        return f"{int(size)} {units[unit_index]}"
    else:
        # Display other units with two decimal places for better readability.
        # Using f-string formatting for concise code.
        return f"{size:.2f} {units[unit_index]}"


def parse_timestamp(ts_str: str) -> float:
    """
    parse various time string formats into total seconds as a float.

    supports:
    - seconds only (e.g., "123.45")
    - minutes and seconds (e.g., "MM:SS.ms", "10:30.5")
    - hours, minutes, and seconds (e.g., "HH:MM:SS.ms", "1:05:22.75")

    args:
        ts_str: the timestamp string to parse.

    returns:
        the total time in seconds as a float.

    raises:
        valueerror: if the timestamp string format is invalid or contains
                    non-numeric parts where numbers are expected.
    """
    # Split the timestamp string by colons. This handles all supported formats.
    parts = ts_str.strip().split(":")
    seconds = 0.0  # use float for accumulation

    # Iterate through the parts in reverse order (seconds, minutes, hours).
    # This makes calculating the total seconds easier using powers of 60.
    for i, part in enumerate(reversed(parts)):
        try:
            # Convert the part to float and multiply by the appropriate power of 60.
            # i=0: seconds (60^0 = 1)
            # i=1: minutes (60^1 = 60)
            # i=2: hours   (60^2 = 3600)
            seconds += float(part) * (60**i)
        except ValueError:
            # Raise an error if a part cannot be converted to a float.
            raise ValueError(f"invalid timestamp component '{part}' in '{ts_str}'")

    return seconds


def format_time(seconds: float) -> str:
    """
    formats a duration in seconds into a human-readable string (hh:mm:ss.mmm or mm:ss.mmm).

    args:
        seconds: the duration in seconds (float).

    returns:
        a formatted time string.
    """
    # Ensure seconds is non-negative
    if seconds < 0:
        seconds = 0

    # Calculate hours, minutes, and remaining seconds
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60

    # Use decimal for precise formatting of milliseconds
    # Quantize rounds to a specific number of decimal places
    # '1.000' means round to 3 decimal places (milliseconds)
    decimal_secs = Decimal(str(secs)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)

    # Format based on whether hours are present
    if hours > 0:
        # hh:mm:ss.mmm format
        # :02d ensures minutes are zero-padded (e.g., 05)
        # :06.3f ensures seconds are zero-padded with 3 decimal places (e.g., 09.123)
        return f"{hours}:{minutes:02d}:{decimal_secs:06.3f}"
    else:
        # mm:ss.mmm format (no hours)
        # :02d ensures minutes are zero-padded only if hours > 0 was false,
        # otherwise just print minutes directly for mm:ss.mmm
        # :06.3f ensures seconds are zero-padded with 3 decimal places
        return f"{minutes}:{decimal_secs:06.3f}"
