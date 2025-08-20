from .functions import *
def set_search_params(self, params):  # ← IDE will call this
    try:
        """params is your FinderTab SearchParams (directory + filters)."""
        self._params = params
        # reflect directory in the input for clarity:
        if getattr(params, "directory", None):
            self.file_in.setText(params.directory)
    except Exception as e:
        logger.info(f"set_search_params: {e}")
def browse_file(self):
    try:
        # pick a project root directory
        d = QFileDialog.getExistingDirectory(self, "Select Project Root")
        if d:
            self.file_in.setText(d)
    except Exception as e:
        logger.info(f"browse_file: {e}")
def preview_patch(self):
    # Prefer FinderTab-provided params if present
    try:
        p = getattr(self, "_params", None)

        root = (p.directory if p and getattr(p, "directory", None) else self.file_in.text().strip())
        if not root or not os.path.isdir(root):
            QMessageBox.critical(self, "Error", "Invalid project root.")
            return

        diff = self.diff_text.toPlainText().strip()
        if not diff:
            QMessageBox.critical(self, "Error", "No diff provided.")
            return

        # Gather filters from SearchParams if available, else fall back to simple defaults
        kwargs = {}
        if p:
            kwargs = dict(
                allowed_exts=p.allowed_exts,
                unallowed_exts=p.unallowed_exts,
                exclude_types=p.exclude_types,
                exclude_dirs=p.exclude_dirs,
                exclude_patterns=p.exclude_patterns,
                add=p.add,
                recursive=p.recursive,
            )
        else:
            kwargs = dict(exclude_dirs=["node_modules", "__pycache__"])
    except Exception as e:
        logger.info(f"Error: {e!r}")#QMessageBox.critical(self, "Prefer FinderTab-provided params if present", f"{e!r}")
    try:
        previews = plan_previews(
            diff,
            directory=root,
            **kwargs,  # ← pass Finder filters through
        )
        if not previews:
            QMessageBox.information(self, "No Matches", "No targets found for this diff.")
            self.preview.clear()
            self._previews = {}
            return

        # stash for save
        self._previews = previews

        # render a simple multi-file preview
        chunks: List[str] = []
        for fp in sorted(previews.keys()):
            chunks.append(f"=== {fp} ===")
            chunks.append(previews[fp])
        self.preview.setPlainText("\n".join(chunks))

    except Exception as e:
        logger.info(f"Error: {e!r}")#QMessageBox.critical(self, "Error", f"{e!r}")

def save_patch(self):
    if not hasattr(self, "_previews") or not self._previews:
        QMessageBox.warning(self, "Warning", "Nothing to save. Generate a preview first.")
        return
    changed = 0
    try:
        for fp, text in self._previews.items():
            # one-time backup per file
            bak = fp + ".bak"
            if not os.path.exists(bak):
                try: shutil.copyfile(fp, bak)
                except Exception: pass
            write_text_atomic(fp, text if text.endswith("\n") else text + "\n")
            changed += 1
        QMessageBox.information(self, "Success", f"Saved {changed} file(s).")
    except Exception as e:
        logger.info(f"Error: {e!r}")#QMessageBox.critical(self, "Error", f"Failed to save: {e!r}")
