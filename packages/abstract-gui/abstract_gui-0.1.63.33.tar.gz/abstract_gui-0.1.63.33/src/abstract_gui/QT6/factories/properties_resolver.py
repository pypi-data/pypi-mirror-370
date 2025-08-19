from ..imports import Any, Iterable, Optional,QtCore, QtWidgets, enum
def _qmeta_key_to_value(meta_enum: QtCore.QMetaEnum, key: str) -> int:
    """
    PyQt5: returns int
    PyQt6: returns (int, ok: bool)
    """
    v = meta_enum.keyToValue(key)
    if isinstance(v, tuple):
        val, ok = v
        return val if ok else -1
    return v

def _qmeta_keys_to_value(meta_enum: QtCore.QMetaEnum, keys: str) -> int:
    """
    For flag enums: 'A|B' → int. PyQt6 returns (int, ok).
    """
    v = meta_enum.keysToValue(keys)
    if isinstance(v, tuple):
        val, ok = v
        return val if ok else -1
    return v
def _meta_property(obj: QtCore.QObject, name: str) -> Optional[QtCore.QMetaProperty]:
    mo = obj.metaObject()
    for i in range(mo.propertyCount()):
        p = mo.property(i)
        if p.name() == name:
            return p
    return None

def _coerce_basic(value: Any, type_name: str) -> Any:
    t = (type_name or "").lower()
    if t in ("bool", "qbool"):
        if isinstance(value, bool): return value
        if isinstance(value, (int, float)): return bool(value)
        return str(value).strip().lower() in ("1","true","yes","on")
    if t in ("int", "qint", "qlonglong", "qulonglong"):
        return int(value)
    if t in ("double", "float", "qreal"):
        return float(value)
    if t in ("qstring", "str", "string"):
        return str(value)
    return value

def _find_python_enum_class(obj: QtCore.QObject, enum_name: str):
    # Search on class and its bases (PyQt6 keeps nested enums on the class)
    for cls in type(obj).mro():
        py_enum_cls = getattr(cls, enum_name, None)
        if py_enum_cls is not None:
            return py_enum_cls
    return None


def _find_python_enum_class(obj: QtCore.QObject, enum_name: str):
    for cls in type(obj).mro():
        py_enum_cls = getattr(cls, enum_name, None)
        if py_enum_cls is not None:
            return py_enum_cls
    return None

def _normalize_tokens(x) -> list[str]:
    if isinstance(x, (list, tuple, set)):
        return [str(t).strip() for t in x]
    if isinstance(x, str):
        return [t.strip() for t in x.replace(",", "|").split("|") if t.strip()]
    return [str(x).strip()]

def _coerce_enum_like(obj, prop: QtCore.QMetaProperty, value: Any) -> Any:
    meta_enum = prop.enumerator()
    enum_name = meta_enum.name()  # e.g., 'InsertPolicy'
    py_enum_cls = _find_python_enum_class(obj, enum_name)

    # Already a typed enum instance?
    if py_enum_cls and isinstance(value, py_enum_cls):
        return value

    # Raw int → try to cast to typed enum (PyQt6 likes typed)
    if isinstance(value, int):
        if py_enum_cls and issubclass(py_enum_cls, enum.Enum):
            try:
                return py_enum_cls(value)
            except Exception:
                return value
        return value

    # Strings or iterables
    if meta_enum.isFlag():
        # Use Qt's own parser when possible
        joined = "|".join(_normalize_tokens(value))
        acc = _qmeta_keys_to_value(meta_enum, joined)
        if acc < 0:
            raise ValueError(f"Unknown flag token(s) '{joined}' for {type(obj).__name__}.{enum_name}")
        if py_enum_cls and issubclass(py_enum_cls, enum.IntFlag):
            try:
                return py_enum_cls(acc)
            except Exception:
                return acc
        return acc
    else:
        tok = _normalize_tokens(value)[0]
        iv = _qmeta_key_to_value(meta_enum, tok)
        if iv < 0:
            raise ValueError(f"Unknown enum '{tok}' for {type(obj).__name__}.{enum_name}")
        if py_enum_cls and issubclass(py_enum_cls, enum.Enum):
            try:
                return py_enum_cls(iv)
            except Exception:
                return iv
        return iv

def _apply_via_qproperty(obj: QtCore.QObject, name: str, value: Any) -> bool:
    return bool(obj.setProperty(name, value))

def _apply_via_setter(obj: QtCore.QObject, name: str, value: Any) -> bool:
    setter = "set" + name[0].upper() + name[1:]
    meth = getattr(obj, setter, None)
    if callable(meth):
        meth(value)  # PyQt6 expects the *typed enum* here
        return True
    return False

def resolve_attr(obj: QtCore.QObject, name: str, value: Any) -> bool:
    prop = _meta_property(obj, name)
    coerced = value

    if prop is not None:
        if prop.isEnumType():
            coerced = _coerce_enum_like(obj, prop, value)
        else:
            coerced = _coerce_basic(value, prop.typeName() or "")

        if _apply_via_qproperty(obj, name, coerced):
            return True

    if _apply_via_setter(obj, name, coerced):
        return True

    return _apply_via_setter(obj, name, value)


def discover_writable_properties(obj):
    mo = obj.metaObject()
    out = []
    for i in range(mo.propertyOffset(), mo.propertyCount()):
        p = mo.property(i)
        if p.isWritable():
            out.append(p.name())
    return out

def apply_properties(obj, props: dict):
    for k, v in props.items():
        resolve_attr(obj, k, v)


def resolve_attr(obj: QtCore.QObject, name: str, value: Any) -> bool:
    """
    Introspect the Q_PROPERTY 'name', coerce 'value' appropriately (incl. enums/flags),
    then apply via setProperty; fallback to explicit setter.
    """
    prop = _meta_property(obj, name)
    coerced = value

    if prop is not None:
        if prop.isEnumType():
            coerced = _coerce_enum_like(obj, prop, value)
        else:
            coerced = _coerce_basic(value, prop.typeName() or "")

        # First try Q_PROPERTY route
        if _apply_via_qproperty(obj, name, coerced):
            return True

    # Fallback: explicit setter (expects proper enum instance in PyQt6)
    if _apply_via_setter(obj, name, coerced):
        return True

    # Last-chance: try the original value
    return _apply_via_setter(obj, name, value)
                    #input(values["mapping"][attr][attr_value])  
def discover_writable_properties(obj):
    mo = obj.metaObject()
    writable = []
    for i in range(mo.propertyOffset(), mo.propertyCount()):
        p = mo.property(i)
        if p.isWritable():
            writable.append(p.name())
    return writable

def apply_properties(obj, props: dict):
    for name, val in props.items():
        response = resolve_attr(obj, name, val)
        print(response)
        if response == False:
            print(obj, name, val)
