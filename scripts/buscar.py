"""Busca la oferta de ida y vuelta más barata según config.json.

Fuentes:
  - Ryanair: API pública de tarifas (services-api.ryanair.com/farfnd).
  - Vueling: Google Flights (vía fast-flights), porque vueling.com bloquea
    las peticiones automáticas.

Escribe site/vuelos.json, que es lo que muestra la app.
"""

import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from itertools import permutations
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "site" / "vuelos.json"

DIAS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
NOMBRES = {"AGP": "Málaga", "BCN": "Barcelona"}
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")


def dia_semana(nombre):
    n = nombre.strip().lower().replace("é", "e").replace("á", "a")
    return DIAS.index(n)


def sumar_meses(d, meses):
    m = d.month - 1 + meses
    a, m = d.year + m // 12, m % 12 + 1
    ultimo = [31, 29 if a % 4 == 0 and (a % 100 or a % 400 == 0) else 28,
              31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
    return date(a, m, min(d.day, ultimo))


def hhmm(h):
    hh, mm = h.split(":")
    return int(hh) * 60 + int(mm)


# ---------------------------------------------------------------- Ryanair

def ryanair(origen, destino, dia, hora_desde):
    """Vuelo Ryanair más barato de `dia` que sale a partir de `hora_desde`."""
    q = urllib.parse.urlencode({
        "departureAirportIataCode": origen,
        "arrivalAirportIataCode": destino,
        "outboundDepartureDateFrom": dia.isoformat(),
        "outboundDepartureDateTo": dia.isoformat(),
        "outboundDepartureTimeFrom": hora_desde,
        "outboundDepartureTimeTo": "23:59",
        "currency": "EUR",
    })
    url = f"https://services-api.ryanair.com/farfnd/v4/oneWayFares?{q}"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        datos = json.load(r)
    vuelos = []
    for fare in datos.get("fares") or []:
        o = fare.get("outbound") or {}
        precio = (o.get("price") or {}).get("value")
        salida = o.get("departureDate")
        if precio is None or not salida:
            continue
        llegada = o.get("arrivalDate") or ""
        vuelos.append({
            "aerolinea": "Ryanair",
            "vuelo": o.get("flightNumber") or "",
            "origen": origen,
            "destino": destino,
            "fecha": salida[:10],
            "salida": salida[11:16],
            "llegada": llegada[11:16],
            "precio": round(float(precio), 2),
            "fuente": "ryanair.com",
            "enlace": ("https://www.ryanair.com/es/es/trip/flights/select?adults=1&teens=0&children=0&infants=0"
                       f"&dateOut={dia.isoformat()}&isReturn=false&originIata={origen}&destinationIata={destino}"),
        })
    return vuelos


# ---------------------------------------------------------- Google Flights

def google(origen, destino, dia):
    """Vuelos directos de `dia` según Google Flights (incluye Vueling)."""
    from fast_flights import FlightQuery, Passengers, create_query, get_flights

    q = create_query(
        flights=[FlightQuery(date=dia.isoformat(), from_airport=origen, to_airport=destino)],
        seat="economy", trip="one-way", passengers=Passengers(adults=1),
        language="es", currency="EUR",
    )
    vuelos = []
    for f in get_flights(q):
        tramos = getattr(f, "flights", []) or []
        if len(tramos) != 1 or not getattr(f, "price", None):
            continue  # solo vuelos directos
        t = tramos[0]
        if t.from_airport.code != origen or t.to_airport.code != destino:
            continue
        aerolinea = (f.airlines or [""])[0]
        dep, arr = t.departure, t.arrival
        if tuple(dep.date) != (dia.year, dia.month, dia.day):
            continue
        vuelos.append({
            "aerolinea": aerolinea,
            "vuelo": "",  # Google no da el número de vuelo
            "origen": origen,
            "destino": destino,
            "fecha": dia.isoformat(),
            "salida": "%02d:%02d" % tuple(dep.time),
            "llegada": "%02d:%02d" % tuple(arr.time),
            "precio": float(f.price),
            "fuente": "Google Flights",
            "enlace": "https://www.google.com/travel/flights?hl=es&curr=EUR&q=" + urllib.parse.quote(
                f"vuelos de {origen} a {destino} el {dia.isoformat()} solo ida"),
        })
    return vuelos


# --------------------------------------------------------------- búsqueda

def con_reintentos(fn, *args, intentos=3):
    for i in range(intentos):
        try:
            return fn(*args)
        except Exception as e:  # noqa: BLE001
            if i == intentos - 1:
                raise
            print(f"  reintento {fn.__name__}{args}: {e}", file=sys.stderr)
            time.sleep(3 * (i + 1))


def main():
    cfg = json.loads((RAIZ / "config.json").read_text(encoding="utf-8"))
    aerolineas = {a.lower() for a in cfg.get("aerolineas", ["Ryanair", "Vueling"])}
    adultos = int(cfg.get("adultos", 1))
    d_ida, d_vta = dia_semana(cfg["diaIda"]), dia_semana(cfg["diaVuelta"])
    h_ida, h_vta = cfg["horaIdaDesde"], cfg["horaVueltaDesde"]
    hoy = datetime.now(timezone(timedelta(hours=1))).date()
    fin = sumar_meses(hoy, int(cfg.get("meses", 3)))
    salto = (d_vta - d_ida) % 7 or 7

    findes = []
    d = hoy + timedelta(days=(d_ida - hoy.weekday()) % 7)
    while d <= fin:
        findes.append((d, d + timedelta(days=salto)))
        d += timedelta(days=7)

    # Qué hay que consultar: (origen, destino, día, hora mínima)
    consultas = set()
    for a, b in permutations(cfg["aeropuertos"], 2):
        for ida, vta in findes:
            consultas.add((a, b, ida, h_ida))
            consultas.add((b, a, vta, h_vta))

    vuelos, errores = [], []
    fuentes = {"Ryanair": {"consultas": 0, "fallos": 0}, "Google Flights": {"consultas": 0, "fallos": 0}}
    for origen, destino, dia, hora in sorted(consultas, key=lambda c: (c[2], c[0])):
        print(f"{dia} {origen}->{destino} desde {hora}")
        if "ryanair" in aerolineas:
            fuentes["Ryanair"]["consultas"] += 1
            try:
                vuelos += con_reintentos(ryanair, origen, destino, dia, hora)
            except Exception as e:  # noqa: BLE001
                fuentes["Ryanair"]["fallos"] += 1
                errores.append(f"Ryanair {origen}-{destino} {dia}: {e}")
        if aerolineas - {"ryanair"}:
            fuentes["Google Flights"]["consultas"] += 1
            try:
                for v in con_reintentos(google, origen, destino, dia):
                    # Ryanair ya viene de su propia API, más fiable.
                    if v["aerolinea"].lower() in aerolineas - {"ryanair"} and hhmm(v["salida"]) >= hhmm(hora):
                        vuelos.append(v)
            except Exception as e:  # noqa: BLE001
                fuentes["Google Flights"]["fallos"] += 1
                errores.append(f"Google Flights {origen}-{destino} {dia}: {e}")
            time.sleep(1.5)

    for v in vuelos:
        v["precio"] = round(v["precio"] * adultos, 2)

    def mas_barato(origen, destino, dia, hora):
        cand = [v for v in vuelos if v["origen"] == origen and v["destino"] == destino
                and v["fecha"] == dia.isoformat() and hhmm(v["salida"]) >= hhmm(hora)]
        cand.sort(key=lambda v: (v["precio"], v["salida"]))
        return cand

    ofertas = []
    for a, b in permutations(cfg["aeropuertos"], 2):
        for ida, vta in findes:
            idas, vueltas = mas_barato(a, b, ida, h_ida), mas_barato(b, a, vta, h_vta)
            if not idas or not vueltas:
                continue
            ofertas.append({
                "origen": a, "destino": b,
                "fechaIda": ida.isoformat(), "fechaVuelta": vta.isoformat(),
                "total": round(idas[0]["precio"] + vueltas[0]["precio"], 2),
                "ida": idas[0], "vuelta": vueltas[0],
                "alternativasIda": idas[1:4], "alternativasVuelta": vueltas[1:4],
            })
    ofertas.sort(key=lambda o: (o["total"], o["fechaIda"]))

    resultado = {
        "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "config": cfg,
        "desde": hoy.isoformat(), "hasta": fin.isoformat(),
        "nombres": NOMBRES,
        "fuentes": fuentes,
        "errores": errores[:30],
        "ofertas": ofertas,
    }
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{len(vuelos)} vuelos, {len(ofertas)} combinaciones, {len(errores)} errores")

    resumen = os.environ.get("GITHUB_STEP_SUMMARY")
    lineas = ["## Ofertas de vuelos", ""]
    if ofertas:
        o = ofertas[0]
        lineas += [
            f"**Mejor oferta: {o['total']:.2f} €** — {NOMBRES.get(o['origen'], o['origen'])} ⇄ "
            f"{NOMBRES.get(o['destino'], o['destino'])}, {o['fechaIda']} → {o['fechaVuelta']}",
            "",
            "| Trayecto | Fecha | Hora | Compañía | Precio |",
            "|---|---|---|---|---|",
        ]
        for t in (o["ida"], o["vuelta"]):
            lineas.append(f"| {t['origen']}→{t['destino']} | {t['fecha']} | {t['salida']} | "
                          f"{t['aerolinea']} {t['vuelo']} | {t['precio']:.2f} € |")
    else:
        lineas.append("No se ha encontrado ninguna combinación.")
    if errores:
        lineas += ["", f"{len(errores)} consultas fallaron:", ""] + [f"- {e}" for e in errores[:10]]
    print("\n".join(lineas))
    if resumen:
        with open(resumen, "a", encoding="utf-8") as fh:
            fh.write("\n".join(lineas) + "\n")

    # Si ninguna fuente respondió, falla para que se note en Actions.
    if not vuelos:
        sys.exit(1)


if __name__ == "__main__":
    main()
