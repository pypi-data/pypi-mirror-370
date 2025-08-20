import csv
import html
from typing import List, Dict, Any

def export_json(events: List[Dict[str, Any]], path: str) -> None:
    import json
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(events, f, ensure_ascii=False, indent=2)

def export_csv(events: List[Dict[str, Any]], path: str) -> None:
    def _flatten(e: Dict[str, Any]) -> Dict[str, Any]:
        out = dict(e)
        out['stack'] = '; '.join(
            f"{fr.get('file','')}:{fr.get('line','')}:{fr.get('func','')}"
            for fr in e.get('stack', [])[:6]
        ) if 'stack' in e else ''
        call = e.get('call')
        if call:
            out['args'] = str(call.get('args', []))
            out['kwargs'] = str(call.get('kwargs', {}))
        else:
            out['args'] = ''
            out['kwargs'] = ''
        return {k: v for k, v in out.items() if k not in ('call',)}
    flat = [_flatten(e) for e in events]
    if not flat:
        headers = ['ts','monotonic_ns','module','function','file','def_line','duplicate','key_hash','stack','args','kwargs']
        with open(path, 'w', newline='', encoding='utf-8') as f:
            csv.DictWriter(f, fieldnames=headers).writeheader()
        return
    headers = sorted({k for e in flat for k in e.keys()})
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        for row in flat:
            w.writerow(row)

def export_html(events: List[Dict[str, Any]], path: str, title: str = 'PendragonDI API Pro Report') -> None:
    esc = html.escape
    rows = []
    for e in events:
        stack_html = ''
        for fr in e.get('stack', [])[:8]:
            stack_html += f"<div class='frame'>{esc(fr.get('file',''))}:{esc(str(fr.get('line','')))} — {esc(fr.get('func',''))}</div>"
        call = e.get('call')
        args_html = esc(str(call.get('args'))) if call else ''
        kwargs_html = esc(str(call.get('kwargs'))) if call else ''
        rows.append(f"""
        <tr>
            <td>{esc(str(e.get('ts','')))}</td>
            <td>{esc(e.get('module',''))}.{esc(e.get('function',''))}</td>
            <td>{esc(e.get('file',''))}:{esc(str(e.get('def_line','')))}</td>
            <td>{'yes' if e.get('duplicate') else 'no'}</td>
            <td><code>{esc(e.get('key_hash',''))}</code></td>
            <td>{stack_html}</td>
            <td><div class='args'>{args_html}</div><div class='kwargs'>{kwargs_html}</div></td>
        </tr>
        """)
    doc = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>{esc(title)}</title>
<style>
body {{ font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; background:#0b1220; color:#e8eefc; }}
table {{ width:100%; border-collapse: collapse; }}
th, td {{ border-bottom:1px solid #223; padding:8px 10px; vertical-align: top; }}
th {{ background:#111a33; position: sticky; top:0; }}
.frame {{ color:#9bb; font-size: 12px; }}
code {{ color:#9ef; }}
.args, .kwargs {{ color:#bde; font-size: 12px; }}
.caption {{ margin: 14px 4px; color:#9bb; }}
</style>
</head>
<body>
<h1>{esc(title)}</h1>
<div class="caption">Total duplicate events: {len(events)}</div>
<table>
<thead>
<tr>
  <th>Time</th><th>Function</th><th>Defined at</th><th>Duplicate</th><th>Key</th><th>Stack</th><th>Args</th>
</tr>
</thead>
<tbody>
{''.join(rows)}
</tbody>
</table>
</body>
</html>"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(doc)
