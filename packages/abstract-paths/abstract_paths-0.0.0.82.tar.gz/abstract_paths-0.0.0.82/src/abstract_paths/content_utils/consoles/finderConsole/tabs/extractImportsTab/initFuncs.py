

from .functions import (append_log, browse_dir, display_imports, make_params, start_extract)

def initFuncs(self):
    try:
        for f in (append_log, browse_dir, display_imports, make_params, start_extract):
            setattr(self, f.__name__, f)
    except Exception as e:
        logger.info(f"{e}")
    return self
