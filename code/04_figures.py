"""Step 4: figures for the page (img/*.jpg), the blog (release/blog/b_*.png, 1800 px) and the paper (release/paper/f_*.png)."""
import warnings
warnings.filterwarnings("ignore")
import pandas as pd
from PIL import Image
from figstyle import *

R = jload(f"{DATA}/results.json")
A = pd.read_csv(f"{DATA}/airports.csv", keep_default_na=False, na_values=[""])
S = pd.read_csv(f"{DATA}/stations.csv", keep_default_na=False, na_values=[""])
MAP = jload(f"{DATA}/map.json")
F = pd.DataFrame(MAP["f"], columns=MAP["fields"])
BLOG, PAPERD = f"{ROOT}/release/blog", f"{ROOT}/release/paper"
for d in (BLOG, PAPERD):
    os.makedirs(d, exist_ok=True)


def out(fig, name, dpi=200):
    fig.savefig(f"{WORK}/{name}.png", dpi=dpi, facecolor=fig.get_facecolor())
    plt.close(fig)
    im = Image.open(f"{WORK}/{name}.png").convert("RGB")
    im.resize((1600, round(im.size[1] * 1600 / im.size[0])), Image.LANCZOS).save(f"{IMG}/{name}.jpg", quality=84, optimize=True)
    im.resize((1800, round(im.size[1] * 1800 / im.size[0])), Image.LANCZOS).save(f"{BLOG}/b_{name}.png", optimize=True)
    w = min(2000, im.size[0]); im.resize((w, round(im.size[1] * w / im.size[0])), Image.LANCZOS).save(f"{PAPERD}/f_{name}.png", optimize=True)
    os.remove(f"{WORK}/{name}.png")


short = lambda s: s.replace(" Airport", "").replace(" International", "").replace("Airport ", "")

# ---------------------------------------------------------------- 1. Europe map
fig = plt.figure(figsize=(12, 8.4)); fig.patch.set_facecolor(PAPER)
ax = fig.add_axes([0.01, 0.06, 0.64, 0.8])
f = plain_base(ax, 3035, (-10.5, 27.5, 41.0, 61.5))
E = F[(F.t == "a")].copy()
E = E.merge(A[["iata", "lon", "lat"]].rename(columns={"iata": "code"}), on=["code", "lon", "lat"], how="left")
eu = A[(A.km >= 30)]
eu = eu[eu.lon.between(-12, 30) & eu.lat.between(40, 63)].sort_values("km")
for _, r in eu.iterrows():
    x0, y0 = f(r.lon, r.lat); x1, y1 = f(r.lon + 0, r.lat + 0)
    pr = F[(F.t == "a") & (F.code == r.iata)].iloc[0]
    x1, y1 = f(pr.plon, pr.plat)
    c = km_colour(r.km)
    ax.plot([x0, x1], [y0, y1], color=c, lw=1.2 + r.km / 45, solid_capstyle="round", zorder=5, alpha=0.95)
    ax.scatter([x1], [y1], s=16, color="white", edgecolor=INKC, lw=0.8, zorder=6)
    ax.scatter([x0], [y0], s=26, color=c, edgecolor="white", lw=0.8, zorder=7)
top = R["air_europe"][:12]
lst = []
for i, t in enumerate(top, 1):
    r = A[A.iata == t["iata"]].iloc[0]
    x0, y0 = f(r.lon, r.lat)
    ax.text(x0, y0, f" {i}", fontsize=11, family=MONO, color=INKC, fontweight="bold", va="center", ha="left", zorder=9, path_effects=HALO)
    nm = t["marketed"] or short(t["label"])
    lst.append((i, nm, t["place"], t["km"]))
