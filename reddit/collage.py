"""Reddit collage (r/dataisbeautiful style) and the 1200 x 630 header card.
Light background; small maps all at one scale with names in the panel titles (no labels on land); full legend; source footer.
Output: reddit/far_from_home_collage.png (3000 x 2100 px) and header.png. Run after code/04_figures.py."""
import os, sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code"))
import pandas as pd
from matplotlib import font_manager as fm
from shapely.geometry import shape, box
from shapely.ops import transform as stransform
from figstyle import *

R = jload(f"{DATA}/results.json")
A = pd.read_csv(f"{DATA}/airports.csv", keep_default_na=False, na_values=[""])
MAP = jload(f"{DATA}/map.json")
F = pd.DataFrame(MAP["f"], columns=MAP["fields"])
C10 = [shape(f["geometry"]) for f in jload(f"{GEO}/ne_10m_admin_0_countries.geojson")["features"]]
OUT = os.path.join(ROOT, "reddit", "far_from_home_collage.png")
FR = lambda size, w="bold": fm.FontProperties(fname=f"{FONTS}/FrauncesVar.ttf", size=size, weight=w)
HALF = 80e3                                                   # every panel is 160 km across


def panel(ax, code, title, sub):
    r = F[(F.t == "a") & (F.code == code)].iloc[0]
    lon0, lat0 = (r.lon + r.plon) / 2, (r.lat + r.plat) / 2
    f = projector(f"+proj=aeqd +lat_0={lat0} +lon_0={lon0} +units=m")
    clip = box(lon0 - 3, lat0 - 2, lon0 + 3, lat0 + 2)
    ax.set_facecolor(SEA)
    for g in C10:
        if not g.intersects(clip): continue
        g = stransform(f, g.intersection(clip))
        patches(ax, g, fc=LAND, ec="none", zorder=1)
        lines(ax, g, color=BORDER, lw=0.8, zorder=2)
    x0, y0 = f(r.lon, r.lat); x1, y1 = f(r.plon, r.plat)
    c = km_colour(r.km)
    ax.plot([x0, x1], [y0, y1], color=c, lw=5, solid_capstyle="round", zorder=4)
    ax.scatter([x1], [y1], s=150, color="white", edgecolor=INKC, lw=2, zorder=5)
    ax.scatter([x0], [y0], s=230, color=c, edgecolor="white", lw=2, zorder=6)
    ax.set_xlim(-HALF, HALF); ax.set_ylim(-HALF, HALF); ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_color("#B9B5AA"); s.set_linewidth(1)
    ax.set_title(title, loc="left", fontproperties=FR(19), color=INKC, pad=30)
    ax.text(0, 1.015, sub, transform=ax.transAxes, fontsize=15, color=c if r.km < 120 else "#7E1B2A", family=MONO, va="bottom", fontweight="bold")
    if sub: ax.texts[-1].set_text(f"{sub}: {r.km:.0f} km")
    return r


