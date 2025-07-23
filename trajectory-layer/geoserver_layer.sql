CREATE OR REPLACE FUNCTION get_column_name(iri VARCHAR)
RETURNS VARCHAR AS
$$
DECLARE
    column_name_result VARCHAR;
BEGIN
    SELECT column_name
    INTO column_name_result
    FROM time_series_quantities
    WHERE data_iri = iri;


    RETURN column_name_result;
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_table_name(iri VARCHAR)
RETURNS VARCHAR AS
$$
DECLARE
    table_name_result VARCHAR;
BEGIN
    SELECT table_name
    INTO table_name_result
    FROM time_series_quantities
    WHERE data_iri = iri;


    RETURN table_name_result;
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_time_series(iri VARCHAR)
RETURNS VARCHAR AS
$$
DECLARE
    time_series_result VARCHAR;
BEGIN
    SELECT time_series_iri
    INTO time_series_result
    FROM time_series_quantities
    WHERE data_iri = iri;


    RETURN time_series_result;
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_location_table(
    data_iri TEXT
)
RETURNS TABLE (
    "time" bigint,
    "geom" geometry
) AS $$
DECLARE
    query TEXT := '';
BEGIN
    query := format(
        'SELECT time, %I AS geom FROM %I WHERE time_series_iri=%L',
        get_column_name(data_iri),
        get_table_name(data_iri),
        get_time_series(data_iri)
    );

    RETURN QUERY EXECUTE query;
END $$ LANGUAGE plpgsql;

WITH timeseries AS (
    SELECT
        time,
        geom
    FROM
        public.get_location_table('http://botanic_trajectory')
    ORDER BY time
),
line AS (
    SELECT
        ts.time,
        LAG(ts.geom) OVER (ORDER BY time) AS prev_geom,
        ST_MakeLine(LAG(ts.geom) OVER (ORDER BY ts.time), ts.geom) AS geom
    FROM
        timeseries ts
)

SELECT
    time, geom, 'http://botanic_trajectory' AS iri
FROM
    line
WHERE
    line.prev_geom IS NOT NULL