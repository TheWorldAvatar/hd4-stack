import rasterio
from rasterio.transform import xy
import numpy as np
import matplotlib.pyplot as plt
import geojsoncontour
import json
from pathlib import Path
import re

# important assumption, year is extracted from the filename, e.g. ndvi_2023.tif


def main(raster_file):
    """
    This script reads in a TIF file and  converts it into polygons
    """
    match = re.search(r"(19|20)\d{2}", str(raster_file))
    year = int(match.group()) if match else None

    x_list = []
    y_list = []
    value_list = []
    num_x_cell = 100
    num_y_cell = 100

    i = 0
    with rasterio.open(raster_file) as src:
        band = src.read(1)
        transform = src.transform
        nodata = src.nodata

        rows, cols = band.shape
        for row in range(rows):
            for col in range(cols):
                value = band[row, col]
                if nodata is not None and value == nodata:
                    continue
                lon, lat = xy(transform, row, col)
                x_list.append(lon)
                y_list.append(lat)
                value_list.append(value)

    x_cell = np.linspace(min(x_list), max(x_list), num_x_cell)
    y_cell = np.linspace(min(y_list), max(y_list), num_y_cell)

    x_index = np.digitize(x_list, x_cell) - 1
    y_index = np.digitize(y_list, y_cell) - 1

    x_matrix = np.empty((len(x_cell), len(y_cell)))
    y_matrix = np.empty((len(x_cell), len(y_cell)))

    for i in range(len(x_cell)):
        for j in range(len(y_cell)):
            x_matrix[i, j] = x_cell[i]
            y_matrix[i, j] = y_cell[j]

    result_total_matrix = np.zeros((len(x_cell), len(y_cell)))
    result_len_matrix = np.zeros((len(x_cell), len(y_cell)))

    for i in range(len(x_list)):
        result_total_matrix[x_index[i], y_index[i]] += value_list[i]
        result_len_matrix[x_index[i], y_index[i]] += 1

    result_len_matrix[result_len_matrix == 0] = 1  # replace zeros with ones
    result_matrix = result_total_matrix / result_len_matrix  # average

    contour_level = 30
    _, ax = plt.subplots()

    contourf = ax.contourf(x_matrix, y_matrix, result_matrix,
                           levels=contour_level, cmap=plt.cm.jet)
    plt.colorbar(contourf)
    ax.remove()

    geojsonstring = geojsoncontour.contourf_to_geojson(
        contourf=contourf, fill_opacity=0.5)

    # add property to each feature if year is present
    if year:
        colorbar_filename = f"colorbar_{year}.png"
        parsed_geojson = json.loads(geojsonstring)

        for feature in parsed_geojson.get("features", []):
            feature["properties"]["year"] = year

        with open(f"processed/{raster_file.stem}.geojson", 'w') as f:
            json.dump(parsed_geojson, f)
    else:
        colorbar_filename = f"{raster_file.stem}_colorbar.png"

        with open(f"processed/{raster_file.stem}.geojson", 'w') as f:
            f.write(geojsonstring)

    plt.savefig(f"processed/{colorbar_filename}", bbox_inches='tight',
                transparent=True, dpi=300)


if __name__ == "__main__":
    folder = '../stack-data-uploader/inputs/data/ndvi/raster'
    files = list(Path(folder).glob("*.tif"))
    for file in files:
        main(file)
