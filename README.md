# Not where it says on the ticket

Airports and railway stations far from the places they are named after. The straight-line distance from 4,448 airports with an IATA code (Wikidata) to the place in their name, and from 2,888 UK railway stations and halts (OpenStreetMap) to the town or village their name begins with, with every long case read by eye.

Interactive page: https://maps.tristanhotham.com/far-from-home/
Paper: https://doi.org/10.5281/zenodo.24087597
Blog post: https://blog.tristanhotham.com/2026/10/31/far-from-home/
Code and data: https://github.com/Tristan-Hotham/far-from-home

## Headline results

- Half of all airports are within 5.6 km of their namesake; 3% are more than 30 km away.
- Farthest confirmed: Châlons Vatry, sold as Paris-Vatry, 136 km from Paris; Chicago Rockford 126 km; Tongren Dejiang 110 km; Frankfurt-Hahn 103 km; Memmingen (Munich West) 101 km; Warsaw Radom 94 km; London Oxford 90 km from London. Twelve of the fifteen farthest are second airports for a city with a closer one.
- Britain: London Oxford 90 km, Southend 57 km, Stansted 49 km, Glasgow Prestwick 45 km, Luton 44 km, Gatwick 40 km. Airports in the Republic of Ireland all lie within 8 km of their towns.
- Stations: half within 0.6 km of their namesake; 169 are 2 km or more away. Airport stations aside (they are named after the airport, not the town), farthest beyond a notional town circle: Tiverton Parkway (9.1 km), Llanbister Road (6.7 km), Dent (5.8 km), Beaulieu Road (5.5 km). The farthest from a town centre are airport stations: Manchester Airport (12.8 km), Birmingham International, London City Airport, Inverness Airport (11.6 km).
- 82 stations have Road in their name; 9 are named after a village 2 km or more away.
- Data checks: of 113 airport cases of 40 km or more, 23 were wrong links or coordinates, 12 regions or islands, 12 unsure (42% not as first given); of 286 station matches of 3 km or more, 208 homonyms, 7 streets, 7 coordinate errors, 4 unsure (79%).

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

- Airports: Wikidata airports with an IATA code; a place served counts as the namesake if its name is in the airport's English label; else a Natural Earth town of the same country named in the label within 150 km; plus 11 names sold by airlines (`code/marketing_names.csv`). Ranked by the farthest named place. Second airport: another airport named after the same city is closer to it.
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

Hotham, T. (2026) Not where it says on the ticket: airports and railway stations far from their namesakes. Zenodo. https://doi.org/10.5281/zenodo.24087597

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
