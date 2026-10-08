-- Extract metadata from monthly-average daily heat-index filenames.
-- Example: HI_2020_01_monthly_average_daily_max_station_input_approx_4m.tif
ALTER TABLE heat_index_raster
    ADD COLUMN IF NOT EXISTS year integer,
    ADD COLUMN IF NOT EXISTS month integer,
    ADD COLUMN IF NOT EXISTS stat character varying;

WITH parsed_filenames AS (
    SELECT DISTINCT
        filename,
        regexp_match(
            filename,
            'HI_([0-9]{4})_([0-9]{2})_monthly_average_daily_(max|mean|min)_'
        ) AS parts
    FROM heat_index_raster
)
UPDATE heat_index_raster AS raster
SET year = (parsed.parts[1])::integer,
    month = (parsed.parts[2])::integer,
    stat = parsed.parts[3]
FROM parsed_filenames AS parsed
WHERE raster.filename = parsed.filename
  AND parsed.parts IS NOT NULL;

CREATE INDEX IF NOT EXISTS heat_index_raster_year_idx ON heat_index_raster (year);
CREATE INDEX IF NOT EXISTS heat_index_raster_month_idx ON heat_index_raster (month);
CREATE INDEX IF NOT EXISTS heat_index_raster_stat_idx ON heat_index_raster (stat);
