

from .functions import (append_log, browse_dir, display_map, make_params, start_map)

def initFuncs(self):
    try:
        for f in (append_log, browse_dir, display_map, make_params, start_map):
            setattr(self, f.__name__, f)
    except Exception as e:
        logger.info(f"{e}")
    return self
