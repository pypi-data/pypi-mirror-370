from asyncio import TaskGroup
from pathlib import Path
from typing import Iterable

from fabrial import SequenceStep, StepRunner

from .simultaneous_widget import NAME


class SimultaneousStep(SequenceStep):
    """Run the nested items at the same time; step."""

    def __init__(self, steps: Iterable[SequenceStep]):
        self.steps = steps

    async def run(self, runner: StepRunner, data_directory: Path):  # implementation
        async with TaskGroup() as task_group:
            for i, step in enumerate(self.steps):
                task_group.create_task(runner.run_single_step(step, data_directory, i + 1))
        # all tasks in the task group are run when the context manager ends

    def reset(self):  # implementation
        for step in self.steps:
            step.reset()

    def name(self) -> str:  # implementation
        return NAME
