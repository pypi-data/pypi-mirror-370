

from .functions import (_add_fn_button, _build_ui, _clear_fn_buttons, _filter_fn_buttons, _on_filter_mode_changed, _on_function_clicked, _on_map_ready, _rebuild_fn_buttons, _render_fn_lists_for, _start_func_scan, appendLog, create_radio_group)

def initFuncs(self):
    try:
        for f in (_add_fn_button, _build_ui, _clear_fn_buttons, _filter_fn_buttons, _on_filter_mode_changed, _on_function_clicked, _on_map_ready, _rebuild_fn_buttons, _render_fn_lists_for, _start_func_scan, appendLog, create_radio_group):
            setattr(self, f.__name__, f)
    except Exception as e:
        logger.info(f"{e}")
    return self
