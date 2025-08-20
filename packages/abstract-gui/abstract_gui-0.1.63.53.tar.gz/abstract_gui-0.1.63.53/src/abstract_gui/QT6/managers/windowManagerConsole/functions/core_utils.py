from ..imports import *
# ---------------- core actions ----------------
def refresh(self) -> None:
    self.get_windows()
    self.update_table()
    self.update_monitor_dropdown()
    self.statusBar().showMessage("Refreshed", 2500)

def _selected_rows(self) -> List[Tuple[str, str, str, str, str]]:
    sel = []
    for idx in self.table.selectionModel().selectedRows():
        data = self.table.item(idx.row(), 0).data(Qt.UserRole)
        if data:
            sel.append(data)
    return sel

def select_all_by_type(self) -> None:
    t_req = self.type_combo.currentText()
    if t_req == "All":
        self.table.selectAll(); return
    self.table.clearSelection()
    for r in range(self.table.rowCount()):
        if self.table.item(r, 4).text() == t_req:
            self.table.selectRow(r)

def move_window(self) -> None:
    sel = self._selected_rows();
    if not sel:
        return
    tgt = self.monitor_combo.currentText()
    for win_id, *_ in sel:
        for name, x, y, *_ in self.monitors:
            if name == tgt:
                self.run_command(f"wmctrl -i -r {win_id} -e 0,{x},{y},-1,-1")
    self.refresh()

def control_window(self, act: str) -> None:
    sel = self._selected_rows();
    if not sel:
        return
    for win_id, *_ in sel:
        if act == "minimize":
            self.run_command(f"xdotool windowminimize {win_id}")
        elif act == "maximize":
            self.run_command(f"wmctrl -i -r {win_id} -b add,maximized_vert,maximized_horz")
    self.refresh()

def close_selected(self, include_unsaved: bool) -> None:
    sel = self._selected_rows();
    if not sel:
        return
    skip, to_close = [], []
    for data in sel:
        win_id, _, title, *_ = data
        if looks_unsaved(title) and not include_unsaved:
            skip.append(title); continue
        to_close.append((win_id, title))
    if not to_close:
        QMessageBox.information(self, "Nothing to close", "No saved windows selected."); return
    if any(looks_unsaved(t) for _, t in to_close):
        if QMessageBox.question(self, "Unsaved?", "Some look unsaved – close anyway?", QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
    for win_id, _ in to_close:
        self.run_command(f"xdotool windowclose {win_id}")
    msg = f"Closed {len(to_close)} window(s)" + (" (skipped unsaved)" if skip else "")
    self.statusBar().showMessage(msg, 4000)
    self.refresh()

def activate_window(self, item) -> None:
    data = item.data(Qt.UserRole)
    if data:
        self.run_command(f"xdotool windowactivate {data[0]}")
