CREATE TABLE IF NOT EXISTS income_with_geometry_original AS (
SELECT income."Number" AS planning_area, income."Below_1_000", income."1_000_1_999", income."2_000_2_999", income."3_000_3_999", income."4_000_4_999", income."5_000_5_999", income."6_000_6_999",
income."7_000_7_999", income."8_000_8_999", income."9_000_9_999", income."10_000_10_999", income."11_000_11_999", income."12_000_12_999", income."13_000_13_999", income."14_000_14_999", 
income."15_000_17_499", income."17_500_19_999", income."20_000andOver", wkb_geometry
FROM income
JOIN planning_area ON LOWER(income."Number")=LOWER(planning_area."PLN_AREA_N")
);

CREATE INDEX IF NOT EXISTS income_with_geometry_original_idx ON income_with_geometry_original USING GIST (wkb_geometry);