"""Figure 2B: country growth and relative growth shares across six tracks."""
import json
from collections import Counter
from common import DATA, TRACKS, TRACK_COLORS, TRACK_LABELS, SVG, annual_growth, read_csv, studies, tags, write_table

COLORS = ("#F5F7C6", "#E9DF97", "#E0BC68", "#D99A39", "#D07429", "#B15337")
BOUNDS = (10, 20, 40, 60, 80)
ALIASES = {"United States of America": "United States", "Republic of Korea": "South Korea",
           "Republic of Serbia": "Serbia", "Türkiye": "Turkey",
           "United Republic of Tanzania": "Tanzania", "Congo": "Republic of the Congo"}
CODES = dict(zip(
    ("Italy", "India", "China", "Iran", "United States", "Australia", "South Korea", "United Kingdom", "Canada", "Germany", "Saudi Arabia", "Brazil"),
    ("IT", "IN", "CN", "IR", "US", "AU", "KR", "GB", "CA", "DE", "SA", "BR")))


def aggregate():
    counts, tracks = Counter(), Counter()
    for r in studies():
        year = int(r["year"])
        if not 2016 <= year <= 2025:
            continue
        for country in tags(r["countries"]):
            counts[country, year] += 1
            for track in tags(r["one_health_tracks"]):
                tracks[country, track, year] += 1
    result = []
    for country in sorted({country for country, _ in counts}):
        annual = [counts[country, y] for y in range(2016, 2026)]
        result.append(dict(country=country, total=sum(annual), mean_annual_publications=sum(annual) / 10,
                           mean_annual_growth_percent=annual_growth(annual), publications_2025=annual[-1]))
    eligible = [r for r in result if r["mean_annual_publications"] > 2 and r["country"] != "Taiwan"]
    top = sorted(eligible, key=lambda r: (-r["mean_annual_growth_percent"], -r["publications_2025"], r["country"]))[:12]
    return result, top, tracks


def main():
    country_rows, top, track_counts = aggregate()
    write_table("figure2b_country_growth.csv", country_rows)
    write_table("figure2b_top12.csv", [dict(rank=i, **r) for i, r in enumerate(top, 1)])
    layout = {r["country"]: r for r in read_csv("map_layout.csv")}
    if set(layout) != {r["country"] for r in top}:
        raise ValueError("Top-12 membership changed. Update the cartographic layout before plotting.")
    geo = json.loads((DATA / "world.geojson").read_text())
    routes = json.loads((DATA / "map_routes.json").read_text())
    lookup = {r["country"]: r["mean_annual_growth_percent"] for r in country_rows}
    svg = SVG(7.45 * 72, 5 * 72, "Figure 2B. Country publication growth, 2016–2025")
    scale = 7.45 * 72 * 0.98 / 396

    def point(lon, lat):
        return (lon + 198) * scale + 0.01 * svg.width, (90 - lat) * scale + 7.2

    def color(value):
        return COLORS[sum(value >= boundary for boundary in BOUNDS)]

    for feature in geo["features"]:
        name = feature["properties"]["ADMIN"]
        if name == "Antarctica":
            continue
        country = ALIASES.get(name, name)
        fill = color(lookup[country]) if country in lookup else "#D3D3D3"
        geometry = feature["geometry"]
        polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
        for polygon in polygons:
            vertices = [point(lon, lat) for lon, lat in polygon[0]]
            svg.path("M " + " L ".join(f"{x:.3f} {y:.3f}" for x, y in vertices) + " Z", fill, "white", 0.3)
    # Stored routes are presentation coordinates only. Counts are recomputed above.
    for country, vertices in routes.items():
        svg.polyline([point(*xy) for xy in vertices], "#777777", 0.6)
    direction_rows = []
    for rank, row in enumerate(top, 1):
        country = row["country"]
        rates = [annual_growth([track_counts[country, t, y] for y in range(2016, 2026)]) for t in TRACKS]
        if min(rates) < 0 or sum(rates) <= 0:
            raise ValueError(f"Cannot normalize negative or all-zero growth rates: {country}")
        shares = [rate / sum(rates) for rate in rates]
        diameter = 60 - (rank - 1) * 27 / (len(top) - 1) if len(top) > 1 else 60
        position = layout[country]
        x, y = point(float(position["donut_lon"]), float(position["donut_lat"]))
        # A white disk masks the connector through the otherwise transparent hole.
        svg.circle(x, y, diameter / 2, "white")
        svg.donut(x, y, diameter / 2, shares, TRACK_COLORS)
        svg.text(x, y + 4, CODES[country], anchor="middle")
        for track, rate, share in zip(TRACKS, rates, shares):
            direction_rows.append(dict(rank=rank, country=country, track=track,
                                       mean_annual_growth_percent=rate, relative_share_percent=share * 100))
    write_table("figure2b_track_growth.csv", direction_rows)
    x, y = point(-190, 0)
    svg.text(x, y + 4, "One Health directions")
    for i, (label, fill) in enumerate(zip(TRACK_LABELS, TRACK_COLORS)):
        xx, yy = point(-190, -12 - i * 10)
        svg.rect(xx, yy - 2, 6, 4, fill)
        svg.text(xx + 10, yy + 4, label)
    x, y = point(-190, -76)
    svg.text(x, y + 4, "Mean annual growth (%)")
    for i, (fill, label) in enumerate(zip(("#D3D3D3", *COLORS), ("No records", "0–<10", "10–<20", "20–<40", "40–<60", "60–<80", "80–100"))):
        xx, yy = point(-190 + (i % 2) * 75, -88 - (i // 2) * 10)
        svg.rect(xx, yy - 2, 6, 4, fill)
        svg.text(xx + 10, yy + 4, label)
    return svg.save("Figure_2B.svg")


if __name__ == "__main__":
    print(main())
