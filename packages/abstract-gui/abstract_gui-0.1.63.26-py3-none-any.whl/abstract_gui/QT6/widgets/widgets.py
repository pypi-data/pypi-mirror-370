from ..imports import *
from ..factories import connect_signals, apply_properties
from abstract_utilities import make_list

# ---- Qt5/Qt6 compat for QSizePolicy ----
try:
    # Qt6
    _QSP_Policy = QSizePolicy.Policy
except AttributeError:
    # Qt5
    _QSP_Policy = QSizePolicy

def _as_size_policy_tuple(v):
    """
    Accepts:
      - None -> (Expanding, Expanding)
      - tuple of two policies (QSizePolicy.Policy or ints)
      - tuple of two booleans -> (Expanding if True else Preferred)
    Returns a pair suitable for setSizePolicy(w, h).
    """
    if v is None:
        return (_QSP_Policy.Expanding, _QSP_Policy.Expanding)
    if isinstance(v, (list, tuple)) and len(v) == 2:
        a, b = v
        def norm(x):
            if isinstance(x, bool):
                return _QSP_Policy.Expanding if x else _QSP_Policy.Preferred
            return x
        return (norm(a), norm(b))
    # fallback: both same
    if isinstance(v, bool):
        pol = _QSP_Policy.Expanding if v else _QSP_Policy.Preferred
        return (pol, pol)
    return (_QSP_Policy.Expanding, _QSP_Policy.Expanding)

# ---------------- basic adders ----------------

def addWidget(target, widget):
    """
    Adds a single widget into a layout or into a QWidget that has a layout.
    """
    if isinstance(target, (QHBoxLayout, QVBoxLayout, QGridLayout, QFormLayout)):
        target.addWidget(widget)
    elif isinstance(target, QWidget):
        lay = target.layout()
        if not lay:
            lay = QVBoxLayout(target)
            target.setLayout(lay)
        lay.addWidget(widget)
    else:
        raise TypeError(f"Unsupported target for addWidget: {type(target)}")

def addLabel(target, text):
    lbl = QLabel(text)
    addWidget(target, lbl)
    return lbl

def getQHBoxLayout(label=None):
    row = QHBoxLayout()
    if label:
        addLabel(row, label)
    return row

def getQComboBox(items=None):
    box = QComboBox()
    items = make_list(items) or []
    if items:
        # supports [(text,userData), ...] or [text,...]
        for it in items:
            if isinstance(it, (list, tuple)) and len(it) >= 1:
                if len(it) == 1:
                    box.addItem(str(it[0]))
                else:
                    box.addItem(str(it[0]), it[1])
            else:
                box.addItem(str(it))
    return box

def addItemWidgetToLayout(widget, layout, row=None, items=None):
    items = make_list(items) or []
    if hasattr(widget, "addItems") and items:
        # QComboBox.addItems expects iterable[str]
        if items and isinstance(items[0], (list, tuple)):  # [(text,userData), ...]
            for it in items:
                if len(it) == 1:
                    widget.addItem(str(it[0]))
                else:
                    widget.addItem(str(it[0]), it[1])
        else:
            widget.addItems([str(i) for i in items])
    if row is None:
        row = QHBoxLayout()
    row.addWidget(widget)
    layout.addLayout(row)

def getOutput(
    readOnly=True,
    minHeight=None,
    maxHeight=None,
    Expanding=(True, True),
    setVisible=False,
):
    output = QTextEdit()
    output.setReadOnly(readOnly)
    if minHeight is not None:
        output.setMinimumHeight(int(minHeight))
    if maxHeight is not None:
        output.setMaximumHeight(int(maxHeight))
    hpol, vpol = _as_size_policy_tuple(Expanding)
    output.setSizePolicy(hpol, vpol)
    output.setVisible(bool(setVisible))
    return output

def getWidget(widget_cls, args=None, parent=None):
    """
    Instantiate widget_cls with positional args (list/tuple). Does not overwrite it with parent.widget.
    """
    args = make_list(args) or []
    w = widget_cls(*args)
    return w

