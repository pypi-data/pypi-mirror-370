from typing import Literal

from airflow.models import DAG, Operator
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from pydantic import Field

from .__abc import OperatorTask


class EmptyTask(OperatorTask):
    """Empty Task model."""

    op: Literal["empty"]

    def build(self, dag: DAG | None = None, **kwargs) -> Operator:
        return EmptyOperator(task_id=self.task, dag=dag)


class PythonTask(OperatorTask):
    op: Literal["python"]

    def build(self, **kwargs): ...


class BashTask(OperatorTask):
    """Bash Task model that will represent to Airflow BashOperator object."""

    op: Literal["bash"] = Field(description="An operator type for bash model.")
    bash_command: str = Field(description="A bash command or bash file")
    env: dict[str, str] | None = None
    append_env: bool = False
    output_encoding: str = "utf-8"
    skip_on_exit_code: int | list[int] | None = None
    cwd: str | None = None

    def build(self, dag: DAG | None = None, **kwargs) -> Operator:
        return BashOperator(
            task_id=self.task,
            bash_command=self.bash_command,
            dag=dag,
        )


class SparkTask(OperatorTask):
    op: Literal["spark"]

    def build(self, **kwargs): ...


class DockerTask(OperatorTask):
    op: Literal["docker"]

    def build(self, **kwargs): ...
