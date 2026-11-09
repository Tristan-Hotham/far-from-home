"""Step 3: apply the overrides, choose each airport's and station's namesake, rank, and write data/*.csv, data/map.json and
data/results.json (every number quoted anywhere comes from results.json)."""
import numpy as np, pandas as pd
from common import *

AP = pd.read_pickle(f"{WORK}/ap.pkl"); CA = pd.read_pickle(f"{WORK}/ca_raw.pkl")
OA = pd.read_csv(os.path.join(ROOT, "code", "overrides_airports.csv"), keep_default_na=False)
DENS = 3000.0          # people per km2 for the notional circle of a town (an assumption, used only for the 'beyond the edge' ranking)
radius = lambda pop: np.sqrt(np.asarray(pop, float) / (np.pi * DENS))
R = {}

# ======================= airports
N = CA[CA.named].copy()
N = N.merge(OA[["qid", "place_qid", "verdict", "reason"]], on=["qid", "place_qid"], how="left")
N["verdict"] = N.verdict.fillna("ok"); N["reason"] = N.reason.fillna("")
assert set(N.verdict) <= {"ok", "wrong", "region", "unsure"}
miss = OA[~OA.set_index(["qid", "place_qid"]).index.isin(N.set_index(["qid", "place_qid"]).index)]
assert miss.empty, miss
N = N.join(AP[["label", "iata", "icao", "lon", "lat", "iso", "country", "continent", "pax", "sitelinks"]], on="qid")
N["has_iata"] = N.iata != ""
rev = N[N.has_iata & (N.km >= 40)]
R["air_review"] = dict(n=len(rev), wrong=int((rev.verdict == "wrong").sum()), region=int((rev.verdict == "region").sum()),
                       unsure=int((rev.verdict == "unsure").sum()), ok=int((rev.verdict == "ok").sum()))
R["air_review"]["corrected_pc"] = 100 * (len(rev) - R["air_review"]["ok"]) / len(rev)
R["air_review"]["wrong_pc"] = 100 * R["air_review"]["wrong"] / len(rev)

V = N[(N.verdict == "ok") & N.has_iata].copy()
V["pop0"] = V["pop"].fillna(0)
V = V.sort_values(["qid", "km", "pop0"], ascending=[True, False, False])
best = V.groupby("qid").head(1).copy()                          # when an airport names several places, the farthest of them
nplaces = V.groupby("qid").place.nunique()
best["n_named"] = best.qid.map(nplaces)
best["others"] = best.qid.map(V.groupby("qid").apply(lambda g: "; ".join(f"{p} {k:.0f} km" for p, k in zip(g.place.iloc[1:], g.km.iloc[1:])), include_groups=False))
# a second airport for the same city: another airport named after the same place, and closer to it
closest = V.groupby("place_qid").km.min()
nair = V.groupby("place_qid").qid.nunique()
best["closest_other_km"] = [V[(V.place_qid == p) & (V.qid != q)].km.min() if nair[p] > 1 else np.nan for p, q in zip(best.place_qid, best.qid)]
best["secondary"] = best.closest_other_km < best.km
best["times_main"] = best.km / best.closest_other_km
best["radii"] = np.where(best["pop"] >= 100000, best.km / radius(best["pop"]), np.nan)
best["region"] = best.continent
best = best.sort_values("km", ascending=False).reset_index(drop=True)
R["air_n"] = dict(airports=len(AP), iata=int((AP.iata != "").sum()), served=int(CA[CA.source == "served"].qid.nunique()),
                  named=int(N[N.has_iata].qid.nunique()), ranked=len(best), marketed=int((N.source == "marketed").sum()),
                  pax=int(AP.pax.notna().sum()))
R["air_median_km"] = float(best.km.median())
R["air_over30_pc"] = 100 * float((best.km > 30).mean())
R["air_over50_n"] = int((best.km >= 50).sum())
R["air_over80_n"] = int((best.km >= 80).sum())


