import rasterio
from rasterio.transform import xy
import numpy as np
import matplotlib.pyplot as plt
import geojsoncontour
import sys


def main():
    """
    This script reads in a TIF file and  converts it into polygons
    """
    x_list = []
    y_list = []
    value_list = []
    num_x_cell = 100
    num_y_cell = 100

    i = 0
    with rasterio.open(sys.argv[1]) as src:
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
    plt.savefig("ndvi_colorbar.png", bbox_inches='tight',
                transparent=True, dpi=300)
    geojsonstring = geojsoncontour.contourf_to_geojson(
        contourf=contourf, fill_opacity=0.5)

    with open('ndvi.geojson', 'w') as f:
        f.write(geojsonstring)


if __name__ == "__main__":
    main()
