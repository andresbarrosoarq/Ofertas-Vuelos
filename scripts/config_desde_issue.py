"""Lee los criterios de búsqueda del texto de una issue y los guarda en config.json.

La app abre una issue con un bloque ```json; si no lo trae, se deja config.json
como está y solo se repite la búsqueda.
"""

import json
import os
import re
import sys
from pathlib import Path

CONFIG = Path(__file__).resolve().parent.parent / "config.json"
DIAS = {"lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"}
AEROLINEAS = {"Ryanair", "Vueling"}


def validar(c):
    aeropuertos = [str(a).strip().upper() for a in c["aeropuertos"]]
    assert len(aeropuertos) == 2 and all(re.fullmatch(r"[A-Z]{3}", a) for a in aeropuertos) \
        and aeropuertos[0] != aeropuertos[1], "aeropuertos: dos códigos IATA distintos"
    aerolineas = [a for a in c["aerolineas"] if a in AEROLINEAS]
    assert aerolineas, "aerolineas: Ryanair y/o Vueling"
    assert c["diaIda"] in DIAS and c["diaVuelta"] in DIAS, "días de la semana sin tildes"
    for k in ("horaIdaDesde", "horaVueltaDesde"):
        assert re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", c[k]), f"{k}: formato HH:MM"
    meses, adultos = int(c["meses"]), int(c["adultos"])
    assert 1 <= meses <= 6 and 1 <= adultos <= 9, "meses 1-6, adultos 1-9"
    return {
        "aeropuertos": aeropuertos, "aerolineas": aerolineas,
        "diaIda": c["diaIda"], "horaIdaDesde": c["horaIdaDesde"],
        "diaVuelta": c["diaVuelta"], "horaVueltaDesde": c["horaVueltaDesde"],
        "meses": meses, "adultos": adultos,
    }


def main():
    cuerpo = os.environ.get("ISSUE_BODY") or ""
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cuerpo, re.S)
    if not m:
        print("Sin criterios nuevos: se repite la búsqueda actual.")
        return
    try:
        cfg = validar(json.loads(m.group(1)))
    except (ValueError, KeyError, TypeError, AssertionError) as e:
        print(f"Criterios no válidos: {e}")
        sys.exit(1)
    CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("config.json actualizado:", json.dumps(cfg, ensure_ascii=False))


if __name__ == "__main__":
    main()