MAIN_IATA = {"DCS/DSA": "DSA", "BSL/EAP/MLH": "BSL"}   # airports with more than one IATA code in Wikidata: the one in use


def arow(r):
    return dict(iata=MAIN_IATA.get(r.iata, r.iata.split("/")[0]), label=r.label, place=r.place, km=round(float(r.km), 1), country=r.country, iso=r.iso,
                pax=None if pd.isna(r.pax) else int(r.pax), pop=None if pd.isna(r["pop"]) else int(r["pop"]), source=r.source,
                marketed=r.get("marketed_as") if isinstance(r.get("marketed_as"), str) else "", secondary=bool(r.secondary),
                closest_other_km=None if pd.isna(r.closest_other_km) else round(float(r.closest_other_km), 1),
                times_main=None if pd.isna(r.times_main) else round(float(r.times_main), 1))


R["air_world"] = [arow(r) for _, r in best.head(15).iterrows()]
R["air_world_secondary_n"] = int(sum(r["secondary"] for r in R["air_world"]))
R["air_world_other_n"] = len(R["air_world"]) - R["air_world_secondary_n"]
far50 = best[best.km >= 50]
R["air_over50_by_cont"] = {k: int(v) for k, v in far50.continent.value_counts().items()}
R["air_ie_max_km"] = float(best[best.iso == "IE"].km.max())
R["air_europe"] = [arow(r) for _, r in best[best.continent == "Europe"].head(12).iterrows()]
uk = best[best.lat.between(49.8, 61) & best.lon.between(-11, 2) & best.iso.isin(["GB", "IE", "IM", "JE", "GG"])]
R["air_ukie"] = [arow(r) for _, r in uk.head(10).iterrows()]
sec = best[best.secondary & best["pop"].ge(500000)].sort_values("times_main", ascending=False)
R["air_secondary"] = [arow(r) for _, r in sec.head(12).iterrows()]
R["air_secondary_n"] = int(best.secondary.sum())
R["air_radii"] = [dict(arow(r), radii=round(float(r.radii), 1)) for _, r in best.dropna(subset=["radii"]).sort_values("radii", ascending=False).head(10).iterrows()]
rk = best.dropna(subset=["radii"]).sort_values("radii", ascending=False).reset_index(drop=True)
R["air_radii_hhn_rank"] = int(rk.index[rk.iata.str.split("/").map(lambda x: "HHN" in x)][0]) + 1
multi = best[best.n_named >= 2].sort_values("km", ascending=False)
R["air_multi_n"] = int(len(multi))
R["air_multi"] = [dict(arow(r), others=r.others) for _, r in multi.head(6).iterrows()]
R["air_marketed"] = [arow(r) for _, r in best[best.source == "marketed"].iterrows()]
by_cont = best.groupby("continent").km.agg(["median", "size"])
R["air_by_continent"] = {k: dict(median=round(float(v["median"]), 1), n=int(v["size"])) for k, v in by_cont.iterrows() if v["size"] >= 50}
for k in ("DEJ", "WGN", "HHN", "FMM", "BVA", "REU", "NYO", "PIK", "OXF", "BSL", "SEN", "XCR", "RDO", "RFD", "STN", "LTN", "LGW", "LHR", "CRL", "TRF", "GRO", "VST", "MXP", "BGY", "NRN", "LBC", "TSF", "WMI", "FRA", "MUC", "CDG", "BCN", "ARN", "GLA", "EDI", "DSA", "LCY", "MAN", "CFN", "SWF", "MLB", "RZV"):
    s = best[best.iata.str.split("/").map(lambda x: k in x)]
    if len(s):
        R.setdefault("air", {})[k] = dict(arow(s.iloc[0]), radii=None if pd.isna(s.iloc[0].radii) else round(float(s.iloc[0].radii), 1))
