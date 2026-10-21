#!/bin/bash
pip install -q curl_cffi 2>&1 | tail -1
python3 - <<'PY'
import re
from curl_cffi import requests as cr
s = cr.Session(impersonate="chrome")
h = s.get("https://www.vueling.com/es", timeout=30).text
srcs = re.findall(r'<script[^>]+src="([^"]+)"', h)
print("SCRIPTS", srcs)
print("INLINE API", sorted(set(re.findall(r'https?://[a-zA-Z0-9.-]*vueling\.com[^"\'\s<>]*', h)))[:80])
found=set()
for src in srcs:
    u = src if src.startswith("http") else "https://www.vueling.com/" + src.lstrip("/")
    try:
        t = s.get(u, timeout=30).text
    except Exception as e:
        print("ERR", u, e); continue
    print("JS", u, len(t))
    for m in re.findall(r'["\'`]([^"\'`\s]{0,80}(?:[Aa]pi|[Pp]rice|[Ff]are|[Cc]alendar|[Aa]vailab)[^"\'`\s]{0,120})["\'`]', t):
        if "/" in m: found.add(m)
for f in sorted(found)[:400]: print("STR", f)
PY
