# TELEVIC CoCon CLIENT
# parser.py
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 3P Technologies Srl
"""Utilities to parse CoCon API notifications into Python dataclasses."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Type, List, Union, Callable, Optional
from .types import JSON

_model_registry: Dict[str, Type] = {}


def register_model(name: str) -> Callable[..., Any]:
    """Decorator to register a model class under a given JSON key."""

    def decorator(cls) -> Any:
        _model_registry[name] = cls
        return cls

    return decorator


def parse_notification(message: JSON) -> Any:
    """Convert a raw notification payload into a dataclass instance.

    Args:
        message: The JSON object received from the server.

    Returns:
        The parsed dataclass instance representing the payload.

    Raises:
        NotImplementedError: If the payload contains an unknown model key.
    """
    for key, payload in message.items():
        model_cls = _model_registry.get(key)
        if model_cls:
            return model_cls.from_dict(payload)
    raise NotImplementedError(
        f"Parser for {list(message.keys())!r} not implemented yet."
    )


@dataclass
class BaseModel:
    """Base class for models parsed from CoCon notifications."""

    @classmethod
    def from_dict(cls, data) -> BaseModel:
        return cls(**data)


@register_model("Meeting")
@dataclass
class Meeting(BaseModel):
    Id: int = -1  # The id of the meeting
    Title: str = ""  # The title of the meeting
    Description: str = ""  # The description of the meeting
    StartTime: str = ""  # The start time of the meeting
    State: str = ""  # The state of the meeting.
    Nameplate_Layout: str = ""


@register_model("Meetings")
@dataclass
class Meetings(BaseModel):
    meetings: list[Meeting]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Meeting:
        items = [Meeting.from_dict(i) for i in data]
        return cls(meetings=items)

    def get_active(self) -> Meeting:
        for item in self.meetings:
            if item.State in ["Running", "Prepared"]:
                return item
        return None


@register_model("IndividualVote")
@dataclass
class IndividualVote(BaseModel):
    DelegateId: int
    VotingOptionId: Union[int, list[int]]
    SeatNumber: int


@register_model("VotingCountWeight")
@dataclass
class VotingCountWeight(BaseModel):
    Count: int
    Weight: float


@register_model("VotingOption")
@dataclass
class VotingOption(BaseModel):
    Id: int
    Name: str
    Color: str


@register_model("VotingOptionVoteDetail")
@dataclass
class VotingOptionVoteDetail(BaseModel):
    Option: VotingOption
    OptionVoted: VotingCountWeight


@register_model("AuthorityAssigned")
@dataclass
class AuthorityAssigned(BaseModel):
    Present: int
    Voted: int
    Register: int


@register_model("VotingResultSummary")
@dataclass
class VotingResultSummary(BaseModel):
    Total: VotingCountWeight
    Voted: VotingCountWeight
    NotVoted: VotingCountWeight
    Options: VotingOptionVoteDetail
    AuthorityAssigned: AuthorityAssigned


@register_model("VotingState")
@dataclass
class VotingState(BaseModel):
    Id: int
    State: str
    VotingTemplate: str = ""


@register_model("VotingOutcome")
@dataclass
class VotingOutcome(BaseModel):
    Id: int
    VotingOptionId: int
    OutCome: str


@register_model("HungVotingOccured")
@dataclass
class HungVotingOccured(BaseModel):
    Id: int
    State: bool


@register_model("MeetingStatus")
@dataclass
class MeetingStatus(BaseModel):
    MeetingId: int
    State: str


@register_model("MeetingAgendaChanged")
@dataclass
class MeetingAgendaChanged(BaseModel):
    MeetingId: int


@register_model("GeneralVotingResults")
@dataclass
class GeneralVotingResults(BaseModel):
    Id: int  # ID of the VotingAgendaItem
    VotingResults: VotingResultSummary


@register_model("IndividualVotingResults")
@dataclass
class IndividualVotingResults(BaseModel):
    Id: int
    VotingResults: List[IndividualVote]

    @classmethod
    def from_dict(cls, data: JSON) -> IndividualVotingResults:
        items = [IndividualVote.from_dict(i) for i in data.get("VotingResults", [])]
        return cls(Id=data["Id"], VotingResults=items)


@register_model("Group")
@dataclass
class Group(BaseModel):
    Id: int
    Name: str


@register_model("Delegate")
@dataclass
class Delegate(BaseModel):
    Id: int = -1
    Name: str = ""
    MiddleName: str = ""
    FirstName: str = ""
    Title: str = ""
    BadgeNumber: str = ""
    UserName: str = ""
    Password: str = ""
    Street: str = ""
    StreetNumber: int = -1
    City: str = ""
    PostCode: str = ""
    Country: str = ""
    District: str = ""
    BirthDate: str = ""  # yyyy-MM-dd
    Email: str = ""
    PhoneNr: str = ""
    VotingRight: bool = False
    VotingWeight: float = 0.0
    FingerprinterData: str = ""
    KeypadLoginCode: str = ""
    Biography: str = ""
    Groups: Optional[list[Group]] = field(default_factory=list)
    SeatNumber: int = -1


@register_model("Delegates")
@dataclass
class Delegates(BaseModel):
    delegates: Optional[list[Delegate]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: JSON) -> Delegates:
        items = [Delegate.from_dict(i) for i in data]
        return cls(delegates=items)

    def by_id(self, delegateId: int) -> Delegate | None:
        if self.delegates is None:
            return None

        for d in self.delegates:
            if d.Id == delegateId:
                return d
        return None

    def filter_by_voting_right(self, voting_right: bool = True) -> Delegates:
        if self.delegates is None:
            return Delegates()

        items = [d for d in self.delegates if d.VotingRight == voting_right]
        return Delegates(delegates=items)


@register_model("Agenda_ItemChanged")
@register_model("AgendaItem")
@dataclass
class AgendaItem(BaseModel):
    Id: str = ""
    Title: str = ""
    Description: str = ""
    Type: str = ""
    State: str = ""
    Children: Optional[list[AgendaItem]] = field(default_factory=list)
    IdInDb: int = 0
    AgendaItemSpeechTimeSettings: str = ""
    VotingOptions: Optional[List[VotingOption]] = field(default_factory=list)
    Lectures: Optional[List[Delegate]] = field(default_factory=list)


@register_model("AgendaItems")
@dataclass
class AgendaItems(BaseModel):
    agenda_items: Optional[list[AgendaItem]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: JSON) -> AgendaItems:
        items = [AgendaItem.from_dict(i) for i in data]
        return cls(agenda_items=items)

    def get_active(self) -> AgendaItem:
        if self.agenda_items is None:
            return AgendaItem()
        for item in self.agenda_items:
            if item.State == "active":
                return item
        return AgendaItem


@register_model("ScreenLockRemoved")
@dataclass
class ScreenLockRemoved(BaseModel):
    screen_lock_removed: bool

    @classmethod
    def from_dict(cls, data):
        return cls(screen_lock_removed=data)


@register_model("DelegateScreenSetChanged")
@dataclass
class DelegateScreenSetChanged(BaseModel):
    IsLocked: bool
    IsGoTo: bool
    IsShow: bool
    Screen: str
    Option: str
