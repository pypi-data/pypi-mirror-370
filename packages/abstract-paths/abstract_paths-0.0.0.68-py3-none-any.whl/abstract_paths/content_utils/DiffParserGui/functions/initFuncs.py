from .mainFuncs import *
def initFuncs(self):
    try:
        self.set_search_params = set_search_params
        self.browse_file = browse_file
        self.preview_patch = preview_patch
        self.save_patch = save_patch
        return self
    except Exception as e:
        logger.info(f"Approve save: {e}")
