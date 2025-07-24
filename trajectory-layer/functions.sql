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