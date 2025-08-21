"""
Standardized signals definitions for events within the architecture subdomain ``analytics``.

All signals defined in this module must follow the name and versioning
conventions specified in OEP-41.

They also must comply with the payload definition specified in
docs/decisions/0003-events-payload.rst
"""

from openedx_events.analytics.data import TrackingLogData
from openedx_events.tooling import OpenEdxPublicSignal

# .. event_type: org.openedx.analytics.tracking.event.emitted.v1
# .. event_name: TRACKING_EVENT_EMITTED
# .. event_key_field: tracking_log.name
# .. event_description: Emitted when a tracking log event is emitted.
# .. event_data: TrackingLogData
# .. event_trigger_repository: openedx/event-tracking
TRACKING_EVENT_EMITTED = OpenEdxPublicSignal(
    event_type="org.openedx.analytics.tracking.event.emitted.v1",
    data={
        "tracking_log": TrackingLogData,
    }
)
