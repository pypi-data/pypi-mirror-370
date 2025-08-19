"""Models."""

from __future__ import annotations

__all__: tuple[str, ...] = (
    "CallDirection",
    "CallID",
    "CallItem",
    "CallResponse",
    "CallScope",
    "CallsRequest",
    "CallsResponse",
    "ContentFields",
    "ContentFieldsCollaboration",
    "ContentFieldsContent",
    "ContentFieldsInteraction",
    "ContentSelector",
    "ContextTiming",
    "ContextType",
    "Cursor",
    "EventID",
    "FilterParams",
    "MediaType",
    "RecordsInfo",
    "RequestID",
    "StrID",
    "UserID",
    "WorkspaceID",
)

from datetime import datetime, timedelta  # noqa: TC003
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, HttpUrl

from gongy.utils.model_utils import AllTrueModel
from gongy.utils.types import Milliseconds  # noqa: TC001

type StrID = str

type WorkspaceID = StrID
type RequestID = StrID
type CallID = StrID
type UserID = StrID
type EventID = StrID
type ObjectID = StrID
type PartyID = StrID
type SpeakerID = StrID
type TrackerID = StrID
type CallOutcomeID = StrID
type CommentID = StrID

type Cursor = str


def to_camel(s: str) -> str:
    """snake_case -> camelCase."""
    parts = s.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


class CallDirection(str, Enum):
    """Call direction."""

    INBOUND = "Inbound"
    OUTBOUND = "Outbound"
    CONFERENCE = "Conference"
    UNKNOWN = "Unknown"


class CallScope(str, Enum):
    """Scope of the call."""

    INTERNAL = "Internal"
    EXTERNAL = "External"
    UNKNOWN = "Unknown"


class MediaType(str, Enum):
    """Media type of the call recording."""

    VIDEO = "Video"
    AUDIO = "Audio"


class RecordsInfo(BaseModel):
    """Information about the number of records that match the requested filter."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    total_records: int
    """Total number of records."""

    current_page_size: int
    """Number of records in the current page."""

    current_page_number: int
    """Current page number."""

    cursor: Cursor | None = None
    """Pagination cursor. Returned only when there are more records to be retrieved.
    Pass this value in the next request to fetch the next page."""


class CallItem(BaseModel):
    """One call entry."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    id: CallID
    """Gong's unique numeric identifier for the call (up to 20 digits)."""

    url: HttpUrl
    """URL to the call page in the Gong web application."""

    title: str
    """The title of the call."""

    scheduled: datetime
    """Scheduled date and time of the call (ISO-8601)."""

    started: datetime
    """Date and time when the call was recorded (ISO-8601)."""

    duration: timedelta
    """Duration of the call in seconds."""

    primary_user_id: UserID
    """Primary user ID of the team member who hosted the call."""

    direction: CallDirection
    """Call direction. Allowed values: Inbound, Outbound, Conference, Unknown."""

    system: str
    """System with which the call was carried out (e.g., WebEx, ShoreTel)."""

    scope: CallScope
    """Scope of the call: 'internal', 'external', or 'unknown'."""

    media: MediaType
    """Media type. Allowed values: Video, Audio."""

    language: str
    """Language code (ISO-639-2B), e.g., 'eng', 'fre', 'spa', 'ger', 'ita'.
    Also: 'und', 'zxx'."""

    workspace_id: WorkspaceID
    """Gong's unique numeric identifier for the call's workspace (up to 20 digits)."""

    sdr_disposition: str | None = None
    """SDR disposition of the call—automatically provided or manually entered."""

    client_unique_id: StrID | None = None
    """Call's unique ID in the origin recording system."""

    custom_data: str | None = None
    """Custom metadata provided during call creation."""

    purpose: str | None = None
    """Purpose of the call."""

    meeting_url: HttpUrl | None = None
    """Meeting provider URL where the web conference was recorded."""

    is_private: bool
    """Whether the call is private."""

    calendar_event_id: EventID | None = None
    """ID of the associated Google or Outlook Calendar event."""


