"""All functions for formatting time."""

from datetime import date, timedelta


def format_date(fdate: date) -> date:
    """
    Return date only from time

    Args:
        time: Expected time as datetime.datetime class

    Returns:
        Formatted date.

    """
    return fdate.strftime("%Y-%m-%d")


def format_start_year(fdate: date) -> date:
    """
    Format date starting at the first day of year for provided datetime.

    Args:
        time: Expected date as datetime.date class

    Returns:
        Formatted date.

    """
    return format_date(fdate.replace(month=1, day=1))


def format_start_month(fdate: date) -> date:
    """
    Format date starting at the first of the month for provided datetime.

    Args:
        date: Expected date as datetime.date class

    Returns:
        Formatted date.

    """
    return format_date(fdate.replace(day=1))


def format_start_week(fdate: date) -> date:
    """
    Format date starting at the start of week for provided date.

    Args:
        date: Expected date as datetime.date class

    Returns:
        Formatted date.
    """
    return format_date(fdate - timedelta(days=fdate.weekday()))


def format_yesterday(fdate: date) -> date:
    """
    Format date for yesterday for provided datetime.

    Args:
        date: Expected date as datetime.date class

    Returns:
        Formatted date.

    """
    return format_date(fdate - timedelta(days=1))
