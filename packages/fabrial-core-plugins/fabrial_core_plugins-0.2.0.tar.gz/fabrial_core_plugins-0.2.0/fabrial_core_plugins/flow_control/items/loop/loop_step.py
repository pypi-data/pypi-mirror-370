from pathlib import Path
from typing import Any, Iterable

from fabrial import SequenceStep, StepRunner

from .loop_widget import BASE_DISPLAY_NAME


class LoopStep(SequenceStep):
    """Repeat the nested steps a specified number of times; step."""

    def __init__(self, number_of_loops: int, steps: Iterable[SequenceStep]):
        self.number_of_loops = number_of_loops
        self.steps = steps

    async def run(self, runner: StepRunner, data_directory: Path):  # implementation
        # number of loops is guaranteed to be at least 2
        for i in range(1, self.number_of_loops):
            await self.run_one_loop(runner, data_directory, i)
            self.reset()  # reset after each loop
        # except the last loop
        await self.run_one_loop(runner, data_directory, i + 1)

    async def run_one_loop(self, runner: StepRunner, data_directory: Path, count: int):
        """Run the loop's steps sequentially once."""
        await runner.run_steps(self.steps, data_directory.joinpath(str(count)))

    def reset(self):  # implementation
        for step in self.steps:
            step.reset()

    def name(self) -> str:  # implementation
        return BASE_DISPLAY_NAME

    def metadata(self) -> dict[str, Any]:  # overridden
        return {"Selected Number of Loops": self.number_of_loops}
