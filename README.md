# hd4-stack

Configuration for stack hosting HD4 related data

## Contour generation

A script is provided to generate a GeoJSON contour of a tif file for visualisation. The GeoJSON file can be copied into [](/stack-data-uploader/inputs/data/ndvi/raw_contour/) for upload.

To use the script:

```bash
cd miscellaneous\ scripts/
python generate_contour_from_tif.py [REPLACE_WITH_TIF_FILENAME]
```

## Trajectory visualisation

Prerequisite: Point time series uploaded using the TimeSeriesClient.

The GeoServer layer has to be generated manually at the moment, the necessary SQL functions and SQL view are in [trajectory-layer/](trajectory-layer/). Replace point IRI in the SQL view if necessary. The layer name should be `botanic_trajectory`, matching what is in [stack-manager\inputs\data\vis\public\config\data.json](stack-manager\inputs\data\vis\public\config\data.json).

## Setting up visualisation

Populate [stack-manager\inputs\data\vis\public\images](stack-manager\inputs\data\vis\public\images) and [stack-manager\inputs\data\vis\public\optional-pages](stack-manager\inputs\data\vis\public\optional-pages) with files from <https://github.com/TheWorldAvatar/viz/tree/main/code/public>.

## Spin up the stack

```bash
cd stack-manager
./stack.sh start hd4
```

## Uploading data

Ensure files are copied into the respective folders, table below shows the files in the HD4 dropbox or download URLs and the location they need to be saved before running the data uploader:

| File in Dropbox or download URL    | Location to place the file(s) |
| --------| ------- |
| HD4 Programme/WP1/Data/Primary/1-Buildings/Postcode/sgpostcode.geojson | [stack-data-uploader/inputs/data/sgpostcode/postcode](stack-data-uploader/inputs/data/sgpostcode/postcode)    |
| <https://data.gov.sg/datasets/d_83bdc9dbb7d05756280e97179ce49d2d/view> | [stack-data-uploader/inputs/data/parks/parks_2016](stack-data-uploader/inputs/data/parks/parks_2016)    |
| <https://data.gov.sg/datasets/d_77d7ec97be83d44f61b85454f844382f/view> | [stack-data-uploader/inputs/data/parks/polygons](stack-data-uploader/inputs/data/parks/polygons)    |
| <https://data.gov.sg/datasets/d_9ec9fe2ff2c6c520dd8679933a4a059a/view> | [stack-data-uploader/inputs/data/parks/parks_2019](stack-data-uploader/inputs/data/parks/parks_2019)    |

If visualisation of NDVI is desired, be sure to generate the necessary file in [Contour generation](#contour-generation).

```bash
cd stack-data-uploader
./stack.sh start hd4
```
