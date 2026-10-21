#!/bin/bash
pip install -q curl_cffi fast-flights typing_extensions 2>&1 | tail -1
python3 - <<'PY'
import re
from curl_cffi import requests as cr
s = cr.Session(impersonate="chrome")
base = "https://static.vueling.com/corporativeCMS/WebComponents/home/browser/"
main = s.get(base+"main.js", timeout=30).text
for c in ["main.js"]+sorted(set(re.findall(r'(chunk-[A-Za-z0-9]+\.js)', main))):
    t = main if c=="main.js" else s.get(base+c, timeout=30).text
    for pat in [r'\.json', r'serviceName:', r'endpoints:', r'endpoints=']:
        for m in list(re.finditer(pat, t))[:3]:
            print("CTX", c, pat, t[max(0,m.start()-250):m.start()+250].replace("\n"," "))
PY
python3 - <<'PY'
from fast_flights import FlightQuery, Passengers, create_query, get_flights
for fr,to,d in [("AGP","BCN","2026-11-06"),("BCN","AGP","2026-11-08")]:
    try:
        q = create_query(flights=[FlightQuery(date=d, from_airport=fr, to_airport=to)], seat="economy", trip="one-way", passengers=Passengers(adults=1), language="es", currency="EUR")
        res = get_flights(q)
        print(fr,to,d, type(res), len(res) if hasattr(res,"__len__") else "")
        for f in list(res)[:25]: print(" ", repr(f)[:600])
    except Exception:
        import traceback; traceback.print_exc()
PY
