#!/bin/bash
pip install -q curl_cffi 2>&1 | tail -1
python3 - <<'PY'
import re, html
from curl_cffi import requests as cr
s = cr.Session(impersonate="chrome")
h = html.unescape(s.get("https://www.vueling.com/es", timeout=30).text)
keys=set()
for m in re.finditer(r'"([A-Za-z]*(?:[Uu]rl|[Ee]ndpoint|[Aa]pi|[Ss]ervice)[A-Za-z]*)"\s*:\s*"([^"]{1,200})"', h):
    keys.add(f"{m.group(1)} = {m.group(2)}")
for k in sorted(keys):
    if not re.search(r'(image|img|link|Link|href|icon|src)', k.split(" = ")[0]): print("KEY", k)
base = "https://static.vueling.com/corporativeCMS/WebComponents/home/browser/"
main = s.get(base+"main.js", timeout=30).text
chunks = sorted(set(re.findall(r'["\']\.?/?(chunk-[A-Za-z0-9]+\.js)["\']', main)))
print("CHUNKS", len(chunks))
found=set()
for c in chunks:
    t = s.get(base+c, timeout=30).text
    for m in re.findall(r'["\'`]([^"\'`\s]{0,100}(?:/api/|[Pp]rice|[Ff]are|[Cc]alendar|[Aa]vailab|[Ss]chedule|[Ff]light)[^"\'`\s]{0,120})["\'`]', t):
        if "/" in m: found.add(c+" :: "+m)
for f in sorted(found): print("STR", f)
PY
