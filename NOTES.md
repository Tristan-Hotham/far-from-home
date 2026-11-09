# far-from-home: working notes

Brief: /home/claude/work/new10/BRIEFS.md (study 3) + shared rules in /home/claude/work/new8/BRIEFS.md, /home/claude/work/new9/BRIEFS.md
and /home/claude/newdata/BRIEF.md. Format refs: studies/river-names, church-orientation, sunless-valleys; MapLibre page pattern from
studies/tower-shadows. Work files: /home/claude/scratch/far-from-home (delete at the end).

## Pipeline
01_airports.py (Wikidata rows -> one record per airport and per airport-place pair; named places = place served whose name is in
the label, Natural Earth town of the same country whose name is in the label (within 150 km), or a marketed name from
code/marketing_names.csv) -> 02_stations.py (OSM stations merged by name within 1 km; leading settlement name per part of the
name; nearest Wikidata settlement of that name, short forms such as Southend for Southend-on-Sea only if 5 km nearer)
-> 03_analysis.py (overrides, rankings, results.json, data files) -> 04_figures.py -> 05_build_site.py -> 06_paper.py ->
reddit/collage.py -> 07_readme.py -> 08_release.py -> qa.js

## Data checks (whole headline set)
- Airports: every named place 40 km or more from an airport with an IATA code read by eye (108 pairs): 23 wrong links or
  coordinates (Bathurst NSW for Bathurst Island; Wilmington Delaware for Wilmington NC; Ibaraki city for Ibaraki Prefecture;
  two Yichuns, Qianjiangs, Zhijiangs, Nagoyas, Heringsdorfs...), 12 regions/islands/counties, 12 unsure (excluded). Recorded in
  code/overrides_airports.csv. UK and Irish island airports (Isle of Man, Jersey, Islay...) also marked as regions.
- Raw P931 links without the name test are far noisier (regions, destination lists: Tweed-New Haven lists Florida resorts),
  which is why the ranking uses only places the airport is named after.
- Marketing names (code/marketing_names.csv) are from my knowledge, not the data: Frankfurt-Hahn, Paris Beauvais, Paris Vatry,
  Barcelona Reus, Barcelona Girona, Memmingen (Munich West), Düsseldorf Weeze, Oslo Torp, Hamburg Lübeck, Venice Treviso,
  Milan Bergamo. VERIFY each. Distances are from the data's coordinates.
- Stations: every station-to-settlement match of 4 km or more read by eye (243): 22 kept, 208 homonyms (the real namesake is
  missing from the Wikidata settlement list under that name, or the station is named after a district, valley, estate or
  street), 6 streets (Wandsworth Road, Finchley Road, Tottenham Court Road, Edgware Road, Oxford Road...), 6 coordinate errors,
  1 unsure. All in code/overrides_stations.csv. Every match of 40 km or more (183) was a coincidence.
- Bradford (West Yorkshire) is missing from the settlement list (so Bradford stations are unmatched); NI stations have no CRS.

## References and claims to verify (cited from memory)
- Bast, H. and Buchhold, B. (2017) QLever: a query engine for efficient SPARQL+Text search. CIKM 2017, 647 to 656.
- Vrandečić, D. and Krötzsch, M. (2014) Wikidata: a free collaborative knowledgebase. Communications of the ACM 57(10), 78 to 85.
- Haklay, M. and Weber, P. (2008) OpenStreetMap: user-generated street maps. IEEE Pervasive Computing 7(4), 12 to 18.
- Claims from memory in the text: the marketing names above; Dent is the highest main-line station in England (verify wording);
  Hahn was a US air base; Builth Road and Clarbeston Road are villages that grew round their stations; Kings Nympton was once
  South Molton Road; Doncaster Sheffield Airport closed in 2022; Warsaw Radom reopened in 2024; Inverness Airport station opened
  in 2023.

- Station review extended to every match of 3 km or more (286); the edge ranking draws on cases from 3.7 km.
- Ranking uses the farthest named place per airport (so Brussels South Charleroi ranks by Brussels, not Charleroi).
- Claims from memory also: several far airports were military fields (Hahn, Memmingen, Skavsta, Vatry, Radom, Weeze, Torp);
  London Oxford Airport is at Kidlington; Tiverton Parkway is at Sampford Peverell; Irton Road is on the Ravenglass line.

## Log
- All steps done: figures, page (QA desktop 1280 and phone 390: no console errors, no horizontal scroll), paper (10 pages,
  DOI fill tested), blog (6 figures), collage, header, README, LICENSE, Zenodo. Folder 22 MB. Scratch deleted.

## Independent review (2026)
- Pipeline re-run from raw: reproduced results.json exactly before changes.
- Bug fixed: norm() dropped unicode dashes, so "Milan–Malpensa", "Seattle–Tacoma", "Paris–Le Bourget", "Rize–Artvin" and 129
  other labels lost their place names. Now dashes are word breaks. Effect: 4,448 ranked airports (was 4,392); 113 airport cases
  of 40 km or more (6 new, all read and kept: RZV Artvin, MHT Boston, DJE Zarzis, AZA Phoenix, MXP Milan, ROA Blacksburg);
  Rize-Artvin (81 km from Artvin) enters the world top 15 in place of Girona; 12 (not 13) of the top 15 are second airports;
  Milan Bergamo is now a second airport (Malpensa closer); Le Bourget is Paris's closest named airport.
- Station kind rule fixed: "International"/"Gateway" no longer make St Pancras, Ashford, Harwich, Stratford or Edinburgh Gateway
  "airport stations" (now: name contains Airport, or Birmingham International).
- Airport stations (named after the airport, not the town) left out of the beyond-the-town ranking: Tiverton Parkway now leads.
- Seaton Delaval: Wikidata point identical to Seaton Sluice's (coast), marked coord.
- Oslo's closest "Oslo" airport in Wikidata is Fornebu (closed 1998): Torp ratio removed from texts; closed-airport caveat added.
- Texts: "most Road stations are streets" softened to "many"; Ireland claim now Republic of Ireland, max from data (8 km);
  "Europe holds most of the far cases" now "more than any other continent" with counts; Hahn radii rank computed.
- Marketing names: all 11 checked against airline/airport listings by web search (Weeze also on Wikipedia: Ryanair still
  sells it as Düsseldorf-Weeze). References verified: Bast and Buchhold CIKM 2017 pp. 647 to 656; Vrandečić and Krötzsch CACM
  57(10) 78 to 85; Haklay and Weber IEEE Pervasive Computing 7(4) 12 to 18. Dent "highest main-line station in England" and
  Inverness Airport station (opened 2023) confirmed.
- Bradford: only Bradford Interchange and Forster Square go unmatched (matched to a homonym 45 km off and rejected); caveat kept.