ax2 = fig.add_axes([0.665, 0.07, 0.31, 0.83]); ax2.axis("off")
ax2.text(0, 0.985, "Farthest from the city\non the ticket, Europe", fontsize=15, fontweight=600, color=INKC, va="top")
for j, (i, nm, pl, k) in enumerate(lst):
    y = 0.86 - j * 0.06
    ax2.text(0, y, f"{i:>2}", family=MONO, fontsize=12, color=RED, fontweight="bold", va="top")
    ax2.text(0.09, y, nm, fontsize=12.2, color=INKC, va="top")
    ax2.text(0.09, y - 0.028, f"to {pl}: {k:.0f} km", family=MONO, fontsize=10.2, color=MUT, va="top")
yy = 0.86 - len(lst) * 0.06 - 0.01
ax2.plot([0.0, 0.08], [yy, yy], color=km_colour(100), lw=3.5); ax2.text(0.1, yy, "airport to the city it names", fontsize=10.5, color=MUT, va="center")
ax2.scatter([0.04], [yy - 0.04], s=26, color="white", edgecolor=INKC); ax2.text(0.1, yy - 0.04, "the city (Wikidata point)", fontsize=10.5, color=MUT, va="center")
ax2.text(0.0, yy - 0.075, "Lines: every named airport 30 km or\nmore from its city; colour and\nthickness show the distance.", fontsize=10.5, color=MUT, va="top")
ax2.set_xlim(0, 1); ax2.set_ylim(0, 1)
title(fig, "Not where it says on the ticket", "European airports named after a city 30 km or more away, Wikidata and airline names")
foot(fig, "Data: Wikidata (CC0), names sold by airlines as listed in the paper; Natural Earth. maps.tristanhotham.com/far-from-home")
out(fig, "europe")

# ---------------------------------------------------------------- 2. world ranking
W = R["air_world"]
fig, ax = plt.subplots(figsize=(12, 8.2)); fig.patch.set_facecolor(PAPER)
fig.subplots_adjust(left=0.36, right=0.95, top=0.79, bottom=0.13)
ys = np.arange(len(W))[::-1]
for y, t in zip(ys, W):
    c = RED if t["secondary"] else BLUE
    ax.barh(y, t["km"], color=c, height=0.68, alpha=0.9)
    ax.text(t["km"] + 1.5, y, f"{t['km']:.0f} km", va="center", family=MONO, fontsize=11, color=INKC)
    nm = (t["marketed"] or short(t["label"])) + f" ({t['iata']})"
    ax.text(-2, y + 0.13, nm, ha="right", va="center", fontsize=12.2, color=INKC)
    ax.text(-2, y - 0.25, f"to {t['place']}, {t['country']}", ha="right", va="center", fontsize=9.6, color=MUT, family=MONO)
ax.set_yticks([]); ax.set_xlim(0, 160); ax.set_xlabel("Straight-line distance from the airport to the city's point (km)")
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
ax.grid(axis="x", color="#E3E1DA", lw=0.8); ax.set_axisbelow(True)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=RED, label="another airport named after the same city is closer to it"), Patch(color=BLUE, label="no closer airport carries the city's name")],
          loc="lower left", bbox_to_anchor=(-0.02, 1.0), ncol=2, frameon=False, fontsize=10.5)
title(fig, "The farthest airports from the city they name", "Airports with an IATA code, named after a city in Wikidata or by the airlines that sell them; every case checked by eye")
foot(fig, "Data: Wikidata (CC0); airline names as listed in the paper. maps.tristanhotham.com/far-from-home")
out(fig, "world")

# ---------------------------------------------------------------- 3. distribution
fig, ax = plt.subplots(figsize=(12, 6.4)); fig.patch.set_facecolor(PAPER)
fig.subplots_adjust(left=0.08, right=0.96, top=0.8, bottom=0.17)
bins = np.r_[0, np.arange(2, 150, 2)]
ax.hist(A.km.clip(upper=149), bins=bins, color=BLUE, alpha=0.85, edgecolor=PAPER, lw=0.5)
med = R["air_median_km"]
ax.axvline(med, color=INKC, lw=1, ls=(0, (3, 2)))
ax.text(med + 1.2, ax.get_ylim()[1] * 0.92, f"median {med:.1f} km", family=MONO, fontsize=11, color=INKC)
for k in ("HHN", "FMM", "BVA", "OXF", "STN", "LHR"):
    t = R["air"][k]
    ax.annotate(f"{t['marketed'] or short(t['label'])}\n{t['km']:.0f} km", xy=(t["km"], 0), xytext=(t["km"] + (9 if k == "HHN" else 0), ax.get_ylim()[1] * {"FMM": 0.62, "STN": 0.42, "OXF": 0.42, "HHN": 0.25, "BVA": 0.25, "LHR": 0.25}[k]),
                ha="center", fontsize=10, color=RED, arrowprops=dict(arrowstyle="-", color=RED, lw=0.8))