# Treviso is a place served for Venice but sold as Venice Treviso; check the marketed claim survived
assert R["air"]["HHN"]["place"] == "Frankfurt" and R["air"]["FMM"]["place"] == "Munich" and R["air"]["OXF"]["place"] == "London"
cols = ["iata", "icao", "label", "country", "lon", "lat", "place", "place_qid", "source", "km", "pop", "pax", "n_named", "others", "secondary", "closest_other_km", "times_main", "radii"]
best["iata"] = best.iata.map(lambda c: MAIN_IATA.get(c, c.split("/")[0]))
best["marketed_as"] = best.get("marketed_as")
out = best.assign(airport_qid=best.qid)[["airport_qid"] + cols + ["marketed_as"]].round(4)
out.to_csv(f"{DATA}/airports.csv", index=False)
allc = N[N.has_iata][["qid", "iata", "label", "place", "place_qid", "source", "km", "pop", "verdict", "reason"]].rename(columns={"qid": "airport_qid"}).round(3)
allc.to_csv(f"{DATA}/airport_namesakes_all.csv", index=False)

# ======================= stations
M = pd.read_pickle(f"{WORK}/st_raw.pkl"); SS = pd.read_pickle(f"{WORK}/ss.pkl")
OS = pd.read_csv(os.path.join(ROOT, "code", "overrides_stations.csv"), keep_default_na=False)
M = M.merge(OS[["osm", "key", "verdict", "reason"]], on=["osm", "key"], how="left")
assert len(OS) == M.verdict.notna().sum(), (len(OS), M.verdict.notna().sum())
M["verdict"] = M.verdict.fillna("ok"); M["reason"] = M.reason.fillna("")
assert (M[M.km >= 3].reason != "").all()                       # every match of 3 km or more was read by eye
rs = M[M.km >= 3]
R["st_review"] = dict(n=len(rs), ok=int((rs.verdict == "ok").sum()), homonym=int((rs.verdict == "homonym").sum()), street=int((rs.verdict == "street").sum()),
                      coord=int((rs.verdict == "coord").sum()), unsure=int((rs.verdict == "unsure").sum()))
R["st_review"]["corrected_pc"] = 100 * (len(rs) - R["st_review"]["ok"]) / len(rs)
R["st_review"]["over40"] = int((rs.km >= 40).sum())
G = M[M.verdict == "ok"].copy()
G = G.sort_values(["st", "km"], ascending=[True, False])
st = G.groupby("st").head(1).copy()
st["edge_km"] = st.km - np.where(st.spop.notna(), radius(st.spop.fillna(0)), 0.0)
st["kind2"] = np.select([st["name"].str.contains(r"\bParkway\b"), st["name"].str.contains(r"\bAirport\b") | (st["name"] == "Birmingham International"),
                         st["name"].str.contains(r"\bRoad\b")], ["parkway", "airport", "road"], "other")
st = st.sort_values("km", ascending=False).reset_index(drop=True)
R["st_n"] = dict(stations=len(SS), national_rail=int(SS.national_rail.sum()), matched=int(st.st.nunique()),
                 matched_nr=int(st.national_rail.sum()), matched_pc=100 * st.st.nunique() / len(SS))
R["st_median_km"] = float(st.km.median())
R["st_over2_n"] = int((st.km >= 2).sum()); R["st_over2_pc"] = 100 * float((st.km >= 2).mean())
R["st_over5_n"] = int((st.km >= 5).sum())


def srow(r):
    return dict(name=r["name"], crs=r.crs, place=r.sname, km=round(float(r.km), 1), edge_km=round(float(r.edge_km), 1),
                pop=None if pd.isna(r.spop) else int(r.spop), kind=r.kind2, nr=bool(r.national_rail))


