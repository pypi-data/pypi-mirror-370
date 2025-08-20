from ...imports import *

def getRunner(self,layout=None):

    runner_page = QWidget()
    runner_layout = layout or QVBoxLayout(runner_page)
    top = QHBoxLayout()
    top.addWidget(QLabel("User:"))
    top.addWidget(self.user_in, 2)
    top.addWidget(QLabel("Path:"))
    top.addWidget(self.path_in, 3)
    top.addWidget(self.run_btn)
    top.addWidget(self.rerun_btn)
    top.addWidget(self.clear_btn)
    layout.addLayout(top)


    top = QHBoxLayout()
    top.addWidget(QLabel("User:"))
    top.addWidget(self.user_in, 2)
    top.addWidget(QLabel("Path:"))
    top.addWidget(self.path_in, 3)
    top.addWidget(self.run_btn)
    top.addWidget(self.rerun_btn)
    top.addWidget(self.clear_btn)
    layout.addLayout(top)


    filter_row = QHBoxLayout()
    filter_row.addWidget(QLabel("Log Output:"))
    filter_row.addStretch(1)
    filter_row.addWidget(self.rb_all)
    filter_row.addWidget(self.rb_err)
    filter_row.addWidget(self.rb_wrn)
    filter_row.addWidget(self.cb_try_alt_ext)
    runner_layout.addLayout(filter_row)

    layout.addWidget(self.log_view, 3)

    left  = getListBox((self.errors_list,   "Errors (file:line:col):", 1))
    right = getListBox((self.warnings_list, "Warnings (file:line:col):", 1))
    lists_row = getRow(left, right)
    layout.addLayout(lists_row, 2)

    tabs.addTab(runner_page, "Runner")
