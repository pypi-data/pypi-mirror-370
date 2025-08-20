"""# Stock DAGs

This is the stock domain DAG.
"""

import logging

from dagtool import DagTool
from dagtool.plugins.templates.filters import unnested_list

logger = logging.getLogger("dagtool.dag.stock")


dag = DagTool(
    name="stock",
    path=__file__,
    docs=__doc__,
    operators={},
    user_defined_filters={"unnested_list": unnested_list},
    user_defined_macros={},
)
logger.info(f"Start Generate: {dag.name}")
dag.build_to_globals(
    gb=globals(),
    default_args={},
)
