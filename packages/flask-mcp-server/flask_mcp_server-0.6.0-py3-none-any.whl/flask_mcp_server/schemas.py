from __future__ import annotations
import inspect
from typing import Any, Dict, get_type_hints
from pydantic import TypeAdapter

def _py_to_json_schema(py_type: Any) -> Dict[str, Any]:
    try:
        return TypeAdapter(py_type).json_schema()
    except Exception:
        return {"type": "object"}

def build_input_schema(fn) -> Dict[str, Any]:
    sig = inspect.signature(fn)
    props = {}; required = []
    hints = get_type_hints(fn)
    for name, param in sig.parameters.items():
        if name == "self": continue
        ann = hints.get(name, Any)
        props[name] = _py_to_json_schema(ann)
        if param.default is inspect._empty:
            required.append(name)
    return {"type": "object", "properties": props, "required": required}

def build_output_schema(fn) -> Dict[str, Any]:
    hints = get_type_hints(fn)
    rt = hints.get("return", Any)
    return _py_to_json_schema(rt)
