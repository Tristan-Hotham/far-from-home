"""Step 2: stations. Merge OpenStreetMap station nodes of the same name within 1 km; split each name into parts at
'&', 'and', 'for' and '/'; in each part find the longest run of leading words that is the name of a UK settlement in
Wikidata; take the nearest settlement of that name and measure the distance. Classify what follows the settlement name
(Road, Parkway, a direction, or other words). Apply code/overrides_stations.csv. Writes WORK/stations.pkl."""
import numpy as np, pandas as pd
from collections import defaultdict
from common import *

KEEP_TYPES = {"Village", "hamlet", "human settlement", "suburb", "town", "market town", "locality", "area of London", "neighborhood",
              "city", "inner suburb", "county town", "seaside resort", "big city", "urban area", "residential area", "township",
              "new town (UK)", "large village", "built-up area in the United Kingdom", "town of the United Kingdom", "border city",
              "planned community", "model village", "college town", "group of houses", "quarter", "housing estate", "cathedral city",
              "spa town", "city of United Kingdom", "city status in the United Kingdom", "small town", "nucleated village", "port city",
              "largest city", "crofting township", "railway town", "resort town", "fishing village", "maritime settlement", "isolated settlement",
              "dispersed settlement", "inner city", "global city", "megacity", "garden village", "book town", "mining community"}
LEAD = {"east", "west", "north", "south", "great", "little", "upper", "lower", "nether", "old", "new", "long", "high", "much", "kings", "market"}
TAIL = {"wells", "spa", "regis", "magna", "parva", "village", "town", "bay"}
LINK = r"\s+(?:on|upon|in|under|by|le|super|next|cum|juxta|in the|on the|by the|on sea|at|with)\s+"


def keys(label):
    """the full name, plus short forms people use in station names: Southend for Southend-on-Sea, Builth for Builth Wells,
    Harling for East Harling, Burton for Burton upon Trent. The nearest settlement is taken, a short form only if it is
    more than 5 km nearer than any full-name match."""
    k = norm(re.split(r"[,(]", label)[0])
    out = {k: "full"}
    w = k.split()
    m = re.split(LINK, k)
    if len(m) > 1 and m[0]:
        out.setdefault(m[0], "short")
    if len(w) == 2 and w[1] in TAIL and w[0] not in LEAD:
        out.setdefault(w[0], "short")
    if len(w) >= 2 and w[0] in LEAD:
        out.setdefault(" ".join(w[1:]), "short")
    if " upon " in k:
        out.setdefault(k.replace(" upon ", " on "), "full")
    return {x: f for x, f in out.items() if f == "full" or (x not in SHORT_STOP and len(x) >= 4)}


SHORT_STOP = LEAD | TAIL | {"park", "hall", "bank", "green", "common", "wood", "hill", "end", "heath", "cross", "bridge", "london", "street",
                            "road", "lane", "gate", "field", "town", "village", "furnace", "house", "farm", "mill", "mills", "side", "the"}



ST = defaultdict(lambda: {"label": "", "types": set(), "coords": set(), "pop": []})
for r in read_tsv(SETTLE if SETTLE.endswith(".gz") else SETTLE):
    s = ST[qid(r["p"])]
    s["label"] = r["pl"]; s["types"].add(r["typel"])
    x, y = point(r["coord"])
    if x is not None: s["coords"].add((x, y))
    if r["pop"]:
        try: s["pop"].append(float(r["pop"]))
        except ValueError: pass
rows = []
for q, s in ST.items():
    if not (s["types"] & KEEP_TYPES) or not s["coords"] or not s["label"]: continue
    for x, y in s["coords"]:
        for k, form in keys(s["label"]).items():
            rows.append(dict(sq=q, sname=s["label"], key=k, form=form, slon=x, slat=y,
                             spop=max(s["pop"]) if s["pop"] else np.nan, stype="; ".join(sorted(s["types"] & KEEP_TYPES))))
SE = pd.DataFrame(rows)
SE = SE[SE.key.str.len() >= 3]
print("settlements", SE.sq.nunique(), "names", SE.key.nunique())
by_key = {k: g for k, g in SE.groupby("key")}
SHORT_PENALTY_KM = 5.0
maxlen = max(len(k.split()) for k in by_key)

# ---- stations, merged by name within 1 km
S = pd.DataFrame(list(read_tsv(STATIONS)))
S[["lon", "lat"]] = S.p.map(point).tolist()
S["osm"] = S.w.str.replace("https://www.openstreetmap.org/", "", regex=False)
groups = []
for nm, g in S.groupby("name"):
    left = list(g.index)
    while left:
        i = left.pop(0); grp = [i]
        for j in list(left):
            if km(S.at[i, "lat"], S.at[i, "lon"], S.at[j, "lat"], S.at[j, "lon"]) < 1.0:
                grp.append(j); left.remove(j)
        gg = S.loc[grp]
        crs = sorted({c for c in gg.ref if c})
        groups.append(dict(name=nm, lon=gg.lon.mean(), lat=gg.lat.mean(), crs="/".join(crs), osm=gg.osm.iloc[0], n_nodes=len(gg)))
SS = pd.DataFrame(groups)
SS["national_rail"] = SS.crs != ""
print("stations", len(S), "merged", len(SS), "with CRS", SS.national_rail.sum())

DIRS = {"north", "south", "east", "west", "central", "parkway", "junction", "road", "rd", "halt", "high", "low", "level", "street", "town",
        "international", "airport", "village", "park", "bridge", "city", "centre", "interchange", "platform", "spa", "pier", "docks",
        "harbour", "sands", "beach", "main", "upper", "lower", "lane", "station", "western", "eastern", "northern", "southern"}


def match(name):
    """the settlement names that a station name starts with, or that start a part after '&', 'and', 'for' or '/'"""
    base = re.sub(r"\(.*?\)", " ", name)
    out = []
    for part in re.split(r"\s+(?:&|and|for)\s+|/", base):
        w = norm(part).split()
        for n in range(min(len(w), maxlen), 0, -1):
            k = " ".join(w[:n])
            if k in by_key:
                rest = w[n:]
                kind = "name" if not rest else ("road" if rest[-1] in ("road", "rd") else "parkway" if "parkway" in rest
                       else "suffix" if all(x in DIRS for x in rest) else "other")
                out.append((k, " ".join(rest), kind))
                if not rest and w[-1] in ("road", "rd") and n > 1 and " ".join(w[:-1]) in by_key:   # a village named after its station
                    out.append((" ".join(w[:-1]), "road", "road"))
                break
    return out


res = []
for i, r in SS.iterrows():
    for k, rest, kind in match(r["name"]):
        g = by_key[k]
        if rest == "road" and kind == "road":                       # not the station village itself
            g = g[g.key != norm(r["name"])] if len(g[g.key != norm(r["name"])]) else g
        d = km(r.lat, r.lon, g.slat.values, g.slon.values)
        j = int(np.argmin(d + SHORT_PENALTY_KM * (g.form.values == "short"))); b = g.iloc[j]   # the full name wins unless 5 km farther
        res.append(dict(st=i, key=k, rest=rest, kind=kind, sq=b.sq, sname=b.sname, form=b.form, slon=b.slon, slat=b.slat, spop=b.spop, stype=b.stype, km=float(d[j]),
                        n_same=g.sq.nunique()))
M = pd.DataFrame(res)
M = M.join(SS, on="st")
print("stations with a settlement name", M.st.nunique(), "of", len(SS), M.kind.value_counts().to_dict())
SS.to_pickle(f"{WORK}/ss.pkl"); M.to_pickle(f"{WORK}/st_raw.pkl")
