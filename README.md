# AI in One Health: Flourishing Research, Nascent Evaluation

Code and publication-level data for Figures 2A–C and 3. All input files are included and paths are relative to this directory.

## Run

Requires Python 3.9 or later. Uses only the Python standard library.

```bash
python3 make_figures.py
```

Run a single panel or validate the data separately:

```bash
python3 scripts/figure2a.py
python3 scripts/figure2b.py
python3 scripts/figure2c.py
python3 scripts/figure3.py
python3 scripts/validate.py
```

Outputs are written to `figures/` as transparent SVGs with editable text, and to `tables/` as the numerical data behind each panel. Open an SVG in a browser or vector editor. Arial is used when available, with Helvetica and the system sans-serif as fallbacks.

## Files

| File or directory | Purpose |
| --- | --- |
| `data/studies.csv` | Clean publication-level table, one row per included publication |
| `data/country_groups.csv` | Country names and development-group mapping used in the existing analysis |
| `data/country_universe.csv` | Fixed country denominators, including countries with zero publications |
| `data/world.geojson` | Natural Earth country polygons |
| `data/map_layout.csv`, `data/map_routes.json` | Frozen cartographic positions and orthogonal connectors, not statistical results |
| `data/provenance.json` | Source checksum, snapshot date, source URLs and review-status information |
| `scripts/common.py` | Shared definitions, CSV reading, calculation helpers and SVG drawing primitives |
| `scripts/figure2a.py` through `scripts/figure3.py` | Four panel-generation scripts |
| `scripts/validate.py` | Snapshot-integrity and manuscript-count checks |
| `make_figures.py` | Validate the inputs and regenerate all panels |
| `DATA_DICTIONARY.md` | Column definitions and missing-value conventions |
