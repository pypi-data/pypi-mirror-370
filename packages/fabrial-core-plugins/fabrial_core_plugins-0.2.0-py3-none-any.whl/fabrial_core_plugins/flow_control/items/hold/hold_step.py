from pathlib import Path
from typing import Any

from fabrial import SequenceStep, StepRunner

from .hold_widget import BASE_DISPLAY_NAME


class HoldStep(SequenceStep):
    """Hold for a duration; step."""

    def __init__(self, hours: int, minutes: int, seconds: int):
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds

    async def run(self, runner: StepRunner, data_directory: Path):  # implementation
        await self.sleep(self.hours * 3600 + self.minutes * 60 + self.seconds)  # lmao it's so easy

    def reset(self):  # implementation
        return  # nothing to do here

    def name(self) -> str:  # implementation
        return BASE_DISPLAY_NAME

    def metadata(self) -> dict[str, Any]:  # overridden
        return {
            "Selected Hours": self.hours,
            "Selected Minutes": self.minutes,
            "Selected Seconds": self.seconds,
        }
