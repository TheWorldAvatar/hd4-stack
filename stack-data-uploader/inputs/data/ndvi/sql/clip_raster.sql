DROP TABLE IF EXISTS ndvi_raster_with_properties;

CREATE TABLE ndvi_raster_with_properties (
    id bigint GENERATED ALWAYS AS IDENTITY,
    poly_id int REFERENCES greenspace_properties(ogc_fid) ON DELETE CASCADE,
    raster_id int REFERENCES ndvi_raster(rid) ON DELETE CASCADE,
    year int,
    formal_green int,
    public_access int,
    area double precision,
    rast raster
);

INSERT INTO ndvi_raster_with_properties(poly_id, raster_id, year, formal_green, public_access, area, rast)
SELECT 
    p.ogc_fid AS poly_id,
    r.rid AS raster_id,
    r.year,
    p.formal_green_final_value_imputed AS formal_green,
    p.public_access_final_value_imputed AS public_access,
    r.area,
    ST_Clip(r.rast, p.wkb_geometry) AS rast
FROM ndvi_raster r
JOIN greenspace_properties p 
ON p.year=r.year
AND ST_Intersects(r.rast, p.wkb_geometry);

CREATE INDEX ndvi_raster_clipped_year_idx ON ndvi_raster_with_properties(year);
CREATE INDEX ndvi_raster_clipped_public_idx ON ndvi_raster_with_properties(public_access);
CREATE INDEX ndvi_raster_clipped_formal_idx ON ndvi_raster_with_properties(formal_green);
CREATE INDEX ndvi_raster_clipped_gix ON ndvi_raster_with_properties USING GIST(ST_ConvexHull(rast));
