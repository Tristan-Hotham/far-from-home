"""Step 7: README.md, LICENSE and the Reddit post text (reddit/post.md), filled from data/results.json.
https://doi.org/10.5281/zenodo.24087597 and https://blog.tristanhotham.com/2026/10/31/far-from-home/ stay as placeholders for the publisher."""
from common import *

R = jload(f"{DATA}/results.json")
a, s, ra, rs = R["air"], R["st"], R["air_review"], R["st_review"]
readme = f"""# Not where it says on the ticket

Airports and railway stations far from the places they are named after. The straight-line distance from {R['air_n']['ranked']:,} airports with an IATA code (Wikidata) to the place in their name, and from {R['st_n']['matched']:,} UK railway stations and halts (OpenStreetMap) to the town or village their name begins with, with every long case read by eye.

Interactive page: {PAGE}
Paper: {{https://doi.org/10.5281/zenodo.24087597}}
Blog post: {{https://blog.tristanhotham.com/2026/10/31/far-from-home/}}
Code and data: {REPO}

## Headline results

- Half of all airports are within {R['air_median_km']:.1f} km of their namesake; {R['air_over30_pc']:.0f}% are more than 30 km away.
- Farthest confirmed: Châlons Vatry, sold as Paris-Vatry, {a['XCR']['km']:.0f} km from Paris; Chicago Rockford {a['RFD']['km']:.0f} km; Tongren Dejiang {a['DEJ']['km']:.0f} km; Frankfurt-Hahn {a['HHN']['km']:.0f} km; Memmingen (Munich West) {a['FMM']['km']:.0f} km; Warsaw Radom {a['RDO']['km']:.0f} km; London Oxford {a['OXF']['km']:.0f} km from London. {fmt(R['air_world_secondary_n'], 'Word')} of the fifteen farthest are second airports for a city with a closer one.
- Britain: London Oxford {a['OXF']['km']:.0f} km, Southend {a['SEN']['km']:.0f} km, Stansted {a['STN']['km']:.0f} km, Glasgow Prestwick {a['PIK']['km']:.0f} km, Luton {a['LTN']['km']:.0f} km, Gatwick {a['LGW']['km']:.0f} km. Airports in the Republic of Ireland all lie within {R['air_ie_max_km']:.0f} km of their towns.
- Stations: half within {R['st_median_km']:.1f} km of their namesake; {R['st_over2_n']} are 2 km or more away. Airport stations aside (they are named after the airport, not the town), farthest beyond a notional town circle: Tiverton Parkway ({s['tiverton_parkway']['km']:.1f} km), Llanbister Road ({s['llanbister_road']['km']:.1f} km), Dent ({s['dent']['km']:.1f} km), Beaulieu Road ({s['beaulieu_road']['km']:.1f} km). The farthest from a town centre are airport stations: Manchester Airport ({s['manchester_airport']['km']:.1f} km), Birmingham International, London City Airport, Inverness Airport ({s['inverness_airport']['km']:.1f} km).
- {R['road']['n']} stations have Road in their name; {R['road']['away2']} are named after a village 2 km or more away.
- Data checks: of {ra['n']} airport cases of 40 km or more, {ra['wrong']} were wrong links or coordinates, {ra['region']} regions or islands, {ra['unsure']} unsure ({ra['corrected_pc']:.0f}% not as first given); of {rs['n']} station matches of 3 km or more, {rs['homonym']} homonyms, {rs['street']} streets, {rs['coord']} coordinate errors, {rs['unsure']} unsure ({rs['corrected_pc']:.0f}%).

## Files

| File | What it is |
|---|---|
| `index.html`, `js/page.js` | The interactive page: MapLibre on the OpenFreeMap Positron base map, a line from every airport and station to its namesake coloured by distance, filters, search, popups with sources, full-screen button. |
| `header.png` | Social card, 1200 x 630. |
| `data/airports.csv` | One row per ranked airport: codes, label, point, namesake, source of the name, distance, population, passengers, second-airport flag. CC0 (from Wikidata). |
| `data/airport_namesakes_all.csv` | Every airport and named place considered, with the verdict from the checks. CC0. |
| `data/stations.csv` | One row per matched station: name, CRS, point, OSM id, namesake, Wikidata id, population, distance, distance beyond the notional town circle, kind. ODbL. |
| `data/station_namesakes_all.csv` | Every station-to-settlement match with the verdict. ODbL. |
| `data/map.json` | Page data. ODbL (stations) and CC0 (airports). |
| `data/results.json` | Every number quoted on the page, in the paper, blog, collage and post. |
| `code/` | Numbered scripts, `marketing_names.csv` (names sold by airlines), `overrides_airports.csv` and `overrides_stations.csv` (every decision made by eye), templates, `qa.js`. |
| `img/`, `release/`, `reddit/` | Page figures; paper, blog post and Zenodo files; collage and post. |

## Method in brief

- Airports: Wikidata airports with an IATA code; a place served counts as the namesake if its name is in the airport's English label; else a Natural Earth town of the same country named in the label within 150 km; plus {R['air_n']['marketed']} names sold by airlines (`code/marketing_names.csv`). Ranked by the farthest named place. Second airport: another airport named after the same city is closer to it.
- Stations: OSM points of one name merged within 1 km; the longest run of leading words that is a UK settlement in Wikidata (with short forms such as Southend for Southend-on-Sea); measured to the nearest settlement of that name.
- Every long case read by eye; verdicts in the overrides files.
- Caveats: straight lines from centre points; administrative populations; incomplete Wikidata links and settlement list (Bradford, West Yorkshire, is missing); the marketing names are from the author's knowledge, checked against airline and airport listings; Wikidata keeps closed airports (Oslo Fornebu), which can count as a city's closer airport.

## How to rerun

Needs Python 3 with pandas, numpy, shapely, pyproj, matplotlib, Pillow; xelatex, pdftotext, pdfinfo; node with Playwright for `code/qa.js`. Raw inputs are listed in `code/common.py`; intermediates go to `FH_WORK`.

```
python3 code/01_airports.py     # airports and their named places
python3 code/02_stations.py     # stations and settlement names
python3 code/03_analysis.py     # overrides, rankings, results.json, data files
python3 code/04_figures.py      # figures
python3 code/05_build_site.py   # index.html
python3 code/06_paper.py        # paper PDF (DOI=10.5281/zenodo.N to fill the DOI)
python3 reddit/collage.py       # collage and header.png
python3 code/07_readme.py       # README, LICENSE, Reddit post
python3 code/08_release.py      # blog post, Zenodo files
node code/qa.js                 # screenshots
```

## Sources and licences

- Airports, places served, populations, UK settlements: Wikidata (CC0), queried with QLever.
- Stations: © OpenStreetMap contributors, Open Database Licence.
- Countries and towns: Natural Earth (public domain). Base map: OpenFreeMap (OpenStreetMap data, ODbL); MapLibre GL JS (BSD 3-Clause).
- Code MIT; text and figures CC BY 4.0; station data ODbL; airport data CC0.

## Citation

Hotham, T. (2026) Not where it says on the ticket: airports and railway stations far from their namesakes. Zenodo. {{https://doi.org/10.5281/zenodo.24087597}}

{AI}
"""
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(readme)
lic = """MIT License (code)

Copyright (c) 2026 Tristan Hotham

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Text and figures: CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), Tristan Hotham, 2026.
Station data (data/stations.csv, station_namesakes_all.csv and the station part of map.json): derived from OpenStreetMap, © OpenStreetMap contributors, Open Database Licence 1.0 (https://opendatacommons.org/licenses/odbl/1-0/).
Airport data (data/airports.csv, airport_namesakes_all.csv): derived from Wikidata, CC0.
Fonts under the SIL Open Font License.
"""
open(os.path.join(ROOT, "LICENSE"), "w", encoding="utf-8").write(lic)
post = f"""**Title:** [OC] Frankfurt-Hahn is {a['HHN']['km']:.0f} km from Frankfurt, Paris Vatry {a['XCR']['km']:.0f} km from Paris: the airports farthest from the city they are named after

**Body:**

I measured the straight line from {R['air_n']['ranked']:,} airports (Wikidata) to the place in their name, and from {R['st_n']['matched']:,} UK railway stations (OpenStreetMap) to the town their name starts with.

- Half of all airports are within {R['air_median_km']:.1f} km of their namesake; only {R['air_over30_pc']:.0f}% are more than 30 km away.
- Farthest: Paris Vatry {a['XCR']['km']:.0f} km, Chicago Rockford {a['RFD']['km']:.0f} km, Tongren Dejiang {a['DEJ']['km']:.0f} km, Frankfurt-Hahn {a['HHN']['km']:.0f} km, Memmingen ("Munich West") {a['FMM']['km']:.0f} km, London Oxford {a['OXF']['km']:.0f} km. {R['air_world_secondary_n']} of the top 15 are second airports for a city with a closer one.
- UK stations: half within {R['st_median_km']:.1f} km. Farthest beyond their town (airport stations aside): Tiverton Parkway ({s['tiverton_parkway']['km']:.1f} km), Llanbister Road ({s['llanbister_road']['km']:.1f} km), Dent ({s['dent']['km']:.1f} km).
- The data needed a lot of checking: {ra['corrected_pc']:.0f}% of airport cases over 40 km were wrong links (Wilmington NC linked to Wilmington, Delaware), regions or unresolved. Every decision is in the repo.

Interactive map (tap any airport or station): {PAGE}

**Source comment:**

Data: Wikidata (CC0) via QLever; OpenStreetMap contributors (ODbL); Natural Earth. A few airline marketing names (Paris Vatry, Munich West, Barcelona Reus...) added by hand and listed in the paper. Tools: Python (pandas, matplotlib, pyproj), MapLibre. Code and overrides: {REPO}
"""
open(os.path.join(ROOT, "reddit", "post.md"), "w", encoding="utf-8").write(post)
for txt in (readme, post):
    for bad in ("—", "–", "--", "DSIT", "DCMS"):
        assert bad not in txt.replace("|---|---|", ""), bad
print("readme, licence, post written")
