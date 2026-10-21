"""Generate Heat index contour GeoJSON and previews, similarly to generate_ndvi_contour.

Examples:
    python generate_heat_index_contour.py
    python generate_heat_index_contour.py --year 2019 --month 1 --stat Mean
    python generate_heat_index_contour.py --month 1 2 12 --stat Min Max

With no filters, process all years, months and statistics. Each feature has an integer
year, a full
month name (January-December) and stat (min/mean/max), suitable for filtering a
combined map layer. Command-line month selection uses numbers (1-12).
Requires rasterio, numpy, matplotlib, and geojsoncontour.
"""

import argparse
import json
from pathlib import Path
import re

import geojsoncontour
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.transform import from_bounds
from rasterio.warp import reproject, transform_bounds


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = BASE_DIR.parent / "stack-data-uploader/inputs/data/heat/heat_index"
FILENAME = re.compile(
    r"HI_(\d{4})_(0[1-9]|1[0-2])_"
    r"monthly_average_daily_(min|mean|max)_"
    r".*\.tif",
    re.I,
)
MONTH_NAMES = (
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
)


def main(raster_file, output_dir=BASE_DIR / "processed/heat_index", grid_size=100, levels=30):
    """Write one contour collection in EPSG:4326 and its matching contour preview."""
    raster_file = Path(raster_file)
    match = FILENAME.fullmatch(raster_file.name)
    if not match:
        raise ValueError(f"Unexpected Heat index filename: {raster_file.name}")
    year, month, stat = int(match[1]), int(match[2]), match[3].lower()
    if grid_size < 2 or levels < 2:
        raise ValueError("grid_size and levels must be at least 2")

    # Average onto a small geographic grid without constructing a Python list
    # containing every source pixel. Empty cells remain masked, not zero.
    with rasterio.open(raster_file) as src:
        if src.crs is None:
            raise ValueError(f"Raster has no CRS: {raster_file}")
        bounds = transform_bounds(src.crs, "EPSG:4326", *src.bounds)
        transform = from_bounds(*bounds, grid_size, grid_size)
        values = np.full((grid_size, grid_size), np.nan, dtype=np.float32)
        reproject(
            source=rasterio.band(src, 1), destination=values,
            src_transform=src.transform, src_crs=src.crs, src_nodata=src.nodata,
            dst_transform=transform, dst_crs="EPSG:4326", dst_nodata=np.nan,
            resampling=Resampling.average,
        )
        values = np.ma.masked_invalid(values * src.scales[0] + src.offsets[0])
    if values.count() == 0:
        raise ValueError(f"Raster contains no valid values: {raster_file}")

    longitude = transform.c + (np.arange(grid_size) + 0.5) * transform.a
    latitude = transform.f + (np.arange(grid_size) + 0.5) * transform.e

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    figure, ax = plt.subplots()
    try:
        contour = ax.contourf(longitude, latitude, values, levels=levels, cmap="YlOrRd")
        figure.colorbar(contour, ax=ax, label="Heat index (°C)")
        collection = json.loads(geojsoncontour.contourf_to_geojson(
            contourf=contour, fill_opacity=0.5,
        ))
        for feature in collection["features"]:
            properties = feature.setdefault("properties", {})
            if "title" in properties:
                properties["name"] = properties.pop("title")
            properties.update(year=year, month=MONTH_NAMES[month - 1], stat=stat)
        geojson_path = output_dir / f"{raster_file.stem}.geojson"
        geojson_path.write_text(json.dumps(collection, allow_nan=False), encoding="utf-8")
        ax.set_title(f"{year} {MONTH_NAMES[month - 1]} — {stat.title()} Heat index")
        ax.set_xlabel("Longitude (°E)")
        ax.set_ylabel("Latitude (°N)")
        ax.set_aspect(1 / np.cos(np.deg2rad(float(np.mean(latitude)))))
        figure.savefig(output_dir / f"preview_{year}_{month}_{stat}.png",
                       bbox_inches="tight", dpi=200)
    finally:
        plt.close(figure)
    return geojson_path


def cli():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=BASE_DIR / "processed/heat_index")
    parser.add_argument("--year", type=int, nargs="+", help="Years to process; default: all")
    parser.add_argument("--month", type=int, nargs="+", choices=range(1, 13),
                        help="Months to process; default: all")
    parser.add_argument("--stat", type=str.lower, nargs="+", choices=["min", "mean", "max"],
                        help="Statistics to process (case insensitive); default: all")
    parser.add_argument("--grid-size", type=int, default=100,
                        help="Number of grid cells per axis; default: 100, as in the NDVI script")
    parser.add_argument("--levels", type=int, default=30,
                        help="Approximate number of contour levels per raster; default: 30")
    args = parser.parse_args()
    if args.grid_size < 2 or args.levels < 2:
        parser.error("--grid-size and --levels must be at least 2")
    if not args.input_dir.is_dir():
        parser.error(f"Input directory does not exist: {args.input_dir}")
    files = []
    for path in sorted(args.input_dir.iterdir()):
        match = FILENAME.fullmatch(path.name)
        if path.is_file() and match:
            if args.year and int(match[1]) not in args.year:
                continue
            if args.month and int(match[2]) not in args.month:
                continue
            if args.stat and match[3].lower() not in args.stat:
                continue
            files.append(path)
    if not files:
        parser.error("No Heat index rasters match the selected years, months and statistics")
    for path in files:
        print(f"Processing {path.name}", flush=True)
        print(f"Written {main(path, args.output_dir, args.grid_size, args.levels)}", flush=True)


if __name__ == "__main__":
    cli()

