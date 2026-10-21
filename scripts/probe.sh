#!/bin/bash
pip install -q curl_cffi 2>&1 | tail -1
python3 - <<'PY'
import re
from curl_cffi import requests as cr
s = cr.Session(impersonate="chrome")
s.get("https://www.vueling.com/es", timeout=30)
base = "https://static.vueling.com/corporativeCMS/WebComponents/home/browser/"
for c in ["chunk-RD3OOIIV.js","chunk-IK2SU4X2.js"]:
    t = s.get(base+c, timeout=30).text
    i = t.find("bestPrices")
    print("CTX", c, t[max(0,i-2500):i+800].replace("\n"," "))
main = s.get(base+"main.js", timeout=30).text
urls=set()
for c in ["main.js"]+sorted(set(re.findall(r'(chunk-[A-Za-z0-9]+\.js)', main))):
    t = main if c=="main.js" else s.get(base+c, timeout=30).text
    for m in re.findall(r'https?://[A-Za-z0-9.-]+(?:/[A-Za-z0-9._/-]*)?', t):
        if "vueling" in m: urls.add(m)
print("URLS", sorted(urls))
PY
