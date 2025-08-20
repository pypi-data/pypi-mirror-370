from abc import ABC, abstractmethod
from typing import Any

from airflow.models import Operator
from pydantic import BaseModel, Field, field_validator


class BaseTask(BaseModel, ABC):
    """Base Task model that represent Airflow Task object."""

    upstream: list[str] | None = Field(
        default=None,
        description=(
            "A list of upstream task name or only task name of this task."
        ),
    )

    @field_validator(
        "upstream",
        mode="before",
        json_schema_input_type=str | list[str] | None,
    )
    def __prepare_upstream(cls, data: Any) -> Any:
        """Prepare upstream value that passing to validate with string value
        instead of list of string. This function will create list of this value.
        """
        if data and isinstance(data, str):
            return [data]
        return data

    @abstractmethod
    def build(self, **kwargs) -> Any:
        """Build"""


class OperatorTask(BaseTask, ABC):
    task: str = Field(description="A task name.")
    op: str = Field(description="An operator type of this task.")

    @abstractmethod
    def build(self, **kwargs) -> Operator:
        """Build the Airflow Operator object from this model fields."""
