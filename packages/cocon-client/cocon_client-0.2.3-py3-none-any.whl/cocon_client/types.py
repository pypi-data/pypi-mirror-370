# TELEVIC CoCon CLIENT
# types.py
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 3P Technologies Srl
"""Type definitions and helper structures for the CoCon client."""

from dataclasses import dataclass
from enum import Enum
from typing import TypeVar, NamedTuple, Callable, Awaitable, Any
from asyncio import Future
from datetime import date

T = TypeVar("T")
JSON = dict[str, Any]
CommandParams = dict[str, str] | None

# Signature for your user-supplied notification handler
AsyncHandler = Callable[[JSON], Awaitable[None]]

# Signature for the on_handler_error callback
ErrorHandler = Callable[[Exception, JSON], None]


class QueuedCommand(NamedTuple):
    """
    Internal command queue payload.

    Attributes:
        endpoint: The CoCon API endpoint name (e.g. "Subscribe").
        params:  Optional query parameters.
        future:  asyncio.Future that will be set with the response.
    """

    endpoint: str
    params: CommandParams | None
    future: Future[Any]


class Model(str, Enum):
    """Represents the various CoCon data models used in the API."""

    ROOM = "Room"
    MICROPHONE = "Microphone"
    MEETING_AGENDA = "MeetingAgenda"
    VOTING = "Voting"
    TIMER = "Timer"
    DELEGATE = "Delegate"
    AUDIO = "Audio"
    INTERPRETATION = "Interpretation"
    LOGGING = "Logging"
    BUTTON_LED_EVENT = "ButtonLED_Event"
    INTERACTIVE = "Interactive"
    EXTERNAL = "External"
    INTERCOM = "Intercom"
    VIDEO = "Video"

    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value


class _EP(str, Enum):
    """Internal enumeration of known API endpoints."""

    CONNECT = "Connect"
    NOTIFICATION = "Notification"


@dataclass(slots=True)
class Config:
    """Configuration for CoConClient behavior."""

    poll_interval: float = 1.0
    max_retries: int = 5
    backoff_base: float = 0.5
    session_timeout: float = 7.0


@dataclass(slots=True)
class Group:
    id_: int
    name: str


@dataclass(slots=True)
class Delegate:
    """Class that define the data model that represents the single delegate"""

    id_: int
    first_name: str
    name: str
    street: str
    street_number: int
    post_code: str
    city: str
    country: str
    title: str
    birth_date: date
    district: str
    biography: str
    groups: tuple[Group, ...]
