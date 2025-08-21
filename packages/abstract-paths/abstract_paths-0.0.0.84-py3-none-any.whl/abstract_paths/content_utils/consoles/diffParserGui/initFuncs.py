
from ..imports import *
from .functions import (_find_block, _find_block_tolerant, _norm_line, apply_custom_diff, apply_diff_to_directory, browse_dir, getPaths, get_files_and_dirs, make_list, make_params, parse_diff_text, parse_unified_diff, preview_patch, read_any_file, save_patch, write_to_file)

def initFuncs(self):
    try:
        for f in (_find_block, _find_block_tolerant, _norm_line, apply_custom_diff, apply_diff_to_directory, browse_dir, getPaths, get_files_and_dirs, make_list, make_params, parse_diff_text, parse_unified_diff, preview_patch, read_any_file, save_patch, write_to_file):
            setattr(self, f.__name__, f)
    except Exception as e:
        logger.info(f"{e}")
    return self