class CallsResponse(BaseModel):
    """Calls."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    request_id: RequestID
    """A Gong request reference ID generated for this request.
    Use for troubleshooting."""

    records: RecordsInfo
    """Information about the number of records that match the requested filter."""

    calls: list[CallItem]
    """A list in which each item specifies one call."""


class CallResponse(BaseModel):
    """Call."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    request_id: RequestID
    """A Gong request reference ID generated for this request.
    Use for troubleshooting."""

    call: CallItem
    """Call."""


class ContextType(str, Enum):
    """Type of context data to include."""

    NONE = "None"
    BASIC = "Basic"
    EXTENDED = "Extended"


class ContextTiming(str, Enum):
    """Timing for context data."""

    NOW = "Now"
    TIME_OF_CALL = "TimeOfCall"


class FilterParams(BaseModel):
    """Filter parameters for listing recorded calls."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    from_date_time: datetime | None = None
    """Start datetime (ISO-8601). Returns calls that started on or after this time."""

    to_date_time: datetime | None = None
    """End datetime (ISO-8601). Returns calls that started before this time."""

    workspace_id: WorkspaceID | None = None
    """Optional workspace identifier. Filters calls belonging to this workspace."""

    call_ids: list[CallID] | None = None
    """List of call IDs to include. If omitted, returns all calls in the date range."""

    primary_user_ids: list[UserID] | None = None
    """List of primary user IDs. If supplied,
    returns only calls hosted by these users."""


class ContentFieldsContent(AllTrueModel):
    """Content-related fields to include in the response."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    structure: bool | None = None
    """If true, include call agenda if available."""

    topics: bool | None = None
    """If true, include duration of call topics."""

    trackers: bool | None = None
    """If true, include smart tracker and keyword tracker information."""

    tracker_occurrences: bool | None = None
    """If true, include timing and speaker ID for each tracker occurrence."""

    points_of_interest: bool | None = None
    """Deprecated."""

    brief: bool | None = None
    """If true, include the spotlight call brief."""

    outline: bool | None = None
    """If true, include the call outline."""

    highlights: bool | None = None
    """If true, include the call highlights."""

    call_outcome: bool | None = None
    """If true, include the outcome of the call."""

    key_points: bool | None = None
    """If true, include the key points of the call."""


class ContentFieldsInteraction(AllTrueModel):
    """Interaction-related fields to include in the response."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    speakers: bool | None = None
    """If true, include the time each participant spoke."""

    video: bool | None = None
    """If true, include video statistics."""

    person_interaction_stats: bool | None = None
    """If true, include statistics for the host of the call."""

    questions: bool | None = None
    """If true, include question counts."""


class ContentFieldsCollaboration(AllTrueModel):
    """Collaboration-related fields to include in the response."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    public_comments: bool | None = None
    """If true, include public comments made for this call."""


class ContentFields(AllTrueModel):
    """Exposed fields to include in the response object."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    parties: bool | None = None
    """If true, include information about the parties of the call."""

    content: ContentFieldsContent | None = None
    """Content section fields to include."""

    interaction: ContentFieldsInteraction | None = None
    """Interaction section fields to include."""

    collaboration: ContentFieldsCollaboration | None = None
    """Collaboration section fields to include."""

    media: bool | None = None
    """If true and available, include audio and video URLs (valid for 8 hours)."""


class ContentSelector(AllTrueModel):
    """Identifies which data components are needed."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    context: ContextType = ContextType.NONE
    """Type of context data to include."""

    context_timing: list[ContextTiming] | None = None
    """Timing for the context data. Can be Now, TimeOfCall, or both."""

    exposed_fields: ContentFields | None = None
    """Fields to expose in the response."""


