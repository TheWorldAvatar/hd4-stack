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