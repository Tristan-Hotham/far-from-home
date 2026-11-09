"""Step 1: airports. Aggregate the Wikidata rows (one per combination of values) to one record per airport and one per
(airport, place served); find the places the airport is named after (a place served whose name is in the airport's label,
a Natural Earth town of the same country whose name is in the label, or a name airlines sell it under: marketing_names.csv);
measure the great-circle distance from the airport to each; apply code/overrides_airports.csv. Writes WORK/airports.pkl."""
import numpy as np, pandas as pd
from collections import defaultdict
from common import *

# ---- countries: Wikidata QID -> ISO, name, continent (Natural Earth 10m)
C = {}
for f in jload(f"{GEO}/ne_10m_admin_0_countries.geojson")["features"]:
    p = f["properties"]
    C[p["WIKIDATAID"]] = (p["ISO_A2_EH"], p["NAME"], p["CONTINENT"])
C.update({"Q15180": ("SU", "Soviet Union", "Europe")})

A = {}                                  # airport -> dict
P = defaultdict(lambda: {"label": "", "coords": set(), "pop": []})   # (airport, place) -> dict
for r in read_tsv(AIRPORTS):
    a = qid(r["a"])
    d = A.setdefault(a, {"qid": a, "label": "", "iata": set(), "icao": set(), "coords": set(), "ctry": set(), "pax": [], "sl": 0})
    if r["al"]: d["label"] = r["al"]
    if r["iata"]: d["iata"].add(r["iata"])
    if r["icao"]: d["icao"].add(r["icao"])
    x, y = point(r["coord"])
    if x is not None: d["coords"].add((round(x, 5), round(y, 5)))
    if r["ctry"]: d["ctry"].add(qid(r["ctry"]))
    if r["pax"]:
        try: d["pax"].append(float(r["pax"]))
        except ValueError: pass
    if r["sl"]: d["sl"] = max(d["sl"], int(float(r["sl"])))
    if r["place"]:
        pp = P[(a, qid(r["place"]))]
        if r["pl"]: pp["label"] = r["pl"]
        x, y = point(r["pcoord"])
        if x is not None: pp["coords"].add((round(x, 5), round(y, 5)))
        if r["ppop"]:
            try: pp["pop"].append(float(r["ppop"]))
            except ValueError: pass
print("airports", len(A), "airport-place pairs", len(P))

rows = []
for a, d in A.items():
    cs = np.array(sorted(d["coords"])) if d["coords"] else None
    if cs is None: continue
    lon, lat = np.median(cs[:, 0]), np.median(cs[:, 1])
    spread = float(km(lat, lon, cs[:, 1], cs[:, 0]).max()) if len(cs) > 1 else 0.0
    ct = sorted(d["ctry"])
    iso, cname, cont = C.get(ct[0], ("", "", "")) if ct else ("", "", "")
    rows.append(dict(qid=a, label=d["label"], iata="/".join(sorted(d["iata"])), icao="/".join(sorted(d["icao"])), lon=lon, lat=lat,
                     coord_spread_km=spread, ctry_qid=ct[0] if ct else "", n_ctry=len(ct), iso=iso, country=cname, continent=cont,
                     pax=max(d["pax"]) if d["pax"] else np.nan, sitelinks=d["sl"]))
AP = pd.DataFrame(rows).set_index("qid")
print("with coordinates", len(AP), "with IATA", (AP.iata != "").sum(), "with passengers", AP.pax.notna().sum())

# ---- candidate namesakes
cand = []
for (a, p), pp in P.items():
    if a not in AP.index or not pp["coords"]: continue
    cand.append(dict(qid=a, place_qid=p, place=pp["label"] or p, coords=sorted(pp["coords"]), pop=max(pp["pop"]) if pp["pop"] else np.nan, source="served"))
NE = pd.DataFrame([f["properties"] for f in jload(f"{GEO}/ne_10m_populated_places_simple.geojson")["features"]])
NE["key"] = NE["name"].map(norm)
MK = pd.read_csv(os.path.join(ROOT, "code", "marketing_names.csv"))
city = {}
for (a, p), pp in P.items():
    if pp["coords"] and pp["label"]:
        c = city.setdefault(p, {"place": pp["label"], "coords": set(), "pop": []}); c["coords"] |= pp["coords"]; c["pop"] += pp["pop"]
