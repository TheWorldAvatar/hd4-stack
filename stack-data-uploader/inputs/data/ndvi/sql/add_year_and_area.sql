ALTER TABLE ndvi_raster ADD COLUMN IF NOT EXISTS year int;
ALTER TABLE ndvi_raster ADD COLUMN IF NOT EXISTS area double precision;

WITH r AS (
    SELECT rid, ST_Transform(rast, 3857) AS rast_3857
    FROM ndvi_raster
)
UPDATE ndvi_raster
SET year = SUBSTRING(filename FROM '([0-9]{4})')::int,
area = ROUND(ABS(ST_PixelWidth(r.rast_3857) * ST_PixelHeight(r.rast_3857)))
FROM r 
WHERE r.rid = ndvi_raster.rid;

CREATE INDEX ON ndvi_raster(year);