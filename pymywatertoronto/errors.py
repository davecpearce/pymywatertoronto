class AccountNotValidatedError(Exception):
    """Raised when the account has not been validated yet."""

    def __init__(self, status: str) -> None:
        """Initialize."""
        super().__init__(status)
        self.status = status


""" Define package errors """


class ApiError(Exception):
    """Raised when MyWaterToronto API request ended in error."""

    def __init__(self, status: str) -> None:
        """Initialize."""
        super().__init__(status)
        self.status = status


class AccountDetailsError(Exception):
    """Raised when MyWaterToronto API request ended in error."""

    def __init__(self, status: str) -> None:
        """Initialize."""
        super().__init__(status)
        self.status = status


class SessionValidationError(Exception):
    """Raised when Account Info is invalid."""

    def __init__(self, status: str) -> None:
        """Initialize."""
        super().__init__(status)
        self.status = status


class ValidateAccountInfoError(Exception):
    """Raised when Account Info is invalid."""

    def __init__(self, status: str) -> None:
        """Initialize."""
        super().__init__(status)
        self.status = status
