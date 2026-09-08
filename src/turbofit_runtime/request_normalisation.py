"""Request-side streaming usage defaults; response bytes are unchanged."""
from typing import Any, Dict


def apply_stream_usage_default(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy defaulting ``stream_options.include_usage`` for streams."""
    out = dict(payload)
    if out.get("stream") is not True:
        return out
    options = out.get("stream_options")
    if isinstance(options, dict):
        options = dict(options)
        options.setdefault("include_usage", True)
    else:
        options = {"include_usage": True}
    out["stream_options"] = options
    return out