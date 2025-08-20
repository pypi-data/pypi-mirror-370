from ..imports import *
def _on_filter_mode_changed(self):
    self.fn_filter_mode = "source" if self.rb_fn_source.isChecked() else ("all" if self.rb_fn_all.isChecked() else "io")
    if self.current_fn:
        self._render_fn_lists_for(self.current_fn)

def _render_fn_lists_for(self, fn_name: str):
    self.exporters_list.clear()
    self.importers_list.clear()
    data = self.func_map.get(fn_name, {'exported_in': [], 'imported_in': []})

    exported_in, imported_in = [], []
    if isinstance(data, dict):
        exported_in = list(dict.fromkeys(data.get('exported_in', [])))
        imported_in = list(dict.fromkeys(data.get('imported_in', [])))
    elif isinstance(data, list):
        for d in data:
            if isinstance(d, dict):
                exported_in += d.get('exported_in', [])
                imported_in += d.get('imported_in', [])
            elif isinstance(d, str):
                exported_in.append(d); imported_in.append(d)
        exported_in = list(dict.fromkeys(exported_in))
        imported_in = list(dict.fromkeys(imported_in))

    mode = self.fn_filter_mode
    if mode == "source":
        for f in sorted(exported_in): self.exporters_list.addItem(f)
    elif mode == "io":
        for f in sorted(exported_in): self.exporters_list.addItem(f)
        for f in sorted(imported_in): self.importers_list.addItem(f)
    else:  # all
        union = sorted(set(exported_in) | set(imported_in))
        for f in union: self.exporters_list.addItem(f)


def _on_map_ready(self, graph: dict, func_map: dict):
        self.graph = graph or {}
        self.func_map = func_map or {}
        self.func_console.setData(self.func_map)