def getConnect(connect, widget, prepend_widget=True, allow_missing=True):
    """
    connect: fn | [fn | {...}] | {'callbacks': fn|[...], 'signals': 'toggled'|'clicked'|[...] }
    Delegates to your connect_signals(factory).
    """
    if not connect:
        return
    if isinstance(connect, dict):
        connect_signals(widget, prepend_widget=prepend_widget, allow_missing=allow_missing, **connect)
    elif isinstance(connect, list):
        for c in connect:
            if isinstance(c, dict):
                connect_signals(widget, prepend_widget=prepend_widget, allow_missing=allow_missing, **c)
            else:
                connect_signals(widget, callbacks=c, prepend_widget=prepend_widget, allow_missing=allow_missing)
    else:
        connect_signals(widget, callbacks=connect, prepend_widget=prepend_widget, allow_missing=allow_missing)

def _default_attr_name(label, suffix="widget"):
    safe = (label or "").lower().replace(" ", "_").replace(":", "") or "unnamed"
    return f"{safe}_{suffix}"

def getParentAttr(parent, widget, attr_name=None, label=None):
    if parent is None:
        return
    if not attr_name:
        attr_name = _default_attr_name(label, "button" if isinstance(widget, QPushButton) else "widget")
    setattr(parent, attr_name, widget)

def getAddWidget(parent=None, layout=None, widget=None):
    if widget is None:
        return
    if layout is not None:
        addWidget(layout, widget)
    elif parent is not None:
        addWidget(parent, widget)

# ---------------- row + builders ----------------

def make_input_row(
    parent,
    widget_cls=QLineEdit,
    label=None,
    attr_name=None,
    default_value=None,
    clear_button=True,
    connect=None,
    **kwargs
):
    row = QHBoxLayout()
    if label:
        addLabel(row, label)

    w = widget_cls()
    apply_properties(w, kwargs)

    # Default value handling
    if isinstance(w, QLineEdit) and default_value is not None:
        w.setText(str(default_value))
        if clear_button:
            w.setClearButtonEnabled(True)
    elif isinstance(w, QComboBox) and default_value is not None:
        if isinstance(default_value, (list, tuple)):
            w.addItems([str(x) for x in default_value])
        else:
            w.addItem(str(default_value))

    getParentAttr(parent, w, attr_name=attr_name, label=label)
    getConnect(connect, w)
    row.addWidget(w)
    return row

def createCombo(parent, layout=None, widget_cls=None, items=None, label=None, attr_name=None, connect=None, **kwargs):
    items = make_list(items) or []
    widget_cls = widget_cls or QComboBox
    if layout is None and parent is None:
        raise ValueError("createCombo: provide parent or layout")

    box = widget_cls()
    apply_properties(box, kwargs)

    # label (if a layout is passed, add the label to that layout)
    if label:
        getAddWidget(layout=layout or parent, widget=QLabel(label))

    # items
    for it in items:
        if isinstance(it, (list, tuple)) and len(it) >= 1:
            if len(it) == 1:
                box.addItem(str(it[0]))
            else:
                box.addItem(str(it[0]), it[1])
        else:
            box.addItem(str(it))

    getParentAttr(parent, box, attr_name=attr_name, label=label)
    getConnect(connect, box)
    getAddWidget(parent=parent, layout=layout, widget=box)
    return box

def createButton(parent, layout=None, widget_cls=None, label=None, attr_name=None, connect=None, **kwargs):
    widget_cls = widget_cls or QPushButton
    text = label or "button"
    btn = widget_cls(text)
    apply_properties(btn, kwargs)
    getParentAttr(parent, btn, attr_name=attr_name, label=label)
    getConnect(connect, btn)
    getAddWidget(parent=parent, layout=layout, widget=btn)
    return btn

def createCheckBox(parent, layout=None, widget_cls=None, label=None, attr_name=None, connect=None, **kwargs):
    widget_cls = widget_cls or QCheckBox
    text = label or "check"
    chk = widget_cls(text)
    apply_properties(chk, kwargs)
    getParentAttr(parent, chk, attr_name=attr_name, label=label)
    getConnect(connect, chk)
    getAddWidget(parent=parent, layout=layout, widget=chk)
    return chk

def createComponent(parent, layout=None, widget_cls=None, label=None, attr_name=None, connect=None, **kwargs):
    widget_cls = widget_cls or QTextEdit
    text = label or "check"
    addLabel(layout, text)
    chk = widget_cls()
    apply_properties(chk, kwargs)
    getParentAttr(parent, chk, attr_name=attr_name, label=label)
    getConnect(connect, chk)
    getAddWidget(parent=parent, layout=layout, widget=chk)
    return chk