for _, m in MK.iterrows():
    hit = AP.index[AP.iata.str.split("/").map(lambda s: m.iata in s)]
    assert len(hit) == 1, m.iata
    c = city[m.city_qid]
    assert c["place"] == m.city, (c["place"], m.city)
    cand.append(dict(qid=hit[0], place_qid=m.city_qid, place=c["place"], coords=sorted(c["coords"]), pop=max(c["pop"]), source="marketed", marketed_as=m.marketed_as))
CA = pd.DataFrame(cand)


def variants(label):
    """the forms of a place name looked for in an airport label"""
    s = norm(re.split(r"[,(]", label)[0])
    v = {s}
    for sep in (" im ", " am ", " an der ", " on ", " upon ", " sur ", " de ", " del ", " city", " town", " municipality", " shi", " si", " gun"):
        if sep in s and s.split(sep)[0].strip():
            v.add(s.split(sep)[0].strip())
    return {x for x in v if len(x) >= 3}


def in_label(label, place):
    L = " " + norm(label) + " "
    return any(" " + x + " " in L for x in variants(place))


CA["named"] = [src == "marketed" or in_label(AP.at[a, "label"], pl) for a, pl, src in zip(CA.qid, CA.place, CA.source)]
# Natural Earth towns of the same country whose name is in the label and is not already matched by a place served (within NE_MAX_KM)
named_keys = defaultdict(set)
for a, pl in zip(CA.qid[CA.named], CA.place[CA.named]):
    named_keys[a] |= variants(pl)
ne_by_iso = {k: g for k, g in NE.groupby("iso_a2")}
NE_MAX_KM = 150
GENERIC = {"international", "airport", "regional", "municipal", "county", "national", "airfield", "aerodrome", "field", "air base", "city"}
add = []
for a, r in AP.iterrows():
    if r.iso not in ne_by_iso: continue
    L = " " + norm(r.label) + " "
    g = ne_by_iso[r.iso]
    g = g[[len(k) >= 4 and k not in GENERIC and (" " + k + " ") in L and not any(k in x or x in k for x in named_keys[a]) for k in g.key]]
    if len(g):
        dd = km(r.lat, r.lon, g.latitude.values, g.longitude.values)
        for k, sub in g.assign(d=dd).groupby("key"):
            b = sub.sort_values("d").iloc[0]
            if b.d > NE_MAX_KM: continue                          # a town of that name farther away is a namesake by chance
            add.append(dict(qid=a, place_qid="ne:" + str(b.ne_id), place=b["name"], coords=[(b.longitude, b.latitude)], pop=float(b.pop_max) or np.nan, source="label", named=True))
# a Natural Earth town that is also a place served by some airport in Wikidata (same name, within 30 km) takes the Wikidata
# identity, point and population, so that all the airports named after one city are grouped together
served = {}
for p, c in city.items():
    for v in variants(c["place"]):
        served.setdefault(v, []).append((p, c))
for a_ in add:
    best_ = None
    for p, c in served.get(norm(a_["place"]), []):
        cs = np.array(sorted(c["coords"]))
        d = float(km(a_["coords"][0][1], a_["coords"][0][0], cs[:, 1], cs[:, 0]).min())
        if d <= 30 and (best_ is None or d < best_[0]):
            best_ = (d, p, c)
    if best_:
        _, p, c = best_
        a_.update(place_qid=p, place=c["place"], coords=sorted(c["coords"]), pop=max(c["pop"]) if c["pop"] else np.nan, source="label+wd")
CA = pd.concat([CA, pd.DataFrame(add)], ignore_index=True)


def dist(a, coords):
    cs = np.array(coords)
    return float(km(AP.at[a, "lat"], AP.at[a, "lon"], cs[:, 1], cs[:, 0]).min())


CA["km"] = [dist(a, c) for a, c in zip(CA.qid, CA.coords)]
CA["plon"] = [min(c, key=lambda p: km(AP.at[a, "lat"], AP.at[a, "lon"], p[1], p[0]))[0] for a, c in zip(CA.qid, CA.coords)]
CA["plat"] = [min(c, key=lambda p: km(AP.at[a, "lat"], AP.at[a, "lon"], p[1], p[0]))[1] for a, c in zip(CA.qid, CA.coords)]
CA["n_place_coords"] = CA.coords.map(len)
CA = CA.drop(columns="coords")
print("candidates", len(CA), "named", CA.named.sum(), CA[CA.named].source.value_counts().to_dict())
AP.to_pickle(f"{WORK}/ap.pkl"); CA.to_pickle(f"{WORK}/ca_raw.pkl")