class CallsRequest(BaseModel):
    """Request model for retrieving calls."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    cursor: Cursor | None = None
    """Cursor for pagination.
    Provide the value from the previous response to fetch the next page."""

    filter: FilterParams | None = None
    """Filter parameters."""

    content_selector: ContentSelector | None = None
    """Content selector specifying which components to include."""


# ===== Enums =====


class ExternalSystem(str, Enum):
    """External system name used in context links."""

    SALESFORCE = "Salesforce"
    HUBSPOT = "HubSpot"
    MICROSOFT_DYNAMIC = "MicrosoftDynamic"
    GENERIC = "Generic"


class CallContextObjectType(str, Enum):
    """Object types allowed for call-level context."""

    OPPORTUNITY = "Opportunity"
    ACCOUNT = "Account"


class PartyContextObjectType(str, Enum):
    """Object types allowed for party-level context."""

    CONTACT = "Contact"
    USER = "User"
    LEAD = "Lead"


class TrackerType(str, Enum):
    """Type of tracker."""

    KEYWORD = "KEYWORD"
    SMART = "SMART"


class PartyAffiliation(str, Enum):
    """Whether the participant is internal or external."""

    INTERNAL = "Internal"
    EXTERNAL = "External"
    UNKNOWN = "Unknown"


class ParticipantMethod(str, Enum):
    """Whether the participant was invited or only attended."""

    INVITEE = "Invitee"
    ATTENDEE = "Attendee"


class VideoSegmentType(str, Enum):
    """Type of video segment."""

    BROWSER = "Browser"
    PRESENTATION = "Presentation"
    WEBCAM_PRIMARY_USER = "WebcamPrimaryUser"
    WEBCAM_NON_COMPANY = "WebcamNonCompany"
    WEBCAM = "Webcam"


# ===== Call-level Context (links to external systems) =====


class ExternalField(BaseModel):
    """External object data field."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    name: str
    """Field name."""

    value: Any
    """Field value."""


class ExternalObject(BaseModel):
    """Object within an external system (call-level context)."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    object_type: CallContextObjectType
    """Object type (e.g., Opportunity, Account)."""

    object_id: ObjectID
    """Object ID."""

    fields: list[ExternalField] | None = None
    """Array of external object data."""


class CallContextItem(BaseModel):
    """Call-level context entry."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    system: ExternalSystem
    """External system name (e.g., Salesforce)."""

    objects: list[ExternalObject] | None = None
    """Objects within the external system."""

    timing: ContextTiming
    """Timing of object (Now or TimeOfCall)."""


# ===== Party-level Context =====


class PartyContextField(BaseModel):
    """Party external object field."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    name: str
    """Field name. All custom fields are supported."""

    value: Any
    """Object value."""


class PartyContextObject(BaseModel):
    """Object within an external system (party-level context)."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    object_type: PartyContextObjectType
    """Object type (Contact, User, Lead)."""

    object_id: ObjectID
    """Object ID."""

    fields: list[PartyContextField] | None = None
    """Object fields."""


class PartyContextItem(BaseModel):
    """Party-level context entry."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    system: ExternalSystem
    """External system name (e.g., Salesforce)."""

    objects: list[PartyContextObject] | None = None
    """Objects within the external system."""

    timing: ContextTiming
    """Timing of object (Now or TimeOfCall)."""


# ===== Parties =====


class Party(BaseModel):
    """Participant in the call."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    id: PartyID
    """Unique ID of the participant in the call."""

    email_address: EmailStr | None = None
    """Email address."""

    name: str | None = None
    """Participant name."""

    title: str | None = None
    """Job title."""

    user_id: UserID | None = None
    """User ID within the Gong system, if the participant exists in the system."""

    speaker_id: SpeakerID | None = None
    """Unique ID of a participant that spoke in the call
    (references transcript speaker IDs)."""

    context: list[PartyContextItem] | None = None
    """Links to external systems such as CRM, Dialer, Case Management, etc."""

    affiliation: PartyAffiliation | None = None
    """Whether the participant is from the company or not."""

    phone_number: str | None = None
    """Participant phone number."""

    methods: list[ParticipantMethod] | None = None
    """Whether the participant was invited to the meeting or only attended the call."""


# ===== Content =====


class StructureItem(BaseModel):
    """Agenda item / part of the call."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    name: str
    """Agenda name."""

    duration: timedelta
    """Duration of this part of the call."""


class TrackerOccurrence(BaseModel):
    """When a tracker term occurred."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    start_time: timedelta
    """Seconds from the beginning of the call when the tracker phrase was captured."""

    speaker_id: SpeakerID
    """Speaker ID who said the tracker term."""


