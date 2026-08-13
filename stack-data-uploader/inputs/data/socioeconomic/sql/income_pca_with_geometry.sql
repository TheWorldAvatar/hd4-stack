CREATE TABLE IF NOT EXISTS income_pca_with_geometry AS (
SELECT income_pca.area AS planning_area, pc1, pc2, wkb_geometry
FROM income_pca
JOIN planning_area ON LOWER(income_pca.area)=LOWER(planning_area."PLN_AREA_N")
);

CREATE INDEX IF NOT EXISTS income_pca_with_geometry_idx ON income_pca_with_geometry USING GIST (wkb_geometry);