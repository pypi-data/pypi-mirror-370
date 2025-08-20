import typing
from typing import Mapping, Self

from fabrial import Json, SequenceStep, WidgetDataItem

from .hold_step import HoldStep
from .hold_widget import HoldWidget

HOURS = "hours"
MINUTES = "minutes"
SECONDS = "seconds"


class HoldItem(WidgetDataItem):
    """Hold for a duration; item."""

    def __init__(self, hours: int = 0, minutes: int = 0, seconds: int = 0):
        self.hold_widget = HoldWidget(hours, minutes, seconds)

    @classmethod
    def deserialize(cls, serialized_obj: Mapping[str, Json]) -> Self:  # implementation
        item = cls(
            typing.cast(int, serialized_obj[HOURS]),
            typing.cast(int, serialized_obj[MINUTES]),
            typing.cast(int, serialized_obj[SECONDS]),
        )
        item.hold_widget.handle_value_change()
        return item

    def serialize(self) -> dict[str, Json]:  # implementation
        return {
            HOURS: self.hold_widget.hours_spinbox.value(),
            MINUTES: self.hold_widget.minutes_spinbox.value(),
            SECONDS: self.hold_widget.seconds_spinbox.value(),
        }

    def widget(self) -> HoldWidget:  # implementation
        return self.hold_widget

    # implementation
    def create_sequence_step(self, _) -> SequenceStep:
        return HoldStep(
            self.hold_widget.hours_spinbox.value(),
            self.hold_widget.minutes_spinbox.value(),
            self.hold_widget.seconds_spinbox.value(),
        )
