from typing import Iterable, Self

from fabrial import Json, SequenceStep, WidgetDataItem

from .simultaneous_step import SimultaneousStep
from .simultaneous_widget import SimultaneousWidget


class SimultaneousItem(WidgetDataItem):
    """Run the nested items at the same time; item."""

    def __init__(self):
        self.simultaneous_widget = SimultaneousWidget()

    @classmethod
    def deserialize(cls, _) -> Self:  # implementation
        return cls()

    def serialize(self) -> dict[str, Json]:  # implementation
        return {}

    def widget(self) -> SimultaneousWidget:  # implementation
        return self.simultaneous_widget

    # implementation
    def create_sequence_step(self, substeps: Iterable[SequenceStep]) -> SequenceStep:
        return SimultaneousStep(substeps)

    def supports_subitems(self) -> bool:  # overridden
        return True
