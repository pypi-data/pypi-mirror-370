from typing import Any

from .filters import unnested_list

PLUGINS_FILTERS: dict[str, Any] = {
    "unnested_list": unnested_list,
}
