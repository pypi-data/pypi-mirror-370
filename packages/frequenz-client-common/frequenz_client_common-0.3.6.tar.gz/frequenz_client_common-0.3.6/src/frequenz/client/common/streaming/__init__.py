# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Type wrappers for the generated protobuf messages."""


from enum import Enum

# pylint: disable-next=no-name-in-module
from frequenz.api.common.v1alpha8.streaming import event_pb2 as PBEvent


class Event(Enum):
    """Enum representing the type of streaming event."""

    UNSPECIFIED = PBEvent.EVENT_UNSPECIFIED
    """Unspecified event type."""

    CREATED = PBEvent.EVENT_CREATED
    """Event when a new resource is created."""

    UPDATED = PBEvent.EVENT_UPDATED
    """Event when an existing resource is updated."""

    DELETED = PBEvent.EVENT_DELETED
    """Event when a resource is deleted."""
