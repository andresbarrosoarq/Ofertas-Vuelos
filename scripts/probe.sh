#!/bin/bash
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
for h in apiwww.vueling.com api.vueling.com apimobile.vueling.com tickets.vueling.com www.vueling.com vueling.com apiservices.vueling.com; do echo "DNS $h: $(getent hosts $h)"; done
for u in https://www.vueling.com/es https://tickets.vueling.com/ https://www.vueling.com/api/FlightPrice/GetAllFlights?originCode=AGP\&destinationCode=BCN\&year=2026\&month=11\&currencyCode=EUR\&monthsRange=1 ; do
  echo "== curl $u"; curl -sS --compressed -A "$UA" -H 'Accept: text/html,application/json,*/*' -H 'Accept-Language: es-ES,es;q=0.9' -o out.txt -w "%{http_code}\n" "$u"; head -c 400 out.txt; echo
done
pip install -q fast-flights==2.2 2>&1 | tail -1
python3 - <<'PY'
from fast_flights import FlightData, Passengers, get_flights
for fr,to,d in [("AGP","BCN","2026-11-06"),("BCN","AGP","2026-11-08")]:
    try:
        r = get_flights(flight_data=[FlightData(date=d, from_airport=fr, to_airport=to)], trip="one-way", seat="economy", passengers=Passengers(adults=1), fetch_mode="common")
        print(fr,to,d, "current_price", r.current_price)
        for f in r.flights: print(" ", f.name, f.departure, f.arrival, f.stops, f.price)
    except Exception as e: print("ERR", fr, to, repr(e)[:500])
PY