R["st_top"] = [srow(r) for _, r in st.head(15).iterrows()]
# stations named after an airport (Manchester Airport, Inverness Airport...) take their name from the airport, not the town, so
# they are left out of the 'beyond the town' ranking; they stay in st_top and the data
R["st_edge"] = [srow(r) for _, r in st[st.kind2 != "airport"].sort_values("edge_km", ascending=False).head(12).iterrows()]
R["st_airport_n"] = int((st.kind2 == "airport").sum())
nonair = st[st.kind2 != "airport"]
R["st_top_nonair"] = [srow(r) for _, r in nonair.head(10).iterrows()]
roads = SS[SS["name"].str.contains(r"\bRoad\b")]
R["road"] = dict(n=len(roads), nr=int(roads.national_rail.sum()))
rd = M[M["name"].str.contains(r"\bRoad\b")].copy()
rd_ok = st[st.kind2 == "road"]
R["road"]["named_town"] = int(len(rd_ok))
R["road"]["street"] = int(rd[rd.verdict == "street"].st.nunique())
R["road"]["away2"] = int((rd_ok.km >= 2).sum())
R["road_list"] = [srow(r) for _, r in rd_ok[rd_ok.km >= 2].sort_values("km", ascending=False).iterrows()]
pk = SS[SS["name"].str.contains(r"\bParkway\b")]
R["parkway"] = dict(n=len(pk), matched=int((st.kind2 == "parkway").sum()), median_km=float(st[st.kind2 == "parkway"].km.median()))
R["parkway_list"] = [srow(r) for _, r in st[st.kind2 == "parkway"].sort_values("km", ascending=False).head(10).iterrows()]
for nm in ("Tiverton Parkway", "Bristol Parkway", "Bodmin Parkway", "Dent", "Llanbister Road", "Beaulieu Road", "Inverness Airport", "Birmingham International",
           "Manchester Airport", "Builth Road", "Clarbeston Road", "Harling Road", "Knockholt", "Edinburgh Gateway", "Liverpool South Parkway", "Haddenham and Thame Parkway", "London City Airport"):
    s = st[st["name"] == nm]
    assert len(s), nm
    R.setdefault("st", {})[re.sub(r"\W+", "_", nm.lower())] = srow(s.iloc[0])
st[["name", "crs", "national_rail", "lon", "lat", "osm", "sname", "sq", "stype", "spop", "slon", "slat", "km", "edge_km", "kind2", "n_same"]].rename(
    columns={"sname": "namesake", "sq": "namesake_qid", "stype": "namesake_type", "spop": "namesake_pop", "slon": "namesake_lon", "slat": "namesake_lat", "kind2": "kind"}).round(5).to_csv(f"{DATA}/stations.csv", index=False)
M[["name", "crs", "osm", "key", "sname", "sq", "km", "verdict", "reason"]].rename(columns={"sname": "namesake", "sq": "namesake_qid"}).round(3).to_csv(f"{DATA}/station_namesakes_all.csv", index=False)

# ======================= map data
feats = []
for _, r in best.iterrows():
    feats.append(["a", r.iata, r.label, round(r.lon, 4), round(r.lat, 4), r.place, round(r.plon, 4), round(r.plat, 4), round(float(r.km), 1),
                  r.country, None if pd.isna(r.pax) else int(r.pax), None if pd.isna(r["pop"]) else int(r["pop"]), r.source,
                  r.marketed_as if isinstance(r.marketed_as, str) else "", int(bool(r.secondary)), r.airport_qid if "airport_qid" in r else r.qid,
                  r.place_qid if not str(r.place_qid).startswith("ne:") else ""])
for _, r in st.iterrows():
    feats.append(["s", r.crs, r["name"], round(r.lon, 5), round(r.lat, 5), r.sname, round(r.slon, 5), round(r.slat, 5), round(float(r.km), 2),
                  "United Kingdom", None, None if pd.isna(r.spop) else int(r.spop), r.kind2, "", int(bool(r.national_rail)), r.osm, r.sq])
jsave({"fields": ["t", "code", "name", "lon", "lat", "place", "plon", "plat", "km", "country", "pax", "pop", "src", "marketed", "flag", "id", "pid"], "f": feats}, f"{DATA}/map.json")
jsave(R, f"{DATA}/results.json", indent=1)
print(json.dumps({k: R[k] for k in ("air_review", "air_n", "st_review", "st_n", "road", "parkway", "air_median_km", "st_median_km")}, indent=0, ensure_ascii=False))
