from typing import Annotated, Union

from airflow.utils.task_group import TaskGroup
from pydantic import Field

from .__abc import BaseTask
from .base import (
    BashTask,
    DockerTask,
    EmptyTask,
    PythonTask,
    SparkTask,
)

Task = Annotated[
    Union[
        EmptyTask,
        PythonTask,
        BashTask,
        SparkTask,
        DockerTask,
    ],
    Field(discriminator="op"),
]


class GroupTask(BaseTask):
    """Group of Task model that will represent Airflow Group Task object."""

    group: str = Field(description="A task group name.")
    tasks: list["AnyTask"] = Field(
        default_factory=list,
        description="A list of Any Task model.",
    )

    def build(self) -> TaskGroup:
        with TaskGroup(group_id=self.group) as tg:
            pass

        return tg


AnyTask = Annotated[
    Union[
        Task,
        GroupTask,
    ],
    Field(union_mode="smart"),
]