ax.set_xlabel("Distance from airport to the city it is named after (km)"); ax.set_ylabel("Airports")
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.set_xlim(0, 150)
title(fig, "Most airports sit near their namesake", f"{R['air_n']['ranked']:,} airports with an IATA code named after a place; {R['air_over30_pc']:.0f}% are more than 30 km away")
foot(fig, "Data: Wikidata (CC0). maps.tristanhotham.com/far-from-home")
out(fig, "spread")

# ---------------------------------------------------------------- 4. UK stations map
fig = plt.figure(figsize=(12, 13)); fig.patch.set_facecolor(PAPER)
ax = fig.add_axes([0.0, 0.04, 0.62, 0.86])
f = plain_base(ax, 27700, (-8.3, 2.0, 49.9, 58.9))
s0 = S.sort_values("km")
x, y = f(s0.lon.values, s0.lat.values)
cols = [km_colour(k * 20) for k in s0.km]
ax.scatter(x, y, s=np.where(s0.km >= 3, 22, 4), c=cols, lw=0, zorder=5, alpha=0.9)
TOP = [t for t in R["st_edge"][:10]]
for i, t in enumerate(TOP, 1):
    r = S[S["name"] == t["name"]].iloc[0]
    xx, yy = f(r.lon, r.lat); x1, y1 = f(r.namesake_lon, r.namesake_lat)
    ax.plot([xx, x1], [yy, y1], color=RED, lw=1.6, zorder=6)
    ax.scatter([xx], [yy], s=40, color=RED, edgecolor="white", zorder=7)
    ax.text(xx, yy, f" {i}", fontsize=11, family=MONO, color=INKC, fontweight="bold", va="center", zorder=9, path_effects=HALO)
ax2 = fig.add_axes([0.63, 0.04, 0.35, 0.86]); ax2.axis("off")
ax2.text(0, 0.985, "Stations farthest beyond\nthe town they name", fontsize=15, fontweight=600, color=INKC, va="top")
for j, t in enumerate(TOP):
    yy = 0.9 - j * 0.058
    ax2.text(0, yy, f"{j + 1:>2}", family=MONO, fontsize=12, color=RED, fontweight="bold", va="top")
    ax2.text(0.09, yy, t["name"], fontsize=12.2, color=INKC, va="top")
    ax2.text(0.09, yy - 0.024, f"{t['km']:.1f} km from {t['place']}", family=MONO, fontsize=10.2, color=MUT, va="top")
yy = 0.9 - len(TOP) * 0.058 - 0.02
for k, lab in ((0.3, "under 1 km"), (2.0, "2 km"), (5, "5 km or more")):
    ax2.scatter([0.03], [yy], s=22 if k >= 3 else 8, color=km_colour(k * 20)); ax2.text(0.09, yy, lab, fontsize=10.5, color=MUT, va="center"); yy -= 0.03
ax2.set_xlim(0, 1); ax2.set_ylim(0, 1)
ax2.text(0, yy - 0.01, f"Every dot is one of {R['st_n']['matched']:,} stations whose\nname starts with a town or village.\nRanked by distance beyond a notional\ncircle round the town, sized by\nits population. Stations named\nafter an airport are left out.", fontsize=10.5, color=MUT, va="top")
title(fig, "Stations named after somewhere else", "UK railway stations and the town, village or city in their name; most are within a kilometre")
foot(fig, "Data: OpenStreetMap contributors (ODbL), Wikidata (CC0), Natural Earth. maps.tristanhotham.com/far-from-home")
out(fig, "stations_map")

