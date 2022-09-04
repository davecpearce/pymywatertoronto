"""All functions for formatting time."""

from datetime import date, timedelta


def format_date(date: date) -> date:
    """
    Return date only from time

    Args:
        time: Expected time as datetime.datetime class

    Returns:
        Formatted date.

    """
    return date.strftime("%Y-%m-%d")  # noqa: WPS323


def format_start_year(date: date) -> date:
    """
    Format date starting at the first day of year for provided datetime.

    Args:
        time: Expected date as datetime.date class

    Returns:
        Formatted date.

    """
    return format_date(date.replace(month=1, day=1))


def format_start_month(date: date) -> date:
    """
    Format date starting at the first of the month for provided datetime.

    Args:
        date: Expected date as datetime.date class

    Returns:
        Formatted date.

    """
    return format_date(date.replace(day=1))


def format_start_week(date: date) -> date:
    """
    Format date starting at the start of week for provided date.

    Args:
        date: Expected date as datetime.date class

    Returns:
        Formatted date.
    """
    return format_date(date - timedelta(days=date.weekday()))


def format_yesterday(date: date) -> date:
    """
    Format date for yesterday for provided datetime.

    Args:
        date: Expected date as datetime.date class

    Returns:
        Formatted date.

    """
    return format_date(date - timedelta(days=1))
