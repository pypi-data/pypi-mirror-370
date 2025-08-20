from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Literal, Union

from airflow.models import DAG
from pydantic import BaseModel, Field

from .plugins.operators import AnyTask


class DefaultArgs(BaseModel):
    """Default Args Model that will use with the `default_args` field."""

    owner: str | None = None


class DagModel(BaseModel):
    """Base FastDag Model for validate template config data."""

    name: str = Field(description="A DAG name.")
    type: Literal["dag"] = Field(description="A type of template config.")
    docs: str | None = Field(
        default=None,
        description="A DAG document that allow to pass with markdown syntax.",
    )
    params: dict[str, str] = Field(default_factory=dict)
    tasks: list[AnyTask] = Field(
        default_factory=list,
        description="A list of any task, pure task or group task",
    )

    # NOTE: Runtime parameters.
    filename: str | None = Field(default=None)
    parent_dir: Path | None = Field(default=None, description="")
    created_dt: datetime | None = Field(default=None, description="")
    updated_dt: datetime | None = Field(default=None, description="")

    # NOTE: Airflow DAG parameters.
    owner: str = Field(default=None)
    tags: list[str] = Field(default_factory=list, description="A list of tags.")
    schedule: str
    start_date: str | None = Field(default=None)
    end_date: str | None = Field(default=None)
    concurrency: int | None = Field(default=None)
    max_active_runs: int = 1
    dagrun_timeout_sec: int = 600

    def build(
        self,
        prefix: str | None,
        default_args: dict[str, Any] | None = None,
    ) -> DAG:
        """Build Airflow DAG object.

        Args:
            prefix (str | None): A prefix of DAG name.
            default_args: (dict[str, Any]):
        """
        name: str = f"{prefix}_{self.name}" if prefix else self.name
        dag = DAG(
            dag_id=name,
            tags=self.tags,
            schedule=self.schedule,
            start_date=self.start_date,
            end_date=self.end_date,
            concurrency=self.concurrency,
            max_active_runs=self.max_active_runs,
            dagrun_timeout=timedelta(seconds=self.dagrun_timeout_sec),
            default_args={"owner": self.owner, **(default_args or {})},
        )
        return dag


Primitive = Union[str, int, float, bool]
ValueType = Union[Primitive, list[Primitive], dict[Union[str, int], Primitive]]


class Key(BaseModel):
    key: str
    stages: dict[str, dict[str, ValueType]] = Field(
        default=dict,
        description="A stage mapping with environment and its pair of variable",
    )


class Variable(BaseModel):
    type: Literal["variable"]
    variables: list[Key] = Field(description="A list of Key model.")