# ---------------------------------------------------------------- 5. stations bars: road, parkway, airport
fig, axs = plt.subplots(1, 3, figsize=(13.5, 6.6)); fig.patch.set_facecolor(PAPER)
fig.subplots_adjust(left=0.13, right=0.98, top=0.76, bottom=0.16, wspace=0.95)
groups = [("Road stations", R["road_list"][:8]), ("Parkways", R["parkway_list"][:8]), ("Airport stations", [x for x in R["st_top"] if x["kind"] == "airport"][:6])]
for ax, (lab, L) in zip(axs, groups):
    L = L[::-1]
    ys = np.arange(len(L))
    ax.barh(ys, [t["km"] for t in L], color=[km_colour(t["km"] * 10) for t in L], height=0.66)
    for y, t in zip(ys, L):
        ax.text(t["km"] + 0.2, y, f"{t['km']:.1f}", va="center", family=MONO, fontsize=10, color=INKC)
    ax.set_yticks(ys); ax.set_yticklabels([t["name"].replace(" Parkway", "").replace(" Road", "") for t in L], fontsize=11)
    ax.set_title(lab, loc="left", fontsize=14, fontweight=600, color=INKC)
    ax.set_xlim(0, max(t["km"] for t in L) * 1.25)
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0); ax.set_xlabel("km to the town's point", fontsize=10.5)
title(fig, "Road, Parkway and Airport", "How far UK stations of each kind stand from the place in their name (straight line, km)")
foot(fig, "Data: OpenStreetMap contributors (ODbL), Wikidata (CC0). maps.tristanhotham.com/far-from-home")
out(fig, "kinds")

# ---------------------------------------------------------------- 6. data checks
fig, ax = plt.subplots(figsize=(12, 4.6)); fig.patch.set_facecolor(PAPER)
fig.subplots_adjust(left=0.27, right=0.97, top=0.7, bottom=0.24)
ra, rs = R["air_review"], R["st_review"]
rows = [("Airport named places\n40 km or more away", [("kept", ra["ok"], BLUE), ("wrong link or point", ra["wrong"], RED), ("a region or island", ra["region"], GOLD), ("unsure, left out", ra["unsure"], "#A3A3AD")], ra["n"]),
        ("Station name matches\n3 km or more away", [("kept", rs["ok"], BLUE), ("another place, or a street", rs["homonym"] + rs["street"], RED), ("wrong point", rs["coord"], GOLD), ("unsure, left out", rs["unsure"], "#A3A3AD")], rs["n"])]
for y, (lab, parts, n) in zip((1, 0), rows):
    x = 0
    for nm, v, c in parts:
        ax.barh(y, 100 * v / n, left=x, color=c, height=0.55)
        if 100 * v / n > 6:
            ax.text(x + 50 * v / n, y, f"{v}", ha="center", va="center", color="white", family=MONO, fontsize=11, fontweight="bold")
        x += 100 * v / n
    ax.text(-2, y, lab, ha="right", va="center", fontsize=12, color=INKC)
handles = [Patch(color=BLUE, label="kept"), Patch(color=RED, label="wrong link, another place or a street"), Patch(color=GOLD, label="a region, island or wrong point"), Patch(color="#A3A3AD", label="unsure, left out")]
ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.4, -0.12), ncol=4, frameon=False, fontsize=10.5)
ax.set_xlim(0, 100); ax.set_yticks([]); ax.set_xticks([])
for s in ax.spines.values(): s.set_visible(False)
title(fig, "Where the errors hide", f"Every long-distance case was read by eye: {ra['corrected_pc']:.0f}% of the airport cases and {rs['corrected_pc']:.0f}% of the station cases were not what they seemed", size=24)
foot(fig, "Data: Wikidata (CC0), OpenStreetMap contributors (ODbL). maps.tristanhotham.com/far-from-home")
out(fig, "checks")
print("figures done")
