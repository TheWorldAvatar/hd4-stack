# HD4 stack

Configuration for stack hosting HD4 related data

## Credentials

The following files are required in [stack-manager\inputs\secrets](stack-manager\inputs\secrets)

- geoserver_password
- mapbox_api_key
- mapbox_username
- postgis_password

## Contour generation

A script is provided to generate a GeoJSON contour of a tif file for visualisation. The GeoJSON file can be copied into [/stack-data-uploader/inputs/data/ndvi/raw_contour/](/stack-data-uploader/inputs/data/ndvi/raw_contour/) for upload.

To use the script (be sure to replace command with file name):

```bash
cd miscellaneous\ scripts/
python generate_contour_from_tif.py [REPLACE_WITH_TIF_FILENAME]
```

## Trajectory visualisation

Prerequisite: Point time series uploaded using the TimeSeriesClient.

The GeoServer layer has to be generated manually at the moment, the necessary SQL functions and SQL view are in [trajectory-layer/](trajectory-layer/). Replace point IRI in the SQL view if necessary. The layer name should be `botanic_trajectory`, matching what is in [stack-manager\inputs\data\vis\public\config\data.json](stack-manager\inputs\data\vis\public\config\data.json).

## Setting up visualisation

1) Populate [stack-manager\inputs\data\vis\public\images](stack-manager\inputs\data\vis\public\images) and [stack-manager\inputs\data\vis\public\optional-pages](stack-manager\inputs\data\vis\public\optional-pages) with files from <https://github.com/TheWorldAvatar/viz/tree/main/code/public>.

2) Modify URLs of GeoServer layers in [stack-manager\inputs\data\vis\public\config\data.json](stack-manager\inputs\data\vis\public\config\data.json) depending on deployment settings.

## Spin up the stack

Recommended stack name - `hd4`. If a different stack name is desired, changes are required to the config files.

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

## HTTPS setup

Instructions are adapted from <https://mindsers.blog/en/post/https-using-nginx-certbot-docker/>. The committed files [https/](https/) show the final states, it is necessary to make modifications to the files at least during the initial setup.

1) [https\nginx\conf\default.conf](https\nginx\conf\default.conf) should only contain the following portion

    ```text
    server {
        listen 80;
        listen [::]:80;

        server_name hd4.theworldavatar.io;
        server_tokens off;

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location / {
            return 301 https://hd4.theworldavatar.io$request_uri;
        }
    }
    ```

    Spin up nginx, i.e.

    ```bash
    cd https
    docker compose up webserver -d
    ```

    Make sure the domain name (e.g. hd4.theworldavatar.io) is mapped to the IP address of the machine, also note that certbot must be able to contact the IP address at port 80 while creating the certificate.

2) Execute the following (dry run)

    ```bash
    docker compose run --rm  certbot certonly --webroot --webroot-path /var/www/certbot/ --dry-run -d hd4.theworldavatar.io
    ```

3) If successful, rerun certbot without --dry-run

    ```bash
    docker compose run --rm  certbot certonly --webroot --webroot-path /var/www/certbot/ -d hd4.theworldavatar.io
    ```

4) Revert changes in [https\nginx\conf\default.conf](https\nginx\conf\default.conf), make sure IP address for the stack is correct in this part:

    ```text
    map $host $upstream_host {
        hd4.theworldavatar.io http://172.17.0.1:3841;
    }
    ```

    Note that only GET requests are allowed to visualisation, exposure-feature-info-agent, and geoserver. If access is needed for other routes, please make the necessary changes.

5) Restart nginx

    ```bash
    docker compose restart webserver
    ```

6) Setup should be complete at this stage, the certificate needs to be renewed manually every three months with the following command.

    ```bash
    docker compose run --rm certbot renew
    ```
