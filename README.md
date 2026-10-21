# Ofertas de Vuelos

App para iPhone que busca la ida y vuelta más barata entre dos ciudades en Ryanair y Vueling, mezclando compañías si sale más barato.

Búsqueda por defecto (`config.json`):

- Málaga (AGP) ⇄ Barcelona (BCN), en los dos sentidos
- Ida en viernes a partir de las 17:00, vuelta en domingo a partir de las 08:00
- Próximos 3 meses, 1 persona, Ryanair + Vueling

La app muestra la mejor oferta (fechas, importe total y precio de cada trayecto con su compañía, hora y enlace para reservar) y la lista de todos los fines de semana ordenada por precio.

## Cómo funciona

```
GitHub Actions (cada 6 h, o al pulsar «Actualizar»)
  └─ scripts/buscar.py
       ├─ Ryanair: API de tarifas de ryanair.com
       └─ Vueling: Google Flights (vueling.com bloquea las consultas automáticas)
  └─ site/vuelos.json  ──►  GitHub Pages  ──►  app en el iPhone
```

- `scripts/buscar.py` consulta cada viernes/domingo del periodo en los dos sentidos, se queda con el vuelo más barato que cumple la hora mínima en cada trayecto y suma ida + vuelta.
- `site/` es la app web (PWA): `index.html`, iconos, `manifest.webmanifest` y `sw.js` para que abra sin conexión con los últimos precios.
- Los precios son por persona en tarifa básica, sin maleta facturada ni asiento. El de Vueling viene de Google Flights y puede diferir unos euros del de vueling.com.

## Instalarla en el iPhone

1. En GitHub: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
   GitHub Pages en un repositorio privado necesita GitHub Pro; si no lo tienes, haz el repositorio público (no contiene datos personales).
2. Lanza la primera búsqueda: **Actions → Buscar ofertas → Run workflow**.
3. Abre en Safari `https://andresbarrosoarq.github.io/Ofertas-Vuelos/`, pulsa Compartir → **Añadir a pantalla de inicio**.

## Cambiar la búsqueda desde la app

Pulsa **Cambiar** para elegir ciudades, días, horas, meses, personas y compañías. La primera vez pide un token de GitHub, que se guarda solo en el iPhone:

1. Crea uno en <https://github.com/settings/personal-access-tokens/new>.
2. Repository access: *Only select repositories* → `Ofertas-Vuelos`.
3. Permissions: **Contents** y **Actions** → *Read and write*.

Al guardar, la app actualiza `config.json` y GitHub vuelve a buscar (tarda 3–5 minutos). Con el mismo token, el botón **Actualizar** lanza una búsqueda al momento.

También puedes editar `config.json` directamente en GitHub:

```json
{
  "aeropuertos": ["AGP", "BCN"],
  "aerolineas": ["Ryanair", "Vueling"],
  "diaIda": "viernes",
  "horaIdaDesde": "17:00",
  "diaVuelta": "domingo",
  "horaVueltaDesde": "08:00",
  "meses": 3,
  "adultos": 1
}
```

## Ejecutarlo en local

```sh
pip install -r requirements.txt
python scripts/buscar.py           # escribe site/vuelos.json
python -m http.server -d site 8000 # abre http://localhost:8000
```