class TrackerPhrase(BaseModel):
    """Specific phrase occurrence data for keyword trackers."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    count: int
    """Number of times this phrase was mentioned."""

    occurrences: list[TrackerOccurrence] | None = None
    """List of times each phrase was mentioned."""

    phrase: str
    """The specific phrase within the tracker (e.g., 'Walmart')."""


class Tracker(BaseModel):
    """Tracker summary for the call."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    id: TrackerID
    """Unique ID of the tracker."""

    name: str
    """Tracker name (e.g., Stores)."""

    count: int
    """Number of times words in this tracker occurred in the call."""

    type: TrackerType
    """Type of tracker (KEYWORD or SMART)."""

    occurrences: list[TrackerOccurrence] | None = None
    """When tracker terms were mentioned.
    Empty when keyword trackers are set to display each term separately."""

    phrases: list[TrackerPhrase] | None = None
    """Details for each specific keyword phrase (smart trackers are not listed here)."""


class TopicItem(BaseModel):
    """Topic discussed in the call."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    name: str
    """Topic name (e.g., Pricing)."""

    duration: timedelta
    """Total time spent on this topic."""


class OutlineItem(BaseModel):
    """Item within an outline section."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    text: str
    """Text of this section item."""

    start_time: timedelta
    """Start time of this section item, in seconds from the start of the call."""


class OutlineSection(BaseModel):
    """Outline section of the call."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    section: str
    """Name of this section of the call."""

    start_time: timedelta
    """Starting time of this section, in seconds from the start of the call."""

    duration: timedelta
    """Duration of this section, in seconds."""

    items: list[OutlineItem] | None = None
    """List of items of this section."""


class HighlightItem(BaseModel):
    """Highlight item within a highlight section."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    text: str
    """Text of the highlights section item."""

    start_times: list[timedelta] | None = None
    """Starting times of the highlight item, in seconds from the start of the call."""


class HighlightSection(BaseModel):
    """Highlights section of the call."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    title: str
    """Title of the highlights section."""

    items: list[HighlightItem] | None = None
    """List of highlight items of the call in this section."""


class CallOutcome(BaseModel):
    """Outcome of the call, as automatically set by Gong AI."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    id: CallOutcomeID
    """ID of the call outcome."""

    category: str
    """Category of the call outcome."""

    name: str
    """Name of the call outcome."""


class KeyPoint(BaseModel):
    """Key point extracted from the call."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    text: str
    """Text of the key point."""


class Content(BaseModel):
    """Analysis of the interaction content."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    structure: list[StructureItem] | None = None
    """Agenda divided into parts."""

    trackers: list[Tracker] | None = None
    """Smart/keyword tracker information."""

    topics: list[TopicItem] | None = None
    """Topics discussed during the call."""

    brief: str | None = None
    """Spotlight call brief (when available and requested)."""

    outline: list[OutlineSection] | None = None
    """Call outline, divided into sections (when available and requested)."""

    highlights: list[HighlightSection] | None = None
    """List of highlights of the call (when available and requested)."""

    call_outcome: CallOutcome | None = None
    """Outcome of the call (when available and requested)."""

    key_points: list[KeyPoint] | None = None
    """Key points of the call (when available and requested)."""


# ===== Interaction =====


class SpeakerTalkTime(BaseModel):
    """Talk duration per speaker."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    id: SpeakerID
    """Unique ID of the participant in the call."""

    user_id: UserID | None = None
    """User ID within the Gong system."""

    talk_time: timedelta
    """Talk duration."""


class InteractionStat(BaseModel):
    """Interaction statistic (e.g., Talk Ratio, Longest Monologue)."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    name: str
    """Stat name."""

    value: float
    """Stat measurement."""


class VideoStat(BaseModel):
    """Video segment statistic."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    name: VideoSegmentType
    """Video segment type."""

    duration: timedelta
    """Total video segments duration."""


class QuestionsCounts(BaseModel):
    """Question counts of the call."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    company_count: int
    """Number of questions asked by company speakers."""

    non_company_count: int
    """Number of questions asked by non-company speakers."""


