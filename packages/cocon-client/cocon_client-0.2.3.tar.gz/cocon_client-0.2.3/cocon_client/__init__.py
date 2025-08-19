# TELEVIC CoCon CLIENT
# __init__.py
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 3P Technologies Srl
"""Televic CoCon client package.

This package exposes the :class:`CoConClient` along with common error types,
data models and parsing helpers used by the client.
"""

# expose the client
from .client import CoConClient, logger

# errors
from .errors import (
    CoConError,
    CoConConnectionError,
    CoConCommandError,
    CoConRetryError,
)

# types
from .types import AsyncHandler, ErrorHandler, CommandParams, Config, Model, JSON

# parser
from .parser import (
    parse_notification,
    Meeting,
    IndividualVotingResults,
    IndividualVote,
    Delegate,
    Delegates,
    AgendaItem,
    AgendaItems,
)

__all__ = [
    "CoConClient",
    "logger",
    "Config",
    "Model",
    "CoConError",
    "CoConConnectionError",
    "CoConCommandError",
    "CoConRetryError",
    "AsyncHandler",
    "ErrorHandler",
    "CommandParams",
    "JSON",
    "parse_notification",
    "Meeting",
    "IndividualVotingResults",
    "IndividualVote",
    "Delegate",
    "Delegates",
    "AgendaItem",
    "AgendaItems",
]
