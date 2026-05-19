CREATE TABLE IF NOT EXISTS income_with_geometry AS (
SELECT
    income."Number" AS planning_area,
    (COALESCE("Below_1_000",0) + COALESCE("1_000_1_999",0) + COALESCE("2_000_2_999",0)) AS "3000",
    (COALESCE("3_000_3_999",0) + COALESCE("4_000_4_999",0) + COALESCE("5_000_5_999",0)) AS "6000",
    (COALESCE("6_000_6_999",0) + COALESCE("7_000_7_999",0) + COALESCE("8_000_8_999",0)) AS "9000",
    (COALESCE("9_000_9_999",0) + COALESCE("10_000_10_999",0) + COALESCE("11_000_11_999",0)) AS "12000",
    (COALESCE("12_000_12_999",0) + COALESCE("13_000_13_999",0) + COALESCE("14_000_14_999",0)) AS "15000",
    (COALESCE("15_000_17_499",0) + COALESCE("17_500_19_999",0) + COALESCE("20_000andOver",0)) AS "others", 
    wkb_geometry
FROM income
JOIN planning_area ON LOWER(income."Number")=LOWER(planning_area."PLN_AREA_N")
);

CREATE INDEX IF NOT EXISTS income_with_geometry_idx ON income_with_geometry USING GIST (wkb_geometry);