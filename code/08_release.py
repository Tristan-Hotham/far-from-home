"""Step 8: blog post and meta (release/blog), Zenodo files and metadata (release/zenodo).
10.5281/zenodo.24087597, https://doi.org/10.5281/zenodo.24087597 and https://blog.tristanhotham.com/2026/10/31/far-from-home/ stay as placeholders for the publisher."""
import shutil, zipfile, importlib.util
from PIL import Image
from common import *

spec = importlib.util.spec_from_file_location("b", os.path.join(ROOT, "code", "05_build_site.py"))
spec.loader.exec_module(importlib.util.module_from_spec(spec))          # shared fact checks (and rebuilds index.html)
R = jload(f"{DATA}/results.json")
REL = os.path.join(ROOT, "release"); NAME = "Hotham_Not_Where_It_Says_on_the_Ticket"
KEEP = {"DOI", "DOI_URL", "BLOG_URL"}
assert all(85 <= R["air"][k]["km"] <= 95 for k in ("RDO", "OXF", "NYO", "SWF", "REU"))
assert sum(w["secondary"] for w in R["air_world"]) == R["air_world_secondary_n"]

post = fill(open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read(), R)
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
assert 5 <= len(used) <= 8, len(used)
assert all(re.search(r"^\{\{IMG\|" + re.escape(u_), post, re.M) for u_ in used) and "wp:image" not in post
for img in used:
    assert Image.open(f"{REL}/blog/{img}").size[0] == 1800, img
for fn in os.listdir(f"{REL}/blog"):
    if fn.startswith("b_") and fn not in used:
        os.remove(f"{REL}/blog/{fn}")
assert set(re.findall(r"\{\{([^|}]+)\}\}", post)) <= KEEP, set(re.findall(r"\{\{([^|}]+)\}\}", post))
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
for bad in ("\u2014", "\u2013", "--", "DSIT", "DCMS", "civil serv"):
    assert bad not in vis, bad
assert AI in post
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
a = R["air"]
meta = {"title": "Not where it says on the ticket: the airports and stations far from their namesake",
        "slug": "far-from-home",
        "excerpt": f"Frankfurt-Hahn is {a['HHN']['km']:.0f} km from Frankfurt and Paris Vatry {a['XCR']['km']:.0f} km from Paris. I measured how far every airport and every UK railway station stands from the place in its name, and checked every long case by hand.",
        "seo_description": f"How far airports and UK stations stand from their namesake: Paris Vatry {a['XCR']['km']:.0f} km from Paris, Hahn {a['HHN']['km']:.0f} km from Frankfurt, Dent and Llanbister Road.",
        "tags": ["maps", "airports", "railways", "place names", "low-cost airlines", "Wikidata", "OpenStreetMap", "data visualisation"],
        "header_alt": f"Title card reading 'Not where it says on the ticket' beside two small maps with lines from Frankfurt-Hahn to Frankfurt, {a['HHN']['km']:.0f} km, and from Paris Vatry to Paris, {a['XCR']['km']:.0f} km."}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
jsave(meta, f"{REL}/blog/meta.json", indent=2)

Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)
for fn in os.listdir(Z):
    os.remove(os.path.join(Z, fn))
shutil.copy(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/{SLUG}_data_and_code.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for dd in ("code", "js"):
        for fn in sorted(os.listdir(os.path.join(ROOT, dd))):
            if fn.endswith(".pyc") or fn == "__pycache__" or fn.endswith(".png"):
                continue
            z.write(os.path.join(ROOT, dd, fn), f"{SLUG}/{dd}/{fn}")
    for fn in sorted(os.listdir(os.path.join(ROOT, "data"))):
        z.write(os.path.join(ROOT, "data", fn), f"{SLUG}/data/{fn}")
    for fn in ("README.md", "LICENSE", "index.html"):
        z.write(os.path.join(ROOT, fn), f"{SLUG}/{fn}")
    z.write(os.path.join(ROOT, "reddit", "collage.py"), f"{SLUG}/reddit/collage.py")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = ab.replace("\\%", "%").replace("\\&", "&").replace("``", "\u201c").replace("''", "\u201d")
assert "\\" not in ab and "$" not in ab, ab
zmeta = {"title": "Not Where It Says on the Ticket: Airports and Railway Stations Far from the Places They Are Named After",
         "upload_type": "publication", "publication_type": "workingpaper",
         "description": f"<p>{ab}</p><p>Interactive page: <a href=\"{PAGE}\">{PAGE}</a>. Data and code: <a href=\"{REPO}\">{REPO}</a>. Blog post: {{https://blog.tristanhotham.com/2026/10/31/far-from-home/}}.</p><p>Sources: Wikidata (CC0), queried with QLever; OpenStreetMap contributors (ODbL); Natural Earth (public domain). Station tables derived from OpenStreetMap are released under the Open Database Licence; airport tables CC0; text and figures CC BY 4.0; code MIT.</p>",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "keywords": ["airports", "railway stations", "place names", "secondary airports", "low-cost airlines", "Wikidata", "OpenStreetMap", "data quality"],
         "license": "cc-by-4.0", "language": "eng",
         "notes": "Text and figures CC BY 4.0; code MIT; station tables derived from OpenStreetMap, ODbL; airport tables from Wikidata, CC0.",
         "related_identifiers": [{"identifier": REPO, "relation": "isSupplementedBy", "resource_type": "software"},
                                 {"identifier": PAGE, "relation": "isSupplementedBy", "resource_type": "other"},
                                 {"identifier": "https://www.wikidata.org/", "relation": "isDerivedFrom", "resource_type": "dataset"},
                                 {"identifier": "https://www.openstreetmap.org/", "relation": "isDerivedFrom", "resource_type": "dataset"}],
         "files": sorted(os.listdir(Z))}
sj = json.dumps(zmeta, ensure_ascii=False) + json.dumps(meta, ensure_ascii=False)
assert "\u2014" not in sj and "\u2013" not in sj and "--" not in sj
jsave(zmeta, f"{Z}/metadata.json", indent=2)
print("blog words", words, "figures", len(used), "; zenodo", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")
