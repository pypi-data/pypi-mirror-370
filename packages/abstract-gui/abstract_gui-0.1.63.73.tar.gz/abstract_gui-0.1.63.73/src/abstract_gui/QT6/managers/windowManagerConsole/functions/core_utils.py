from ..imports import *
from PyQt6.QtWidgets import QMessageBox
SB = QMessageBox.StandardButton  # alias for brevity

# ---------------- core actions ----------------

def refresh(self) -> None:
    self._compute_self_ids()
    self.get_windows()
    self.update_table()
    self.update_monitor_dropdown()
    self.statusBar().showMessage("Refreshed", 2500)

def _selected_rows(self) -> List[Tuple[str, str, str, str, str]]:
    sel: List[Tuple[str, str, str, str, str]] = []
    model = self.table.selectionModel()
    if not model:
        return sel
    for idx in model.selectedRows():
        it = self.table.item(idx.row(), 0)
        if not it:
            continue
        data = it.data(Qt.ItemDataRole.UserRole)   # Qt6 enum
        if data:
            sel.append(data)
    return sel

def select_all_by_type(self) -> None:
    t_req = self.type_combo.currentText()
    if t_req == "All":
        self.table.selectAll()
        return
    self.table.clearSelection()
    for r in range(self.table.rowCount()):
        if self.table.item(r, 4).text() == t_req:
            self.table.selectRow(r)

def move_window(self) -> None:
    sel = self._selected_rows()
    if not sel:
        return
    tgt = self.monitor_combo.currentText()
    for win_id, *_ in sel:
        for name, x, y, *_ in self.monitors:
            if name == tgt:
                self.run_command(f"wmctrl -i -r {win_id} -e 0,{x},{y},-1,-1")
    self.refresh()

def control_window(self, act: str) -> None:
    sel = self._selected_rows()
    if not sel:
        return
    for win_id, *_ in sel:
        if act == "minimize":
            self.run_command(f"xdotool windowminimize {win_id}")
        elif act == "maximize":
            self.run_command(f"wmctrl -i -r {win_id} -b add,maximized_vert,maximized_horz")
    self.refresh()

def close_selected(self, include_unsaved: bool) -> None:
    sel = self._selected_rows()
    if not sel:
        return

    self_pid = getattr(self, "_self_pid", None)
    self_win_hex = getattr(self, "_self_win_hex", None)

    skip, to_close = [], []
    for data in sel:
        win_id, pid, title, *_ = data
        # never close ourselves
        if (self_pid and pid == self_pid) or (self_win_hex and win_id.lower() == self_win_hex.lower()):
            continue
        if looks_unsaved(title) and not include_unsaved:
            skip.append(title)
            continue
        to_close.append((win_id, title))

    if not to_close:
        QMessageBox.information(self, "Nothing to close", "No saved windows selected.")
        return

    if any(looks_unsaved(t) for _, t in to_close):
        btn = QMessageBox.question(
            self, "Unsaved?",
            "Some look unsaved – close anyway?",
            SB.Yes | SB.No, SB.No
        )
        if btn != SB.Yes:
            return

    for win_id, _ in to_close:
        self.run_command(f"xdotool windowclose {win_id}")

    msg = f"Closed {len(to_close)} window(s)" + (" (skipped unsaved)" if skip else "")
    self.statusBar().showMessage(msg, 4000)
    self.refresh()

def activate_window(self, item) -> None:
    data = item.data(Qt.ItemDataRole.UserRole)  # Qt6 enum
    if data:
        self.run_command(f"xdotool windowactivate {data[0]}")
