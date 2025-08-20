import typing
from typing import Iterable, Mapping, Self

from fabrial import Json, SequenceStep, WidgetDataItem

from .loop_step import LoopStep
from .loop_widget import LoopWidget

NUMBER_OF_LOOPS = "number_of_loops"


class LoopItem(WidgetDataItem):
    """Repeat the nested steps a specified number of times; item."""

    def __init__(self, number_of_loops: int = 2):
        self.loop_widget = LoopWidget(number_of_loops)

    @classmethod
    def deserialize(cls, serialized_obj: Mapping[str, Json]) -> Self:  # implementation
        item = cls(typing.cast(int, serialized_obj[NUMBER_OF_LOOPS]))
        item.loop_widget.handle_value_change()
        return item

    def serialize(self) -> dict[str, Json]:  # implementation
        return {NUMBER_OF_LOOPS: self.loop_widget.loop_count_spinbox.value()}

    def widget(self) -> LoopWidget:  # implementation
        return self.loop_widget

    # implementation
    def create_sequence_step(self, substeps: Iterable[SequenceStep]) -> SequenceStep:
        return LoopStep(self.loop_widget.loop_count_spinbox.value(), substeps)

    def supports_subitems(self) -> bool:  # overridden
        return True
