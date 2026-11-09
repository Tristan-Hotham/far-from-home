"""Step 5: index.html from code/page_template.html, filled from data/results.json, with the facts stated in words checked.
10.5281/zenodo.24087597, https://doi.org/10.5281/zenodo.24087597 and https://blog.tristanhotham.com/2026/10/31/far-from-home/ stay as placeholders for the publisher."""
import time
import pandas as pd
from common import *

R = jload(f"{DATA}/results.json")
A = pd.read_csv(f"{DATA}/airports.csv", keep_default_na=False, na_values=[""])
W = R["air_world"]
# facts stated in words
assert W[0]["iata"] == "XCR" and [w["iata"] for w in W[1:8]] == ["RFD", "DEJ", "HHN", "FMM", "WGN", "RDO", "OXF"]
assert sum(not w["secondary"] for w in W) == 3 and W[5]["iata"] == "WGN" and W[14]["iata"] == "RZV" and not W[14]["secondary"]
assert R["air"]["SWF"]["km"] > R["air"]["REU"]["km"] - 1 and W[9]["iata"] == "SWF"
assert [x["iata"] for x in R["air_ukie"][:7]] == ["OXF", "SEN", "STN", "PIK", "LTN", "LGW", "DSA"]
ie = A[A.country == "Ireland"]
assert abs(ie.km.max() - R["air_ie_max_km"]) < 0.01
assert R["air"]["LHR"]["km"] < R["air"]["LGW"]["km"]
assert [x["name"] for x in R["st_edge"][:5]] == ["Tiverton Parkway", "Llanbister Road", "Dent", "Beaulieu Road", "Irton Road"]
assert all(x["kind"] != "airport" for x in R["st_edge"])
assert [x["name"] for x in R["st_top"][:4]] == ["Manchester Airport", "Birmingham International", "London City Airport", "Inverness Airport"]
assert [x["name"] for x in R["road_list"]] == ["Llanbister Road", "Beaulieu Road", "Irton Road", "Roughton Road", "Wittersham Road", "Builth Road", "Clarbeston Road", "Farningham Road", "Harling Road"]
assert R["road"]["away2"] == 9 and R["air_review"]["n"] > 100


def a_rows(L):
    out = []
    for t in L:
        nm = f"<i>{t['marketed']}</i>" if t["marketed"] else t["label"].replace(" Airport", "")
        pax = f"{t['pax']:,}" if t["pax"] else ""
        out.append(f'<tr><td><a onclick="__go(\'{t["iata"]}\')">{nm}</a> ({t["iata"]})</td><td>{t["place"]}</td><td class="r">{t["km"]:.0f}</td><td class="r">{pax}</td></tr>')
    return "\n".join(out)


def s_rows(L):
    return "\n".join(f'<tr><td><a onclick="__go(\'{t["name"]}\')">{t["name"]}</a></td><td>{t["place"]}</td><td class="r">{t["km"]:.1f}</td><td class="r">{max(0, t["edge_km"]):.1f}</td></tr>' for t in L)


t = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
fs = open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read()
t = t.replace("{{FULLSCREEN}}", fs).replace("{{TABLE_EUROPE}}", a_rows(R["air_europe"])).replace("{{TABLE_UK}}", a_rows(R["air_ukie"][:8]))
t = t.replace("{{TABLE_ST}}", s_rows(R["st_edge"][:10]))
t = t.replace("{{REPO}}", REPO).replace("{{BYLINE}}", BYLINE).replace("{{AI}}", AI).replace("{{VERSION}}", time.strftime("%Y%m%d"))
t = fill(t, R)
from PIL import Image
t = re.sub(r'<img src="img/([\w.]+)" width="\d+" height="\d+"', lambda m: '<img src="img/%s" width="%d" height="%d"' % ((m.group(1),) + Image.open(f"{IMG}/{m.group(1)}").size), t)
assert set(re.findall(r"\{\{([^}]+)\}\}", t)) <= {"DOI", "DOI_URL", "BLOG_URL"}, set(re.findall(r"\{\{([^}]+)\}\}", t))
vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", t, flags=re.S)
for bad in ("—", "–", "--", "DSIT", "DCMS", "civil serv"):
    assert bad not in vis, bad
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(t)
js = open(os.path.join(ROOT, "js", "page.js"), encoding="utf-8").read()
assert "—" not in js and "–" not in js
print("index.html", len(t) // 1024, "KB")
