

from .functions import (append_log, browse_dir, make_params, open_all_hits, open_one, populate_results, start_collect)

def initFuncs(self):
    try:
        for f in (append_log, browse_dir, make_params, open_all_hits, open_one, populate_results, start_collect):
            setattr(self, f.__name__, f)
    except Exception as e:
        logger.info(f"{e}")
    return self