def collage():
    fig = plt.figure(figsize=(15, 10.5), dpi=200); fig.patch.set_facecolor(PAPER)
    fig.text(0.035, 0.955, "Not where it says on the ticket", fontproperties=FR(44), color=INKC, va="top")
    fig.text(0.035, 0.885, f"How far airports stand from the city they are named after. Every map is 160 km across.",
             fontsize=17, color=MUT, va="top")
    picks = [("XCR", "Paris Vatry", "to Paris"), ("HHN", "Frankfurt-Hahn", "to Frankfurt"), ("FMM", "Munich West (Memmingen)", "to Munich"),
             ("RDO", "Warsaw Radom", "to Warsaw"), ("OXF", "London Oxford", "to London"), ("NYO", "Stockholm Skavsta", "to Stockholm"),
             ("REU", "Barcelona Reus", "to Barcelona"), ("TRF", "Oslo Torp", "to Oslo"), ("BVA", "Paris Beauvais", "to Paris")]
    W, H, x0, y0, gx, gy = 0.17, 0.17, 0.035, 0.62, 0.019, 0.075
    for i, (code, t, s) in enumerate(picks):
        ax = fig.add_axes([x0 + (i % 3) * (W + gx), y0 - (i // 3) * (H + gy), W, H])
        panel(ax, code, t, s)
    # right column: world bars
    ax = fig.add_axes([0.73, 0.42, 0.24, 0.36])
    Wd = R["air_world"][:10][::-1]
    ys = np.arange(len(Wd))
    ax.barh(ys, [t["km"] for t in Wd], color=[km_colour(t["km"]) for t in Wd], height=0.66)
    for y, t in zip(ys, Wd):
        ax.text(t["km"] + 2, y, f"{t['km']:.0f}", va="center", family=MONO, fontsize=13, color=INKC)
        ax.text(-3, y, (t["marketed"] or t["label"].replace(" International", "").replace(" Airport", "")).replace(" (Munich West)", ""), ha="right", va="center", fontsize=13.5, color=INKC)
    ax.set_xlim(0, 150); ax.set_yticks([]); ax.set_xticks([])
    for s in ax.spines.values(): s.set_visible(False)
    fig.text(0.62, 0.80, "World: farthest from the city they name (km)", fontsize=16, color=INKC)
    # stations
    ax = fig.add_axes([0.73, 0.13, 0.24, 0.21])
    St = sorted(R["st_edge"][:6], key=lambda t: t["km"])
    ys = np.arange(len(St))
    ax.barh(ys, [t["km"] for t in St], color=[km_colour(t["km"] * 10) for t in St], height=0.62)
    for y, t in zip(ys, St):
        ax.text(t["km"] + 0.15, y, f"{t['km']:.1f}", va="center", family=MONO, fontsize=13, color=INKC)
        ax.text(-0.3, y, t["name"], ha="right", va="center", fontsize=13.5, color=INKC)
    ax.set_xlim(0, 15); ax.set_yticks([]); ax.set_xticks([])
    for s in ax.spines.values(): s.set_visible(False)
    fig.text(0.62, 0.36, "UK stations farthest beyond their town (km)", fontsize=16, color=INKC)
    # legend and facts
    lg = fig.add_axes([0.035, 0.05, 0.9, 0.035]); lg.axis("off"); lg.set_xlim(0, 1); lg.set_ylim(0, 1)
    lg.scatter([0.01], [0.6], s=230, color=km_colour(100), edgecolor="white", lw=2); lg.text(0.03, 0.6, "airport", va="center", fontsize=14, color=INKC)
    lg.scatter([0.14], [0.6], s=150, color="white", edgecolor=INKC, lw=2); lg.text(0.16, 0.6, "the city it is named after (Wikidata point)", va="center", fontsize=14, color=INKC)
    lg.text(0.47, 0.6, "darker colour: farther away. Stations named after an airport left out.", va="center", fontsize=14, color=MUT)
    lg.text(0.0, -0.25, f"Half of {R['air_n']['ranked']:,} airports are within {R['air_median_km']:.1f} km of their namesake; half of UK stations within {R['st_median_km']:.1f} km. "
            f"{R['air_review']['corrected_pc']:.0f}% of airport cases over 40 km were wrong or unresolved, fixed by hand.", fontsize=13, color=MUT, va="center")
    fig.text(0.035, 0.012, "Data: Wikidata (CC0), OpenStreetMap contributors (ODbL), Natural Earth.  maps.tristanhotham.com/far-from-home",
             fontsize=12, family=MONO, color=MUT)
    fig.savefig(OUT, dpi=200, facecolor=PAPER)
    plt.close(fig)


def header():
    fig = plt.figure(figsize=(6, 3.15), dpi=200); fig.patch.set_facecolor(PAPER)
    fig.text(0.05, 0.84, "Not where it says\non the ticket", fontproperties=FR(25), color=INKC, va="top", linespacing=1.0)
    fig.text(0.05, 0.43, f"Frankfurt-Hahn is {R['air']['HHN']['km']:.0f} km\nfrom Frankfurt. Paris Vatry is\n{R['air']['XCR']['km']:.0f} km from Paris.", fontsize=11.5, color=INKC, va="top", linespacing=1.3)
    fig.text(0.05, 0.08, "Airports and UK stations far from their namesake", fontsize=8, color=MUT, family=MONO)
    for i, (code, t) in enumerate([("HHN", "Frankfurt-Hahn"), ("XCR", "Paris Vatry")]):
        ax = fig.add_axes([0.53 + i * 0.235, 0.2, 0.215, 0.41])
        r = F[(F.t == "a") & (F.code == code)].iloc[0]
        panel(ax, code, "", "")
        ax.set_title(t, loc="left", fontproperties=FR(9.5), color=INKC, pad=4)
        for tx in ax.texts:
            if tx.get_text().endswith("km"): tx.set_fontproperties(FR(9.5))
            else: tx.set_visible(False)
        for c in ax.collections: c.set_sizes([c.get_sizes()[0] * 0.25])
        for l in ax.lines:
            if l.get_linewidth() == 5: l.set_linewidth(2.4)
    fig.savefig(os.path.join(ROOT, "header.png"), dpi=200, facecolor=PAPER)
    plt.close(fig)


collage(); header()
from PIL import Image
print(Image.open(OUT).size, Image.open(os.path.join(ROOT, "header.png")).size)
