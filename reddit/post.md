**Title:** [OC] Frankfurt-Hahn is 103 km from Frankfurt, Paris Vatry 136 km from Paris: the airports farthest from the city they are named after

**Body:**

I measured the straight line from 4,448 airports (Wikidata) to the place in their name, and from 2,888 UK railway stations (OpenStreetMap) to the town their name starts with.

- Half of all airports are within 5.6 km of their namesake; only 3% are more than 30 km away.
- Farthest: Paris Vatry 136 km, Chicago Rockford 126 km, Tongren Dejiang 110 km, Frankfurt-Hahn 103 km, Memmingen ("Munich West") 101 km, London Oxford 90 km. 12 of the top 15 are second airports for a city with a closer one.
- UK stations: half within 0.6 km. Farthest beyond their town (airport stations aside): Tiverton Parkway (9.1 km), Llanbister Road (6.7 km), Dent (5.8 km).
- The data needed a lot of checking: 42% of airport cases over 40 km were wrong links (Wilmington NC linked to Wilmington, Delaware), regions or unresolved. Every decision is in the repo.

Interactive map (tap any airport or station): https://maps.tristanhotham.com/far-from-home/

**Source comment:**

Data: Wikidata (CC0) via QLever; OpenStreetMap contributors (ODbL); Natural Earth. A few airline marketing names (Paris Vatry, Munich West, Barcelona Reus...) added by hand and listed in the paper. Tools: Python (pandas, matplotlib, pyproj), MapLibre. Code and overrides: https://github.com/Tristan-Hotham/far-from-home
