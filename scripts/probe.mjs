const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36';
async function get(url, extra = {}) {
  try {
    const r = await fetch(url, { headers: { 'User-Agent': UA, 'Accept': 'application/json, text/plain, */*', 'Accept-Language': 'es-ES,es;q=0.9', ...extra } });
    const t = await r.text();
    console.log(`\n=== ${r.status} ${url}\n${t.slice(0, 1500)}`);
    return t;
  } catch (e) { console.log(`\n=== ERR ${url} ${e}`); return ''; }
}
await get('https://services-api.ryanair.com/farfnd/v4/oneWayFares?departureAirportIataCode=AGP&arrivalAirportIataCode=BCN&outboundDepartureDateFrom=2026-11-06&outboundDepartureDateTo=2026-11-06&outboundDepartureTimeFrom=17:00&outboundDepartureTimeTo=23:59&currency=EUR');
await get('https://www.ryanair.com/api/farfnd/v4/oneWayFares/AGP/BCN/cheapestPerDay?outboundMonthOfDate=2026-11-01&currency=EUR');
await get('https://www.ryanair.com/api/booking/v4/es-es/availability?ADT=1&CHD=0&INF=0&TEEN=0&Origin=AGP&Destination=BCN&DateOut=2026-11-06&FlexDaysOut=2&FlexDaysBeforeOut=0&RoundTrip=false&ToUs=AGREED&IncludeConnectingFlights=false');
const vq = 'originCode=AGP&destinationCode=BCN&year=2026&month=11&currencyCode=EUR&monthsRange=1';
for (const base of ['https://apiwww.vueling.com/api/FlightPrice/GetAllFlights', 'https://www.vueling.com/api/FlightPrice/GetAllFlights', 'https://apiwww.vueling.com/api/FlightPrice/GetFlightPrices'])
  await get(`${base}?${vq}`, { Origin: 'https://www.vueling.com', Referer: 'https://www.vueling.com/' });
const home = await get('https://www.vueling.com/es');
const scripts = [...home.matchAll(/<script[^>]+src="([^"]+)"/g)].map(m => new URL(m[1], 'https://www.vueling.com').href);
console.log('\nSCRIPTS', scripts);
const found = new Set();
for (const s of scripts.slice(0, 40)) {
  try { const t = await (await fetch(s, { headers: { 'User-Agent': UA } })).text();
    for (const m of t.matchAll(/["'`]([^"'`\s]*(?:apiwww|\/api\/)[^"'`\s]{0,120})["'`]/g)) found.add(m[1]);
  } catch {}
}
console.log('\nAPI STRINGS', [...found].join('\n'));
for (const m of home.matchAll(/(apiwww[^"'\s<]{0,120}|\/api\/[^"'\s<]{0,120})/g)) found.add(m[1]);
console.log('\nAPI STRINGS2', [...found].join('\n'));
