"""House style for the static figures: a plain light map (the look of the page's Positron base map), Fraunces titles,
Source Serif text and IBM Plex Mono numbers; Natural Earth outlines (public domain)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import PathPatch
from matplotlib.path import Path
import matplotlib.patheffects as pe
import numpy as np
from pyproj import Transformer
from shapely.geometry import shape, box
from shapely.ops import transform as stransform, unary_union
from common import *

for f in ("FrauncesVar.ttf", "SourceSerif4-Regular.ttf", "SourceSerif4-Semibold.ttf", "SourceSerif4-It.ttf", "IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf"):
    fm.fontManager.addfont(f"{FONTS}/{f}")
SERIF = "Source Serif 4"
DISPLAY = fm.FontProperties(fname=f"{FONTS}/FrauncesVar.ttf").get_name()
MONO = "IBM Plex Mono"
plt.rcParams.update({"font.family": SERIF, "font.size": 13, "axes.edgecolor": "#8A8A8A", "axes.labelcolor": "#26262B",
                     "xtick.color": "#5C5C66", "ytick.color": "#5C5C66", "axes.facecolor": "none", "axes.unicode_minus": False})
PAPER, SEA, LAND, BORDER, COAST, INKC, MUT = "#FBFAF6", "#E8EEF3", "#F3F1EA", "#C9C5BA", "#A9B4BE", "#26262B", "#6B6B75"
RED, BLUE, GOLD = "#B8322A", "#2E5E8C", "#C98A1B"
# distance ramp for lines (km): pale gold to deep red
RAMP = ["#F2C66D", "#E9A03B", "#D9702C", "#B8322A", "#7E1B2A"]
HALO = [pe.withStroke(linewidth=3.2, foreground=PAPER)]
HALO_SEA = [pe.withStroke(linewidth=3.2, foreground=SEA)]
NE_LAND = jload(f"{GEO}/ne_50m_land.geojson")["features"]
NE_C50 = jload(f"{GEO}/ne_50m_admin_0_countries.geojson")["features"]


def km_colour(k, stops=(0, 25, 50, 75, 100, 140)):
    """colour for a distance in km on the RAMP"""
    from matplotlib.colors import LinearSegmentedColormap
    cm = LinearSegmentedColormap.from_list("r", RAMP)
    return cm(min(1.0, max(0.0, (k - stops[0]) / (stops[-1] - stops[0]))))


def projector(crs):
    tr = Transformer.from_crs(4326, crs, always_xy=True)
    return lambda x, y, z=None: tr.transform(x, y)


def patches(ax, g, **kw):
    polys = g.geoms if g.geom_type == "MultiPolygon" else [g] if g.geom_type == "Polygon" else []
    for p in polys:
        verts, codes = [], []
        for ring in [p.exterior] + list(p.interiors):
            cs = np.asarray(ring.coords)
            verts += cs.tolist(); codes += [Path.MOVETO] + [Path.LINETO] * (len(cs) - 2) + [Path.CLOSEPOLY]
        ax.add_patch(PathPatch(Path(verts, codes), **kw))


def lines(ax, g, **kw):
    if g.is_empty: return
    gs = g.geoms if hasattr(g, "geoms") else [g]
    for x in gs:
        if x.geom_type == "Polygon":
            for ring in [x.exterior] + list(x.interiors):
                cs = np.asarray(ring.coords); ax.plot(cs[:, 0], cs[:, 1], **kw)
        elif x.geom_type in ("LineString", "LinearRing"):
            cs = np.asarray(x.coords); ax.plot(cs[:, 0], cs[:, 1], **kw)
        elif hasattr(x, "geoms"):
            lines(ax, x, **kw)


def plain_base(ax, crs, extent_ll, borders=True, pad=(25, 12)):
    """light sea, pale land, thin grey borders. Returns the projection function."""
    lon0, lon1, lat0, lat1 = extent_ll
    clip = box(max(-180, lon0 - pad[0]), max(-89, lat0 - pad[1]), min(180, lon1 + pad[0]), min(89, lat1 + pad[1]))
    f = projector(crs)
    land = unary_union([shape(ft["geometry"]).intersection(clip) for ft in NE_LAND])
    land = stransform(f, land)
    if not land.is_valid: land = land.buffer(0)
    ax.set_facecolor(SEA)
    patches(ax, land, fc=LAND, ec="none", zorder=1)
    if borders:
        for ft in NE_C50:
            g = shape(ft["geometry"]).intersection(clip)
            if g.is_empty: continue
            g = stransform(f, g)
            lines(ax, g.boundary if hasattr(g, "boundary") else g, color=BORDER, lw=0.5, zorder=2)
    lines(ax, land, color=COAST, lw=0.5, zorder=2)
    xs, ys = f(np.array([lon0, lon1, lon0, lon1, (lon0 + lon1) / 2, (lon0 + lon1) / 2]), np.array([lat0, lat0, lat1, lat1, lat0, lat1]))
    ax.set_xlim(min(xs), max(xs)); ax.set_ylim(min(ys), max(ys)); ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
    return f


def title(fig, t, sub=None, y=0.965, x=0.04, size=26):
    fig.text(x, y, t, fontproperties=fm.FontProperties(fname=f"{FONTS}/FrauncesVar.ttf", size=size, weight="bold"), color=INKC, va="top")
    if sub:
        fig.text(x, y - (size * 1.45 + 4) / 72 / fig.get_figheight(), sub, fontsize=13.5, color=MUT, va="top")


def foot(fig, text, y=0.018):
    fig.text(0.04, y, text, fontsize=9.5, color=MUT, family=MONO, va="bottom")
