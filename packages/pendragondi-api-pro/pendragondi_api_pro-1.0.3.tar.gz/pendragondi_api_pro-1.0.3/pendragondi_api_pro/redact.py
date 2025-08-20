from typing import Dict, Any

_DEFAULT_FIELDS = {'password', 'passwd', 'secret', 'token', 'api_key', 'apikey', 'authorization', 'auth', 'cookie'}

def default_redactor(call: Dict[str, Any]) -> Dict[str, Any]:
    args = call.get('args', [])
    kwargs = dict(call.get('kwargs', {}))
    for k in list(kwargs.keys()):
        if k.lower() in _DEFAULT_FIELDS:
            kwargs[k] = '***'
    def _scrub(v):
        if isinstance(v, str) and len(v) > 40:
            return v[:6] + '...' + v[-4:]
        return v
    args = [_scrub(a) for a in args]
    return {'args': args, 'kwargs': kwargs}
