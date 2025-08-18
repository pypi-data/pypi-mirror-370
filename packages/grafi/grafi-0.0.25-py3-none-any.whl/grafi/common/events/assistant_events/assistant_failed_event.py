from typing import Any
from typing import Dict

from grafi.common.events.assistant_events.assistant_event import AssistantEvent
from grafi.common.events.event import EventType
from grafi.common.events.topic_events.publish_to_topic_event import PublishToTopicEvent


class AssistantFailedEvent(AssistantEvent):
    event_type: EventType = EventType.ASSISTANT_FAILED
    input_event: PublishToTopicEvent
    error: Any

    def to_dict(self) -> Dict[str, Any]:
        return {
            **self.assistant_event_dict(),
            "data": {
                "input_event": self.input_event.to_dict(),
                "error": self.error,
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AssistantFailedEvent":
        base_event = cls.assistant_event_base(data)
        return cls(
            **base_event.model_dump(),
            input_event=PublishToTopicEvent.from_dict(data["data"]["input_event"]),
            error=data["data"]["error"],
        )
