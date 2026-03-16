from .muapi_nodes import (
    NODE_CLASS_MAPPINGS as _N,
    NODE_DISPLAY_NAME_MAPPINGS as _D,
)
from .muapi_video_saver_node import (
    NODE_CLASS_MAPPINGS as _SN,
    NODE_DISPLAY_NAME_MAPPINGS as _SD,
)

NODE_CLASS_MAPPINGS = {**_N, **_SN}
NODE_DISPLAY_NAME_MAPPINGS = {**_D, **_SD}
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
