# TELEVIC CoCon CLIENT
# errors.py
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 3P Technologies Srl
"""Exception hierarchy used by the CoCon client."""


class CoConError(Exception):
    """Base class for all client errors."""

    pass


class CoConConnectionError(CoConError):
    """Raised when the client fails to establish a connection.

    This error usually indicates that the server is unreachable or returned a
    failure during the initial handshake.
    """

    pass


class CoConCommandError(CoConError):
    """Raised when a command sent to the API fails."""

    def __init__(self, endpoint: str, status: int, body: str | None = None) -> None:
        """Initialize the command error with endpoint, status code, and optional response body.

        Args:
            endpoint (str): The API endpoint that failed.
            status (int): HTTP status code returned.
            body (str | None, optional): Optional response body for error inspection.
                Defaults to None.
        """
        super().__init__(f"'/{endpoint}' failed with HTTP {status}")
        self.endpoint: str = endpoint
        self.status: int = status
        self.body: str | None = body


class CoConRetryError(CoConError):
    """Raised when a retryable operation exceeds the retry limit.

    This typically happens when transient failures persist beyond the configured
    ``Config.max_retries`` value.
    """

    pass
