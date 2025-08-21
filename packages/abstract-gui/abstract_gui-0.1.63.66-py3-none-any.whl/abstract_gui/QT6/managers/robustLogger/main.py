        # Output area
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Log Output:")); filter_row.addStretch(1)
        filter_row.addWidget(self.rb_all); filter_row.addWidget(self.rb_err); filter_row.addWidget(self.rb_wrn)
        filter_row.addWidget(self.cb_try_alt_ext)
        root.addLayout(filter_row)
        attach_textedit_to_logs(self.log, tail_file=get_log_file_path())
