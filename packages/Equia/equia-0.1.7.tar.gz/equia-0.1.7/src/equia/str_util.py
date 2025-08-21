""" `models.str_util`

Utility functions for input/output string formatting for `*Input` and `*Result` objects.
"""
import attr
from .types import UNSET, Unset

def default_input_str(self) -> str:
    """Default string representation for `*Input` objects."""
    lines = ["", f"{self.__class__.__name__}:"]
    for fld in attr.fields(self.__class__):
        val = getattr(self, fld.name)
        out = val if not isinstance(val, (Unset, type(None))) else "N/A"
        # indent multi-line repr
        text = str(out).replace("\n", "\n    ")
        lines.append(f"  {fld.name}: {text}")
    return "\n".join(lines)

def default_result_str(self) -> str:
    """Default string representation for `*Result` objects."""
    parts = ["", f"{self.__class__.__name__}:"]
    for field in getattr(self, "__attrs_attrs__", []):
        name = field.name
        val = getattr(self, name)
        if isinstance(val, (Unset, type(None))):
            parts.append(f"  {name}: N/A")
        else:
            text = str(val).replace("\n", "\n    ")
            parts.append(f"  {name}: {text}")
    return "\n".join(parts)
