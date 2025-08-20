from __future__ import annotations
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
    Iterator,
)
from uuid import uuid4
from dataclasses import dataclass

from .models import Attachment, PartialTrackAIEvent
from . import analytics as _core
from opentelemetry import context as context_api


class Interaction:
    """
    Thin helper returned by analytics.begin().
    Each mutator just relays a partial update back to Analytics.
    """

    __slots__ = (
        "_event_id",
        "_analytics",
        "__weakref__",
    )

    def __init__(
        self,
        event_id: Optional[str] = None,
    ):
        self._event_id = event_id or str(uuid4())
        self._analytics = _core

    # -- mutators ----------------------------------------------------------- #
    def set_input(self, text: str) -> None:
        self._analytics._track_ai_partial(
            PartialTrackAIEvent(event_id=self._event_id, ai_data={"input": text})
        )

    def add_attachments(self, attachments: List[Attachment]) -> None:
        self._analytics._track_ai_partial(
            PartialTrackAIEvent(event_id=self._event_id, attachments=attachments)
        )

    def set_properties(self, props: Dict[str, Any]) -> None:
        self._analytics._track_ai_partial(
            PartialTrackAIEvent(event_id=self._event_id, properties=props)
        )

    def set_property(self, key: str, value: Any) -> None:
        self.set_properties({key: value})

    def finish(self, *, output: str | None = None, **extra) -> None:

        payload = PartialTrackAIEvent(
            event_id=self._event_id,
            ai_data={"output": output} if output is not None else None,
            is_pending=False,
            **extra,
        )
        self._analytics._track_ai_partial(payload)

    # convenience
    @property
    def id(self) -> str:
        return self._event_id
