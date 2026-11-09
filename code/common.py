"""Shared paths, constants and helpers for the far-from-home study ("Not where it says on the ticket").

Raw inputs (read in place, never modified):
  AIRPORTS  /home/claude/newdata/raw_new10/airports.tsv.gz: Wikidata airports with an IATA or ICAO code, coordinates, country,
            annual passengers (P3872, every value), and each place served (P931) with its label, coordinates and population
            (P1082). One row per combination of values (queried with QLever, 2026).
  STATIONS  /home/claude/newdata/raw_new10/stations_uk.tsv.gz: OpenStreetMap nodes and ways in the UK tagged railway=station
            or railway=halt, with name, ref:crs where tagged and the first coordinate.
  SETTLE    /home/claude/newdata/raw_new8/uk_settlements.tsv: Wikidata settlements in the UK with coordinates, population and type.
  GEO       Natural Earth 10m countries and populated places (public domain).
Intermediates go to WORK (/home/claude/scratch/far-from-home), outside the repository.
"""
import json, gzip, os, re, math, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.environ.get("FH_RAW", "/home/claude/newdata/raw_new10")
AIRPORTS = os.path.join(RAW, "airports.tsv.gz")
STATIONS = os.path.join(RAW, "stations_uk.tsv.gz")
SETTLE = os.environ.get("FH_SETTLE", "/home/claude/newdata/raw_new8/uk_settlements.tsv")
GEO = os.environ.get("FH_GEO", "/home/claude/newdata/raw/geo")
FONTS = os.environ.get("FH_FONTS", "/home/claude/ref/fonts")
DATA = os.path.join(ROOT, "data")
IMG = os.path.join(ROOT, "img")
WORK = os.environ.get("FH_WORK", "/home/claude/scratch/far-from-home")
for d in (DATA, IMG, WORK):
    os.makedirs(d, exist_ok=True)

SLUG = "far-from-home"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"
REPO = f"https://github.com/Tristan-Hotham/{SLUG}"
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")
BYLINE = "Dr Tristan Hotham · Independent researcher · 2026"


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def dash(v):
    if isinstance(v, str):
        v = re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1 to \2", v)
        v = v.replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ").replace("–", "-")
        while "--" in v:
            v = v.replace("--", "-")
        return v
    if isinstance(v, list):
        return [dash(x) for x in v]
    if isinstance(v, dict):
        return {k: dash(x) for k, x in v.items()}
    return v


def nonan(v):
    if isinstance(v, float) and (v != v or v in (float("inf"), float("-inf"))):
        return None
    if isinstance(v, list):
        return [nonan(x) for x in v]
    if isinstance(v, dict):
        return {k: nonan(x) for k, x in v.items()}
    if hasattr(v, "item"):
        return nonan(v.item())
    return v


def jsave(obj, path, indent=None):
    obj = dash(nonan(obj))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, allow_nan=False, indent=indent, separators=None if indent else (",", ":"))


def get(R, path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f=None):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "pc": return f"{round(float(v))}%"
    if f == "pc1": return f"{float(v):.1f}%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    if f in ("word", "Word"):
        w = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen".split()[int(v)]
        return w.capitalize() if f == "Word" else w
    if f == "ordinal": return "first second third fourth fifth sixth seventh eighth ninth tenth".split()[int(v) - 1]
    raise ValueError(f)


def fill(t, R, keep=("DOI", "DOI_URL", "BLOG_URL"), tf=None):
    """replace {{path|fmt}} tokens from results.json; leave the publisher's placeholders and IMG tokens"""
    f = tf or fmt
    return re.sub(r"\{\{(?!IMG\|)([^{}|]+)(\|(\w+))?\}\}", lambda m: m.group(0) if m.group(1) in keep else f(get(R, m.group(1)), m.group(3)), t)


def read_tsv(path):
    """QLever TSV: header line, IRIs in <...>, literals in "..." (possibly @lang or ^^type)."""
    def lit(s):
        s = s.strip()
        if s.startswith("<") and s.endswith(">"):
            return s[1:-1]
        m = re.match(r'^"(.*)"(?:@[\w-]+|\^\^.*)?$', s, re.S)
        if m:
            return m.group(1).replace('\\"', '"').replace("\\\\", "\\")
        return s
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        head = [h.lstrip("?") for h in f.readline().rstrip("\n").split("\t")]
        for line in f:
            parts = line.rstrip("\n").split("\t")
            parts += [""] * (len(head) - len(parts))
            yield {h: lit(p) for h, p in zip(head, parts)}


def point(wkt):
    """POINT(lon lat), or the first coordinate pair of a LINESTRING or POLYGON prefix"""
    m = re.search(r"(?:POINT|LINESTRING|POLYGON)\s*\(+\s*([-\d.eE]+)\s+([-\d.eE]+)", wkt or "")
    return (float(m.group(1)), float(m.group(2))) if m else (None, None)


def km(lat1, lon1, lat2, lon2):
    import numpy as np
    p1, p2, l1, l2 = map(np.radians, (lat1, lat2, lon1, lon2))
    return 6371.0 * 2 * np.arcsin(np.sqrt(np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin((l2 - l1) / 2) ** 2))


def norm(s):
    """lower case, accents and punctuation removed, single spaces"""
    s = re.sub("[‐-―−]", " ", str(s)).replace("’", "'")   # unicode dashes are word breaks (Milan–Malpensa)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = s.replace("&", " and ").replace("'", "")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s).split())


def qid(iri):
    return iri.rsplit("/", 1)[-1] if iri else ""
