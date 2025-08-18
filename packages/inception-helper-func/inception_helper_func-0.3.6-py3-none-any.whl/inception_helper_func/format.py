import re
from datetime import datetime, UTC
import pytz


def format_datetime_from_iso(
    date: str, date_format: str, time_format: str, time_zone: str
) -> dict:
    """
    Formats a date string based on the provided format and timezone.

    :param date: The date string (e.g., "2025-04-25T12:00:00Z").
    :param date_format: The date format (e.g., 'd MMM yyyy').
    :param time_format: The time format (e.g., 'hh:mm a').
    :param time_zone: The timezone (e.g., 'America/Ojinaga').
    :return: A dictionary containing formatted time, date, and datetime.
    """
    tz = pytz.timezone(time_zone)
    utc_time = datetime.fromisoformat(date).replace(tzinfo=pytz.utc)
    zoned_time = utc_time.astimezone(tz)

    formatted_time = zoned_time.strftime(time_format)
    formatted_date = zoned_time.strftime(date_format)
    formatted_datetime = zoned_time.strftime(f"{date_format} {time_format}")

    return {
        "time": formatted_time,
        "date": formatted_date,
        "dateTime": formatted_datetime,
    }


def format_datetime_from_epoch(
    date: int, date_format: str, time_format: str, time_zone: str
) -> dict:
    """
    Formats an epoch timestamp based on the provided format and timezone.

    :param date: The epoch timestamp (e.g., 1714156800).
    :param date_format: The date format (e.g., 'd MMM yyyy').
    :param time_format: The time format (e.g., 'hh:mm a').
    :param time_zone: The timezone (e.g., 'America/Ojinaga').
    :return: A dictionary containing formatted time, date, and datetime.
    """
    tz = pytz.timezone(time_zone)
    epoch_time = datetime.fromtimestamp(date, tz=UTC)
    zoned_time = epoch_time.astimezone(tz)

    formatted_time = zoned_time.strftime(time_format)
    formatted_date = zoned_time.strftime(date_format)
    formatted_datetime = zoned_time.strftime(f"{date_format} {time_format}")

    return {
        "time": formatted_time,
        "date": formatted_date,
        "dateTime": formatted_datetime,
    }


def clean_name(name: str) -> str:
    name = " ".join(
        re.sub(r"[^a-zA-Z0-9\s\-]+", "", word.strip()) for word in name.split()
    )
    return name.strip()


if __name__ == "__main__":
    # Example usage with an epoch timestamp
    print(
        format_datetime_from_epoch(
            1714156800, "%d %b %Y", "%I:%M %p", "America/Ojinaga"
        )
    )
