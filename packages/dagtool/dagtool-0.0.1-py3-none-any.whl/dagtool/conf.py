import logging
from pathlib import Path
from typing import Any

from pydantic import ValidationError
from yaml import safe_load

from .const import VARIABLE_FILENAME
from .models import DagModel


class YamlConf:
    """Core Config object that use to find and map data from the current path.

    ClassAttributes:
        config_filename (str):
        variable_filename (str):
        assert_dir (str):
    """

    def __init__(self, path: Path) -> None:
        self.path: Path = path

    def variable(self, stage: str) -> dict[str, Any]:
        """Get Variable value with an input stage name."""
        search_files: list[Path] = list(
            self.path.rglob(f"{VARIABLE_FILENAME}.*")
        )
        if not search_files:
            return {}
        return safe_load(search_files[0].open(mode="rt")).get(stage, {})

    def read_conf(self) -> list[DagModel]:
        """Read config from the path argument and reload to the conf."""
        conf: list[DagModel] = []
        for file in self.path.rglob("*"):
            if (
                file.is_file()
                and file.stem != VARIABLE_FILENAME
                and file.suffix in (".yml", ".yaml")
            ):
                data: dict[str, Any] | list[Any] = safe_load(
                    file.open(mode="rt")
                )

                # VALIDATE: Does not support for list of template config.
                if isinstance(data, list):
                    continue

                try:
                    if data.get("type", "NOTSET") != "dag":
                        continue
                    file_stats = file.stat()
                    model = DagModel.model_validate(
                        {
                            "filename": file.name,
                            "parent_dir": file.parent,
                            "created_dt": file_stats.st_ctime,
                            "updated_dt": file_stats.st_mtime,
                            **data,
                        }
                    )
                    logging.info(f"Load DAG: {model.name!r}")
                    conf.append(model)
                except AttributeError:
                    # NOTE: Except case data is not be `dict` type.
                    continue
                except ValidationError as e:
                    # NOTE: Raise because model cannot validate with model.
                    logging.error(
                        f"Template data cannot pass to DagTool model:\n{e}"
                    )
                    continue

        if len(conf) == 0:
            logging.warning(
                "Read config file from this domain path does not exists"
            )
        return conf
