import geopandas as gpd
import json

H_BANDS: dict[str, tuple[int, int | None]] = {
    "h1": (1, 2),
    "h2": (3, 6),
    "h3": (7, 12),
    "h4": (13, 22),
    "h5": (23, None),
}


def floors_in_band(levels_corrected: float, h: str) -> float:
    """Return real floor count of this building that falls in h-band.

    Example:
    - levels_corrected = 15
    - h4 is 13-22
    => real floors in h4 = 3 (13,14,15)

    This exactly reflects the requested logic:
    for the top category, use [category lower bound, actual top floor].
    """
    lower, upper = H_BANDS[h]
    if levels_corrected <= 0:
        return 0.0
    top = levels_corrected if upper is None else min(
        levels_corrected, float(upper))
    bottom = float(lower)
    if top < bottom:
        return 0.0
    return top - bottom + 1.0


# Read GeoPackage
gdf = gpd.read_file(
    "ggva/angular_gvi_repaired_buildings_simplified_total.gpkg")

# remove rows where 2016_h1_ge is null
gdf = gdf[gdf["2016_h1_ge"].notna()]

h1_weights = []
h2_weights = []
h3_weights = []
h4_weights = []
h5_weights = []

columns = gdf.columns
for idx, row in gdf.iterrows():
    num_floors = row['levels_corrected']
    area = row['area_m2']

    h1_floors = floors_in_band(row['levels_corrected'], "h1")
    h2_floors = floors_in_band(row['levels_corrected'], "h2")
    h3_floors = floors_in_band(row['levels_corrected'], "h3")
    h4_floors = floors_in_band(row['levels_corrected'], "h4")
    h5_floors = floors_in_band(row['levels_corrected'], "h5")

    h1_weights.append(h1_floors * area)
    h2_weights.append(h2_floors * area)
    h3_weights.append(h3_floors * area)
    h4_weights.append(h4_floors * area)
    h5_weights.append(h5_floors * area)

gdf['h1_weight'] = h1_weights
gdf['h2_weight'] = h2_weights
gdf['h3_weight'] = h3_weights
gdf['h4_weight'] = h4_weights
gdf['h5_weight'] = h5_weights

# generate columns
years = range(2016, 2026)
heights = ['h1', 'h2', 'h3', 'h4', 'h5']
columns_to_keep = []

for year in years:
    for height in heights:
        columns_to_keep.append(f"{year}_{height}_ge")

with open("ggva_list.json", "w") as file:
    json.dump(columns_to_keep, file, indent=4)

columns_to_keep.extend(['h1_weight', 'h2_weight', 'h3_weight',
                       'h4_weight', 'h5_weight', 'v2_class', 'geometry', 'Name', 'candidate_source'])

gdf = gdf[columns_to_keep]

gdf.to_file("ggva/processed_ggva.gpkg", driver="GPKG")
