

from .functions import (_ask_user_to_pick_file, _is_header_line, apply_custom_diff, apply_diff_to_directory, browse_dir, getPaths, get_files_and_dirs, make_list, make_params, parse_unified_diff, preview_patch, read_any_file, save_patch, set_status, write_to_file)

def initFuncs(self):
    try:
        for f in (_ask_user_to_pick_file, _is_header_line, apply_custom_diff, apply_diff_to_directory, browse_dir, getPaths, get_files_and_dirs, make_list, make_params, parse_unified_diff, preview_patch, read_any_file, save_patch, set_status, write_to_file):
            setattr(self, f.__name__, f)
    except Exception as e:
        logger.info(f"{e}")
    return self
