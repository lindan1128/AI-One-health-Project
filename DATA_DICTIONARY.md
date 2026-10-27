# Publication-level data dictionary

File: `data/studies.csv`. Encoding: UTF-8. Delimiter: comma. Fields containing multiple values use `|`. Every row represents one publication. The table contains 1,786 unique `study_id` values.

| Column | Definition |
| --- | --- |
| `study_id` | Stable study identifier used throughout the review |
| `title` | Article title from the extraction workbook |
| `journal` | Journal name from the extraction workbook |
| `year` | Publication year used in the analyses |
| `doi` | DOI where recorded, without a URL prefix |
| `article_type` | `original_research` or `review` |
| `countries` | Corresponding-author countries or regions as recorded, separated by `|` |
| `one_health_tracks` | One or more of the six action tracks, separated by `|` |
| `data_types` | Recorded input-data categories, separated by `|` |
| `model_categories` | Machine learning, Deep learning, Language models, separated by `|` |
| `model_names` | Extracted model names, separated by `|` |
| `language_models` | Named language models where recorded, separated by `|` |
| `ai_roles` | Analysis, Prediction, Generation, Decision support, Intervention, separated by `|` |
| `analysis_tier` | T1, T2, T3 or T4 for the Analysis role |
| `prediction_tier` | T1, T2, T3 or T4 for the Prediction role |
| `generation_tier` | T1, T2, T3 or T4 for the Generation role |
| `decision_support_tier` | T1, T2 or T3 for the Decision support role |
| `intervention_tier` | T1, T2 or T3 for the Intervention role |

Empty descriptive cells mean not recorded. Empty tier cells mean the role is not assigned. Review rows have empty model, data-type, AI-role and tier columns because these analyses apply to original research. Empty cells must not be interpreted as T1 or as evidence of absence.

The export changes column names, normalizes multi-value separators and removes literal “Not recorded” and “Not applicable” placeholders. It does not change membership, titles, recorded countries, roles or tiers. Audit flags are summarized in `provenance.json` and described in the README. The full audit remains in the source supplementary workbook.

## Supporting files

`country_groups.csv` maps the source `country` to its `classification_name` and `group`. `country_universe.csv` includes countries with zero publications and determines the denominator of country means. The classification snapshot is held fixed across all years.

`map_layout.csv` stores longitude/latitude coordinates for country anchors and ocean donut positions. `map_routes.json` stores connector vertices. They control presentation only. Country rankings, growth values, donut sizes and sector shares are recomputed from `studies.csv`.

`world.geojson` is a cartographic background. Its boundaries and geographic units are inherited from Natural Earth and are not an analytical statement about political status.
