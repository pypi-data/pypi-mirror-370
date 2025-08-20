from enum import Enum


class ScheduleType(str, Enum):
    COMMAND = "command"
    RUN_WORKFLOW = "run-workflow"
    GENERATE_INSIGHTS = "generate-insights"

    def __str__(self) -> str:
        return str(self.value)
