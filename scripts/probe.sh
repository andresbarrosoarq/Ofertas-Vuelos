#!/bin/bash
pip install -q fast-flights curl_cffi 2>&1 | tail -1
pip show fast-flights | head -2
python3 - <<'PY'
from curl_cffi import requests as cr
for u in ["https://www.vueling.com/es","https://apimobile.vueling.com/","https://www.vueling.com/api/FlightPrice/GetAllFlights?originCode=AGP&destinationCode=BCN&year=2026&month=11&currencyCode=EUR&monthsRange=1"]:
    try:
        r = cr.get(u, impersonate="chrome", timeout=20); print("CFFI", r.status_code, u, r.text[:300].replace("\n"," "))
    except Exception as e: print("CFFI ERR", u, e)
PY
python3 - <<'PY'
import fast_flights, inspect
print("FF version", getattr(fast_flights,"__version__",None), [n for n in dir(fast_flights) if not n.startswith("_")])
try:
    from fast_flights import FlightData, Passengers, get_flights
    for fr,to,d in [("AGP","BCN","2026-11-06"),("BCN","AGP","2026-11-08")]:
        try:
            r = get_flights(flight_data=[FlightData(date=d, from_airport=fr, to_airport=to)], trip="one-way", seat="economy", passengers=Passengers(adults=1))
            print(fr,to,d, "current_price", getattr(r,"current_price",None))
            for f in r.flights: print(" ", f)
        except Exception as e: print("ERR", fr, to, repr(e)[:800])
except Exception as e: print("IMPORT ERR", repr(e))
PY
