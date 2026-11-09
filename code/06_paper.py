"""Step 6: the paper. Fills code/paper_template.tex from data/results.json, adds tables, compiles with xelatex.
Output: release/paper/Hotham_Not_Where_It_Says_on_the_Ticket.pdf and .tex beside the f_*.png figures.
The DOI stays a placeholder: the publisher reruns  DOI=10.5281/zenodo.N python3 code/06_paper.py  then 08_release.py."""
import subprocess
import pandas as pd
from common import *

R = jload(f"{DATA}/results.json")
A = pd.read_csv(f"{DATA}/airports.csv", keep_default_na=False, na_values=[""])
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Not_Where_It_Says_on_the_Ticket"
tex = lambda s: str(s).replace("\\", "").replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#").replace("$", "\\$")
# facts stated in words
C = R["air_by_continent"]
order = sorted(C, key=lambda k: C[k]["median"])
assert order[:2] == ["South America", "Africa"] and order[-2:] == ["Europe", "Asia"], order
assert sum(w["secondary"] for w in R["air_world"]) == R["air_world_secondary_n"] == 12 and R["air_world"][14]["iata"] == "RZV"
assert max(R["air_over50_by_cont"], key=R["air_over50_by_cont"].get) == "Europe"
assert (A.place == "New York City").sum() == 1
assert [x["iata"] for x in R["air_radii"][:2]] == ["MLB", "AZS"] and R["air"]["HHN"]["radii"] == R["air_radii"][R["air_radii_hhn_rank"] - 1]["radii"]
assert abs(A[A.country == "Ireland"].km.max() - R["air_ie_max_km"]) < 0.01


def tfmt(v, f):
    if f == "int": return f"{int(round(float(v))):,}"
    if f == "pc": return f"{round(float(v))}\\%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    if f in ("word", "Word", "ordinal"): return fmt(v, f)
    return tex(str(v))


def atab(L, cap, lab, extra=False):
    rows = "".join(f"{i} & {tex(t['marketed'] or t['label'])} ({t['iata']}) & {tex(t['place'])} & {t['km']:.1f} & {'yes' if t['secondary'] else ''} & {(format(t['pax'], ',') if t['pax'] else '')}\\\\\n" for i, t in enumerate(L, 1))
    return ("\\begin{table}[tbp]\\centering\\small\\caption{" + cap + "}\\label{" + lab + "}\\begin{tabular}{rp{6.2cm}p{2.8cm}rcr}\\toprule & Airport (name sold by airlines in place of the label, where used) & Named after & km & Second & Passengers\\\\\\midrule\n"
            + rows + "\\bottomrule\\end{tabular}\\end{table}")


TW = atab(R["air_world"], "The fifteen airports farthest from the place they are named after (IATA code; kept cases). Second: another airport named after the same city is closer to it. Passengers: largest annual value in Wikidata.", "tab:world")
TU = atab(R["air_ukie"], "Airports in Britain and Ireland farthest from the place they are named after.", "tab:uk")
rows = "".join(f"{k} & {v['n']:,} & {v['median']:.1f}\\\\\n" for k, v in sorted(C.items(), key=lambda kv: kv[1]["median"]))
TC = ("\\begin{table}[tbp]\\centering\\small\\caption{Median distance from airport to namesake by continent (Natural Earth continents; at least 50 airports).}\\label{tab:cont}"
      "\\begin{tabular}{lrr}\\toprule Continent & Airports & Median km\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = "".join(f"{i} & {tex(t['name'])} & {tex(t['crs'])} & {tex(t['place'])} & {t['km']:.1f} & {max(0, t['edge_km']):.1f}\\\\\n" for i, t in enumerate(R["st_edge"], 1))
TS = ("\\begin{table}[tbp]\\centering\\small\\caption{UK stations farthest beyond a notional circle round the settlement in their name (3,000 people per km$^2$). km: from the settlement's point.}\\label{tab:st}"
      "\\begin{tabular}{rllp{3.2cm}rr}\\toprule & Station & CRS & Named after & km & Beyond circle\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
MK = pd.read_csv(os.path.join(ROOT, "code", "marketing_names.csv"))
rows = "".join(f"{r.iata} & {tex(r.marketed_as)} & {tex(r.city)} & {R['air'].get(r.iata, {}).get('km', float('nan')):.1f} & {tex(r.note)}\\\\\n" for r in MK.itertuples())
TM = ("\\begin{small}\\begin{longtable}{lp{3.2cm}lrp{6.4cm}}\\caption{Names under which airlines have sold secondary airports, used as namesakes in addition to the data (from the author's knowledge, each checked against airline or airport listings). km: distance in the data.}\\label{tab:mk}\\\\"
      "\\toprule IATA & Sold as & City & km & Note\\\\\\midrule\\endhead\n" + rows + "\\bottomrule\\end{longtable}\\end{small}")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
t = t.replace("{{AI}}", AI).replace("{{TABLE_WORLD}}", TW).replace("{{TABLE_UK}}", TU).replace("{{TABLE_CONT}}", TC).replace("{{TABLE_ST}}", TS).replace("{{TABLE_MK}}", TM)
t = re.sub(r"\{\{(?!TABLE_|DOI)([^}|]+)(\|(\w+))?\}\}", lambda m: tfmt(get(R, m.group(1)), m.group(3) or "raw"), t)
DOI = os.environ.get("DOI")
t = t.replace("https://doi.org/10.5281/zenodo.24087597", f"\\url{{https://doi.org/{DOI}}}" if DOI else "\\{\\{DOI\\_URL\\}\\}")
assert "{{" not in t and "--" not in t and "—" not in t and "–" not in t
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Overfull" in l or l.startswith("!")][:12])
for ext in (".aux", ".log", ".out", ".bbl", ".blg"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
print("paper", r.returncode, len(txt.split()), "words;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("—") + txt.count("–") + txt.count("--"))
