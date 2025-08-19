from datetime import datetime
import re
from typing import Optional, Union

from nemo_library.adapter.hubspot.model.call_activity import CallActivity
from nemo_library.adapter.hubspot.model.communication_activity import (
    CommunicationActivity,
)
from nemo_library.adapter.hubspot.model.email_activity import EmailActivity
from nemo_library.adapter.hubspot.model.feedbacksubmission_activity import (
    FeedbacksubmissionActivity,
)
from nemo_library.adapter.hubspot.model.meeting_activity import MeetingActivity
from nemo_library.adapter.hubspot.model.note_activity import NoteActivity
from nemo_library.adapter.hubspot.model.postalmail_activity import PostalMailActivity
from nemo_library.adapter.hubspot.model.task_activity import TaskActivity
from nemo_library.adapter.hubspot.model.tax_activity import TaxActivity

PATTERN_DATETIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
PATTERN_DATETIME_MS = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")

ACTIVITY_TYPES = {
    "calls": CallActivity,
    "communications": CommunicationActivity,
    "emails": EmailActivity,
    "feedback_submissions": FeedbacksubmissionActivity,
    "meetings": MeetingActivity,
    "notes": NoteActivity,
    "postal_mail": PostalMailActivity,
    "tasks": TaskActivity,
    "taxes": TaxActivity,
}

ACTIVITY_TYPE_DETAILS = {
    "calls": [
        "hubspot_owner_id",
        "hs_call_body",
        "hs_call_direction",
        "hs_call_duration",
        "hs_call_status",
        "hs_call_title",
    ],
    "communications": [
        "hubspot_owner_id",
        "hs_communication_body",
        "hs_communication_channel_type",
    ],
    "emails": [
        "hubspot_owner_id",
        "hs_email_text",
        "hs_email_subject",
        "hs_email_status",
        "hs_email_direction",
    ],
    "feedback_submissions": ["hubspot_owner_id", "hs_feedback_submission_body"],
    "meetings": [
        "hubspot_owner_id",
        "hs_meeting_title",
        "hs_meeting_body",
        "hs_internal_meeting_notes",
        "hs_meeting_location",
        "hs_meeting_start_time",
        "hs_meeting_end_time",
        "hs_meeting_outcome",
    ],
    "notes": ["hubspot_owner_id", "hs_note_body"],
    "postal_mail": ["hubspot_owner_id", "hs_postal_mail_body"],
    "tasks": [
        "hubspot_owner_id",
        "hs_task_body",
        "hs_task_status",
        "hs_task_priority",
        "hs_task_subject",
        "hs_task_type",
    ],
    "taxes": ["hs_tax_body", "hubspot_owner_id"],
}

DEALSTAGE_MAPPING = {
    "appointmentscheduled": "Unqualified lead​",
    "17193482": "Qualified lead",
    "16072556": "Presentation",
    "presentationscheduled": "Test phase",
    "decisionmakerboughtin": "Negotiation",
    "contractsent": "Commit",
    "closedwon": "closed and won",
    "closedlost": "closed and lost",
}


def parse_datetime(value: Optional[Union[str, datetime]]) -> Optional[datetime]:
    """Parses a datetime string or returns datetime directly."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        try:
            if PATTERN_DATETIME.fullmatch(value):
                return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
            elif PATTERN_DATETIME_MS.fullmatch(value):
                return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
            else:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except Exception:
            return None
    return None


# Serialize datetime objects to ISO 8601 strings
def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")
