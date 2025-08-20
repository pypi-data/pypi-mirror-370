from .core import duplicate_guard_pro, get_event_log, EventLog
from .export import export_json, export_csv, export_html
from .redact import default_redactor

def duplicate_guard(func=None, **kwargs):
    """Drop-in duplicate guard with smart defaults (2s window, arg capture)."""
    if func is not None and callable(func):
        return duplicate_guard_pro(window_ms=2000, capture_args=True)(func)
    return duplicate_guard_pro(window_ms=2000, capture_args=True, **kwargs)