class Interaction(BaseModel):
    """Metrics collected around the interaction during the call."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    speakers: list[SpeakerTalkTime] | None = None
    """Talk duration per speaker."""

    interaction_stats: list[InteractionStat] | None = None
    """Interaction statistics."""

    video: list[VideoStat] | None = None
    """Video statistics about what's presented and for how long."""

    questions: QuestionsCounts | None = None
    """Question counts of the call."""


# ===== Collaboration =====


class PublicComment(BaseModel):
    """A public comment on the call."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    id: CommentID
    """Unique identifier of the comment within Gong."""

    audio_start_time: timedelta | None = None
    """Seconds from the beginning of the call where the comment start refers to."""

    audio_end_time: timedelta | None = None
    """Seconds from the beginning of the call where the comment end refers to."""

    commenter_user_id: UserID
    """User ID of the commenter."""

    comment: str
    """The comment text.
    May contain person tagging in the format @[user name](user Id)."""

    posted: datetime
    """Datetime when the comment was posted (ISO-8601)."""

    in_reply_to: CommentID | None = None
    """Unique ID of the original comment, if this is a reply."""

    during_call: bool | None = None
    """True if the comment was written during the call; False if posted after."""


class Collaboration(BaseModel):
    """Collaboration information added to the call."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    public_comments: list[PublicComment] | None = None
    """List of public comments."""


# ===== Media =====


class Media(BaseModel):
    """Media URLs of the call."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    audio_url: HttpUrl | None = None
    """Audio URL of the call (valid for 8 hours)."""

    video_url: HttpUrl | None = None
    """Video URL of the call (valid for 8 hours)."""


# ===== Call container =====


class CallEntry(BaseModel):
    """One call entry with expanded data."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    meta_data: CallItem
    """Call metadata."""

    context: list[CallContextItem] | None = None
    """List of call-level context entries (links to external systems)."""

    parties: list[Party] | None = None
    """List of the call's participants."""

    content: Content | None = None
    """Analysis of the interaction content."""

    interaction: Interaction | None = None
    """Interaction metrics collected during the call."""

    collaboration: Collaboration | None = None
    """Collaboration information."""

    media: Media | None = None
    """Media URLs for the call."""


# ===== Root response =====


class CallsExpandedResponse(BaseModel):
    """Expanded calls API.

    Contains output with metadata, context, parties, content,
    interaction, collaboration, and media.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    request_id: RequestID
    """A Gong request reference ID generated for this request.
    Use for troubleshooting purposes."""

    records: RecordsInfo
    """Information about the number of records that match the requested filter."""

    calls: list[CallEntry]
    """A list with one entry per call."""


class TranscriptSentence(BaseModel):
    """A single sentence spoken in the monologue."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    start: Milliseconds
    """Start time of the sentence in milliseconds from the start of the call."""

    end: Milliseconds
    """End time of the sentence in milliseconds from the start of the call."""

    text: str
    """The sentence text."""


class TranscriptMonologue(BaseModel):
    """A monologue within the call transcript."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    speaker_id: SpeakerID
    """Unique ID of the speaker
    (cross-reference with `speakerId` in `parties` from `/v2/calls/extensive`)."""

    topic: str | None = None
    """Name of the topic (if applicable)."""

    sentences: list[TranscriptSentence]
    """List of sentences spoken in the monologue."""


class CallTranscriptEntry(BaseModel):
    """Transcript data for a specific call."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    call_id: CallID
    """Gong's unique numeric identifier for the call (up to 20 digits)."""

    transcript: list[TranscriptMonologue]
    """List of monologues for the call."""


class CallTranscriptsResponse(BaseModel):
    """Response containing call transcripts."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_attribute_docstrings=True,
    )

    request_id: RequestID
    """A Gong request reference ID generated for this request.
    Use for troubleshooting."""

    records: RecordsInfo
    """Information about the number of records that match the requested filter."""

    call_transcripts: list[CallTranscriptEntry]
    """A list with one entry per call."""
