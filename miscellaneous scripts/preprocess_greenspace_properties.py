import json
from pathlib import Path
from shapely.ops import transform
from pyproj import Transformer
from shapely.geometry import shape, mapping

# this script removes properties from the features to reduce the upload file size
path = Path('input/preprocess_greenspace_properties_inputs.json')
if not path.exists():
    raise FileNotFoundError(
        'preprocess_greenspace_properties_inputs.json does not exist')

with path.open("r", encoding="utf-8") as f:
    inputs = json.load(f)

property_mapping = inputs['property_mapping']
boolean_properties = inputs['boolean_properties']

with open(inputs['input_file'], "r", encoding="utf-8") as f:
    geojson = json.load(f)

transformer = None
if 'crs' in geojson:
    crs = geojson['crs']['properties']['name']
    transformer = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
    del geojson['crs']

for feature in geojson.get("features", []):
    # --- Whitelist properties ---
    old_props = feature.get("properties", {})

    new_props = {}
    for k, v in old_props.items():
        if k in property_mapping:
            if k in boolean_properties:
                if isinstance(v, bool):
                    new_props[property_mapping[k]] = v
                elif v in ("0", "1"):
                    new_props[property_mapping[k]] = bool(int(v))
                elif v in (0, 1):
                    new_props[property_mapping[k]] = bool(v)
                else:
                    raise Exception(f"Not able to convert {v} to boolean")
            else:
                new_props[property_mapping[k]] = v

    feature["properties"] = new_props

    # convert coordinates
    if transformer is not None:
        geom = shape(feature["geometry"])
        new_geom = transform(transformer.transform, geom)
        feature["geometry"] = mapping(new_geom)

with open(inputs['output_file'], "w", encoding="utf-8") as f:
    json.dump(geojson, f, indent=4)

print(f"Processed {inputs['input_file']}")
