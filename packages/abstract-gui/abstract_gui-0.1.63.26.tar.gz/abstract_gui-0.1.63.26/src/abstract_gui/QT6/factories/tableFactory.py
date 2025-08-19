# table_factory.py
from typing import Any, Iterable, List, Dict, Sequence, Optional, Tuple
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView
)
from PyQt6.QtCore import Qt

# -- you already have these; importing for clarity
# from .attr_resolver import apply_properties
# from .auto_signals import connect_signals
# from abstract_utilities import make_list

DEFAULT_TABLE_SIGNALS = [
    # selection / navigation
    "itemSelectionChanged", "currentCellChanged",
    # activation / clicks
    "cellActivated", "cellClicked", "cellDoubleClicked",
    # edits / data changes
    "itemChanged", "cellChanged",
    # context menu
    "customContextMenuRequested",
]

def _normalize_headers_and_data(
    data: Optional[Iterable],
    headers: Optional[Sequence[str]]
) -> Tuple[List[str], List[List[str]]]:
    """
    Accepts:
      - data as list[list] or list[dict]
      - headers optional; if dicts given and no headers, derive from union of keys (ordered by first row)
    Returns (headers, rows) where rows is list[list[str]]
    """
    data = list(data or [])
    if not data:
        return list(headers or []), []
    # dict mode
    if isinstance(data[0], dict):
        if not headers:
            # preserve the key order from the first row’s keys, then include any extras later
            first_keys = list(data[0].keys())
            extra_keys = []
            seen = set(first_keys)
            for row in data[1:]:
                for k in row.keys():
                    if k not in seen:
                        extra_keys.append(k); seen.add(k)
            headers = first_keys + extra_keys
        rows = [[str(d.get(h, "")) for h in headers] for d in data]
        return list(headers), rows
    # list/tuple mode
    # if no headers provided, make generic ones
    if not headers:
        max_len = max(len(r) for r in data)
        headers = [f"Col {i}" for i in range(max_len)]
    # pad rows to header length
    width = len(headers)
    rows = [ [str(r[i]) if i < len(r) else "" for i in range(width)] for r in data ]
    return list(headers), rows

def set_table_data(table: QTableWidget, data: Iterable, headers: Optional[Sequence[str]] = None):
    headers, rows = _normalize_headers_and_data(data, headers)
    table.blockSignals(True)
    table.clear()
    if headers:
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
    else:
        table.setColumnCount(0)
    table.setRowCount(len(rows))
    for r, row in enumerate(rows):
        for c, text in enumerate(row):
            item = QTableWidgetItem(text)
            table.setItem(r, c, item)
    table.blockSignals(False)

def get_selected_row_indices(table: QTableWidget) -> List[int]:
    sel = table.selectionModel()
    if not sel:
        return []
    rows = sorted(set(idx.row() for idx in sel.selectedIndexes()))
    return rows

def row_as_dict(table: QTableWidget, row: int) -> Dict[str, str]:
    headers = [ table.horizontalHeaderItem(c).text() for c in range(table.columnCount()) ]
    out = {}
    for c, h in enumerate(headers):
        it = table.item(row, c)
        out[h] = it.text() if it else ""
    return out

def current_cell(table: QTableWidget) -> Tuple[int, int]:
    return table.currentRow(), table.currentColumn()

def createTable(
    parent: QWidget,
    *,
    layout: Optional[QVBoxLayout] = None,
    label: Optional[str] = None,
    attr_name: Optional[str] = None,
    headers: Optional[Sequence[str]] = None,
    data: Optional[Iterable] = None,
    # table behaviors (sane defaults, all overrideable via props)
    selection_behavior: QAbstractItemView.SelectionBehavior = QAbstractItemView.SelectionBehavior.SelectRows,
    selection_mode: QAbstractItemView.SelectionMode = QAbstractItemView.SelectionMode.SingleSelection,
    edit_triggers: QAbstractItemView.EditTrigger = (
        QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.EditKeyPressed
    ),
    resize_mode: QHeaderView.ResizeMode = QHeaderView.ResizeMode.ResizeToContents,
    stretch_last_section: bool = True,
    props: Optional[Dict[str, Any]] = None,           # extra Qt properties via resolve_attr/apply_properties
    connect: Optional[Any] = None,                    # callbacks or dicts for connect_signals
    connect_signals_names: Optional[List[str]] = None,# explicit signal names; else DEFAULT_TABLE_SIGNALS
    prepend_widget: bool = True,                      # ensure your slot receives widget first
) -> QTableWidget:
    """
    Build a labeled QTableWidget, attach to `parent` as self.<attr_name>, populate, and wire signals.
    """
    from abstract_utilities import make_list
    from .attr_resolver import apply_properties  # your resolve_attr-based applier
    from .helpers import connect_signals, default_signals  # helpers with prepend_widget support

    layout = layout or QVBoxLayout(parent)
    if label:
        layout.addWidget(QLabel(label))

    table = QTableWidget()
    # defaults (can be overridden via props)
    table.setSelectionBehavior(selection_behavior)
    table.setSelectionMode(selection_mode)
    table.setEditTriggers(edit_triggers)
    table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

    # headers + data
    if data is not None or headers is not None:
        set_table_data(table, data or [], headers=headers)

    # header sizing
    if table.horizontalHeader():
        table.horizontalHeader().setSectionResizeMode(resize_mode)
        table.horizontalHeader().setStretchLastSection(stretch_last_section)

    # apply extra properties declaratively (uses your resolve_attr)
    if props:
        apply_properties(table, props)

    # auto attr name
    if not attr_name:
        base = (label or "table").strip().lower().replace(" ", "_").replace(":", "")
        attr_name = f"{base}_table"
    setattr(parent, attr_name, table)

    # connect signals
    if connect:
        # choose signal names
        names = connect_signals_names or DEFAULT_TABLE_SIGNALS
        if isinstance(connect, dict):
            # allow: {'callbacks': fn or [..], 'signals': [...], 'prepend_widget': True/False}
            kw = dict(connect)
            kw.setdefault("signals", names)
            kw.setdefault("prepend_widget", prepend_widget)
            kw.setdefault("allow_missing", True)
            connect_signals(table, **kw)
        elif isinstance(connect, list):
            for c in connect:
                if isinstance(c, dict):
                    kw = dict(c)
                    kw.setdefault("signals", names)
                    kw.setdefault("prepend_widget", prepend_widget)
                    kw.setdefault("allow_missing", True)
                    connect_signals(table, **kw)
                else:
                    connect_signals(table, callbacks=c, signals=names,
                                    prepend_widget=prepend_widget, allow_missing=True)
        else:
            connect_signals(table, callbacks=connect, signals=names,
                            prepend_widget=prepend_widget, allow_missing=True)

    layout.addWidget(table)
    return table
