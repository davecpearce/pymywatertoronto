""" Define enums for package """

from enum import Enum


class ConsumptionBuckets(Enum):
    """Enum for consumption buckets."""

    TOTAL_USAGE = "total_usage"
    TODAY_USAGE = "today_usage"
    WEEK_TO_DATE_USAGE = "week_to_date_usage"
    MONTH_TO_DATE_USAGE = "month_to_date_usage"
    YEAR_TO_DATE_USAGE = "year_to_date_usage"


class LastPaymentMethod(Enum):
    """Enum for last payment methods."""

    PRE_AUTHORIZED = "1"
    MAIL_IN_CHEQUE = "2"
    IN_PERSION = "3"
    BANK_PAYMENT = "4"
    PAYMENT_DROP_BOX = "5"
    MYTORONTO_PAY = "6"
