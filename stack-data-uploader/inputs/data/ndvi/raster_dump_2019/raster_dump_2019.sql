DROP TABLE IF EXISTS raster_dump_2019;
CREATE table raster_dump_2019 AS (
with dump as (
select ST_PixelAsPolygons(rast) as temp
FROM raster_2019)
select (temp).geom AS wkb_geometry, (temp).val, ROUND(ST_Area(ST_Transform((temp).geom, 3857))) AS area FROM dump
);

DROP INDEX IF EXISTS raster_dump_2019_geom_idx;
CREATE INDEX raster_dump_2019_geom_idx ON raster_dump USING GIST (wkb_geometry);