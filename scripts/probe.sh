#!/bin/bash
pip install -q curl_cffi fast-flights typing_extensions 2>&1 | tail -1
python3 - <<'PY'
import re, html
from curl_cffi import requests as cr
s = cr.Session(impersonate="chrome")
h = s.get("https://www.vueling.com/es", timeout=30).text
for m in re.finditer(r'corporate\.api\.proxy|endpoints', h):
    print("HTMLCTX", html.unescape(h[max(0,m.start()-300):m.start()+600]).replace("\n"," "))
    break
base = "https://static.vueling.com/corporativeCMS/WebComponents/home/browser/"
main = s.get(base+"main.js", timeout=30).text
for c in ["main.js"]+sorted(set(re.findall(r'(chunk-[A-Za-z0-9]+\.js)', main))):
    t = main if c=="main.js" else s.get(base+c, timeout=30).text
    for m in re.finditer(r'endpoints', t):
        print("JSCTX", c, t[max(0,m.start()-400):m.start()+400].replace("\n"," ")); break
PY
python3 - <<'PY'
import fast_flights
print("FF", [n for n in dir(fast_flights) if not n.startswith("_")])
from fast_flights import FlightData, Passengers, get_flights
import inspect; print(inspect.signature(get_flights))
for fr,to,d in [("AGP","BCN","2026-11-06"),("BCN","AGP","2026-11-08")]:
    try:
        r = get_flights(flight_data=[FlightData(date=d, from_airport=fr, to_airport=to)], trip="one-way", seat="economy", passengers=Passengers(adults=1))
        print(fr,to,d, type(r))
        for f in (r.flights if hasattr(r,"flights") else r)[:30]: print(" ", f)
    except Exception as e:
        import traceback; traceback.print_exc()
PY
