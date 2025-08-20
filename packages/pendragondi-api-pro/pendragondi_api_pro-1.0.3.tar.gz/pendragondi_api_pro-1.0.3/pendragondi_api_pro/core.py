import time
import json
import hashlib
import inspect
import threading
from collections import deque
from functools import wraps
from typing import Any, Callable, Deque, Dict, List, Optional, Tuple

_now_ns = time.monotonic_ns

class EventLog:
    def __init__(self, capacity: int = 5000, jsonl_path: Optional[str] = None):
        self._buf: Deque[Dict[str, Any]] = deque(maxlen=capacity)
        self._lock = threading.Lock()
        self._jsonl_path = jsonl_path

    def add(self, event: Dict[str, Any]) -> None:
        with self._lock:
            self._buf.append(event)
            if self._jsonl_path:
                try:
                    with open(self._jsonl_path, "a", encoding="utf-8") as f:
                        f.write(json.dumps(event, ensure_ascii=False) + "\n")
                except Exception:
                    pass

    def snapshot(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._buf)

_GLOBAL_EVENT_LOG = EventLog()

def get_event_log() -> EventLog:
    return _GLOBAL_EVENT_LOG

def _wall_time_iso() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def _hash_identity(obj: Any) -> str:
    h = hashlib.sha1(repr(obj).encode("utf-8"))
    return h.hexdigest()

def _freeze_arg(v: Any) -> Any:
    if isinstance(v, (str, int, float, bool, type(None))):
        return v
    if isinstance(v, (list, tuple)):
        return tuple(_freeze_arg(x) for x in v)
    if isinstance(v, dict):
        return tuple(sorted((k, _freeze_arg(val)) for k, val in v.items()))
    r = repr(v)
    return r if len(r) <= 256 else (r[:253] + '...')

def _default_identity(func: Callable, args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> Tuple[Any, ...]:
    module = getattr(func, '__module__', None)
    qualname = getattr(func, '__qualname__', getattr(func, '__name__', '<??>'))
    try:
        sig = inspect.signature(func)
        bound = sig.bind_partial(*args, **kwargs)
        bound.apply_defaults()
        items = []
        for name, val in bound.arguments.items():
            if name in ('self', 'cls'):
                continue
            items.append((name, _freeze_arg(val)))
        normalized = tuple(items)
    except Exception:
        normalized = (tuple(_freeze_arg(a) for a in args),
                      tuple(sorted((k, _freeze_arg(v)) for k, v in kwargs.items())))
    return (module, qualname, normalized)

def _first_n_stack(limit: int) -> List[Dict[str, Any]]:
    frames = []
    for frame_info in inspect.stack()[2: 2 + max(0, limit)]:
        frames.append({'file': frame_info.filename, 'line': frame_info.lineno, 'func': frame_info.function})
    return frames

def _func_location(func: Callable) -> Tuple[str, int]:
    try:
        src = inspect.getsourcefile(func) or inspect.getfile(func)
        _, lineno = inspect.getsourcelines(func)
        return src, lineno
    except Exception:
        return ('<unknown>', -1)

def duplicate_guard_pro(
    *,
    window_ms: Optional[int] = 2000,
    key: Optional[Callable[..., Any]] = None,
    capture_args: bool = False,
    redact: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    stack_depth: int = 6,
    rate_limit_per_minute: Optional[int] = 60,
    event_log: Optional[EventLog] = None,
    jsonl_path: Optional[str] = None,
):
    global _GLOBAL_EVENT_LOG
    log = event_log or get_event_log()
    if jsonl_path and log is _GLOBAL_EVENT_LOG:
        _GLOBAL_EVENT_LOG = log = EventLog(capacity=5000, jsonl_path=jsonl_path)

    seen_map: Dict[str, int] = {}
    hit_counts: Dict[str, int] = {}
    rl_window_ns = 60 * 1_000_000_000
    rl_bucket_start_ns = _now_ns()
    lock = threading.Lock()

    def _should_rate_limit(func_id: str) -> bool:
        nonlocal rl_bucket_start_ns
        now = _now_ns()
        with lock:
            if now - rl_bucket_start_ns >= rl_window_ns:
                hit_counts.clear()
                rl_bucket_start_ns = now
            if rate_limit_per_minute is None:
                return False
            cur = hit_counts.get(func_id, 0)
            if cur >= rate_limit_per_minute:
                return True
            hit_counts[func_id] = cur + 1
            return False

    def _make_event(func: Callable, ident_obj: Any, duplicate: bool,
                    args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> Dict[str, Any]:
        module = getattr(func, '.__module__', '')
        qualname = getattr(func, '__qualname__', getattr(func, '__name__', '<??>'))
        file_src, def_line = _func_location(func)
        event: Dict[str, Any] = {
            'ts': _wall_time_iso(),
            'monotonic_ns': _now_ns(),
            'module': getattr(func, '__module__', ''),
            'function': qualname,
            'file': file_src,
            'def_line': def_line,
            'duplicate': duplicate,
            'key_hash': _hash_identity(ident_obj),
        }
        if stack_depth and stack_depth > 0:
            event['stack'] = _first_n_stack(stack_depth)
        if capture_args:
            cap = {'args': list(args), 'kwargs': dict(kwargs)}
            if redact:
                try:
                    cap = redact(cap)
                except Exception:
                    pass
            event['call'] = cap
        return event

    def _identity(func: Callable, args: Tuple[Any, ...], kwargs: Dict[str, Any]):
        if key:
            try:
                k = key(*args, **kwargs)
            except Exception:
                k = _default_identity(func, args, kwargs)
        else:
            k = _default_identity(func, args, kwargs)
        return k

    def _record(event: Dict[str, Any]) -> None:
        try:
            log.add(event)
        except Exception:
            pass

    def decorator(func: Callable):
        func_id = f"{getattr(func,'__module__','')}.{getattr(func,'__qualname__', getattr(func,'__name__','<??>'))}"

        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                ident = _identity(func, args, kwargs)
                key_h = _hash_identity(ident)
                now = _now_ns()
                duplicate = False
                with lock:
                    last = seen_map.get(key_h)
                    if last is not None:
                        if window_ms is None or (now - last) <= (window_ms * 1_000_000):
                            duplicate = True
                    seen_map[key_h] = now
                if duplicate and not _should_rate_limit(func_id):
                    _record(_make_event(func, ident, True, args, kwargs))
                return await func(*args, **kwargs)
            return async_wrapper

        @wraps(func)
        def wrapper(*args, **kwargs):
            ident = _identity(func, args, kwargs)
            key_h = _hash_identity(ident)
            now = _now_ns()
            duplicate = False
            with lock:
                last = seen_map.get(key_h)
                if last is not None:
                    if window_ms is None or (now - last) <= (window_ms * 1_000_000):
                        duplicate = True
                seen_map[key_h] = now
            if duplicate and not _should_rate_limit(func_id):
                _record(_make_event(func, ident, True, args, kwargs))
            return func(*args, **kwargs)
        return wrapper
    return decorator
