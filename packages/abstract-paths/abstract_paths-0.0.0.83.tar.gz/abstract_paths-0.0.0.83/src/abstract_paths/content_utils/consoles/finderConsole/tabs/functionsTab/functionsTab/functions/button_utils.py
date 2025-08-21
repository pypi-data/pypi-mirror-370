from ..imports import *
# ---- internals --------------------------------------------------------
def _add_fn_button(self, name: str):
    btn = QPushButton(name)
    btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    btn.clicked.connect(lambda _, n=name: self._on_function_clicked(n))
    # FlowLayout supports addWidget; QVBoxLayout does too
    self.fn_layout.addWidget(btn)

def _clear_fn_buttons(self):
    while self.fn_layout.count():
        it = self.fn_layout.takeAt(0)
        w = it.widget()
        if w: w.deleteLater()

def _rebuild_fn_buttons(self, names_iterable):
    self._clear_fn_buttons()
    names = sorted(n for n in names_iterable if n and n != '<reexport>')
    for name in names:
        self._add_fn_button(name)

def _filter_fn_buttons(self, text: str):
    t = (text or '').strip().lower()
    if not self.func_map:
        return
    if not t:
        self._rebuild_fn_buttons(self.func_map.keys())
    else:
        match = [n for n in self.func_map.keys() if t in n.lower()]
        self._rebuild_fn_buttons(match)
def create_radio_group(self, labels, default_index=0, slot=None):
        """
        Create a QButtonGroup with QRadioButtons for the given labels.

        Args:
            self: parent widget (e.g. 'self' inside a class)
            labels (list[str]): button labels
            default_index (int): which button to check by default
            slot (callable): function to connect all toggled signals to
        Returns:
            (QButtonGroup, list[QRadioButton])
        """
        group = QButtonGroup(self)
        buttons = []

        for i, label in enumerate(labels):
            rb = QRadioButton(label)
            if i == default_index:
                rb.setChecked(True)
            group.addButton(rb)
            buttons.append(rb)
            if slot:
                rb.toggled.connect(slot)

        return group, buttons
