from pathlib import Path

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QFormLayout

from fabrial import ItemWidget, TextDescription
from fabrial.custom_widgets import SpinBox

BASE_DISPLAY_NAME = "Loop"
ICON = QIcon(str(Path(__file__).parent.joinpath("arrow-repeat.png")))
LOOP_COUNT_LABEL = "Number of Loops"


class LoopWidget(ItemWidget):
    """Repeat the nested steps a specified number of times; widget."""

    def __init__(self, number_of_loops: int):
        layout = QFormLayout()
        ItemWidget.__init__(
            self,
            layout,
            BASE_DISPLAY_NAME,
            ICON,
            TextDescription(
                BASE_DISPLAY_NAME,
                "Repeat the nested steps a specified number of times.",
                {LOOP_COUNT_LABEL: "The number of times to repeat the nested steps."},
                {
                    "[X]": "Where **[X]** is a numbered directory for "
                    "each loop that contains data for the nested steps."
                },
            ),
        )

        self.loop_count_spinbox = SpinBox(2, initial_value=number_of_loops)
        layout.addRow(LOOP_COUNT_LABEL, self.loop_count_spinbox)
        self.loop_count_spinbox.editingFinished.connect(self.handle_value_change)

    def handle_value_change(self):  # used externally
        """Handle the loop count changing."""
        self.setWindowTitle(f"{BASE_DISPLAY_NAME} ({self.loop_count_spinbox.text()})")
