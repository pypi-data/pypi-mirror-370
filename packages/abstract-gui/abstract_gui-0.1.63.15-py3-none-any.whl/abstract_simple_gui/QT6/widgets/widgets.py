from ..imports import *
from ..factories import connect_signals,apply_properties
from abstract_utilities import make_list

def addWidget(parent,items):
    items = make_list(items) or []
    parent.addWidget(*items)
def addLabel(parent,label):
    q_label= QLabel(label)
    addWidget(parent,q_label)
    
def getQHBoxLayout(label=None):
    label = label or 'QHBox'
    row = QHBoxLayout()
    addLabel(row,label)
    return row
def getQComboBox(listObj=None):
    listObj = listObj or []
    box = QComboBox(listObj)
    return box
def addItemWidgetToLayout(widget,layout,row=None,items=None):
    items = items or []
    widget.addItems(*items)
    row.addWidget(widget)
    layout.addLayout(row)
def getOutput(readOnly=True,
              minHeight=None,
              maxHeight=None,
              Expanding=(True,True),
              setVisible=False
              ):
    output = QTextEdit()
    output.setReadOnly(readOnly)
    if minHeight != None:
        output.setMinimumHeight(minHeight)
    if maxHeight != None:
        output.setMaximumHeight(maxHeight)
    for i,Expand in enumerate(Expanding):
        if expand == True:
            Expanding[i] = QSizePolicy.Policy.Expanding
    output.setSizePolicy(*Expanding)
    output.setVisible(setVisible)  # start hidden
    return output

def getWidget(widget,items=[],parent=None):
    items = make_list(items) or []
    widget = widget(*items)
    if parent:
        widget = parent.widget
    return widget

   
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
    """
    Generic row builder.
    - parent: the object where the widget will be attached as self.attr_name
    - widget_cls: class of widget (QLineEdit, QComboBox, etc.)
    - label: text label shown before widget
    - attr_name: name of the attribute set on parent (default: based on label)
    - default_value: initial value for widget
    - clear_button: only applies to QLineEdit
    - connect: optional signal handler for textChanged/currentIndexChanged
    - kwargs: extra options forwarded to widget_cls
    """
    row = QHBoxLayout()
    if label:
        addLabel(row, label)

    widget = widget_cls(**kwargs)

    # Default value handling
    if isinstance(widget, QLineEdit) and default_value is not None:
        widget.setText(str(default_value))
        if clear_button:
            widget.setClearButtonEnabled(True)

    elif isinstance(widget, QComboBox) and default_value is not None:
        if isinstance(default_value, (list, tuple)):
            widget.addItems(default_value)
        else:
            widget.addItem(str(default_value))

    # Pick attr_name automatically from label if not provided
    if not attr_name:
        safe_name = label.lower().replace(" ", "_")
        attr_name = f"{safe_name}_in"

    setattr(parent, attr_name, widget)

    # Connect signals smartly
    if connect:
        connect_signals(widget, callbacks=connect)

    row.addWidget(widget)
    return row

def createCombo(parent, layout=None, items=None, label=None, attr_name=None, connect=None, **kwargs):
    items = make_list(items) or []
    label = label or 'Combo'
    layout = layout or QVBoxLayout(parent)
    widget = QComboBox()
    if label:
        addLabel(layout, label)

    apply_properties(widget, kwargs)

    for item in items:
        # supports tuples like (text, userData)
        widget.addItem(*item) if isinstance(item, (list, tuple)) else widget.addItem(str(item))

    if not attr_name:
        safe = label.lower().replace(" ", "_").replace(":", "")
        attr_name = f"{safe}_combo"
    setattr(parent, attr_name, widget)

    # Connects: always ensure the widget is first parameter to your slot(s)
    if connect:
        if isinstance(connect, dict):
            # allow {'callbacks': fn or [..], 'signals': [...]} style
            connect_signals(widget, prepend_widget=True, allow_missing=True, **connect)
        elif isinstance(connect, list):
            for c in connect:
                if isinstance(c, dict):
                    connect_signals(widget, prepend_widget=True, allow_missing=True, **c)
                else:
                    connect_signals(widget, callbacks=c, prepend_widget=True, allow_missing=True)
        else:
            connect_signals(widget, callbacks=connect, prepend_widget=True, allow_missing=True)

    layout.addWidget(widget)
    return widget

def makeButton(parent,
               widget_cls=None,
               label=None,
               connect=None):
    widget_cls = widget_cls or QPushButton
    btn = widget_cls(label)
    if connect:
        connect_signals(btn, callbacks=connect)
    addWidget(parent,btn)
