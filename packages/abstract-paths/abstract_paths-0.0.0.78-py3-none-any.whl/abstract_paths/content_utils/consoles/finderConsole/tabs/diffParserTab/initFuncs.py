

from .functions import (browse_file, preview_patch, save_patch)

def initFuncs(self):
    try:
        for f in (browse_file, preview_patch, save_patch):
            setattr(self, f.__name__, f)
    except Exception as e:
        logger.info(f"{e}")
    return self
