ALTER TABLE sport_accessibility
ADD COLUMN IF NOT EXISTS ogc_id_from_sgpostcode integer;

UPDATE sport_accessibility a
SET ogc_id_from_sgpostcode = s.ogc_fid
FROM sgpostcode s
WHERE a.postal_code = s.postal_code;

INSERT INTO exposure_result(subject, exposure, calculation, value, unit)
SELECT CONCAT('https://www.theworldavatar.com/kg/location/', ogc_id_from_sgpostcode), 'https://theworldavatar.io/kg/c516543e-d9be-42e3-83e0-818769f8e5f2', 'https://www.theworldavatar.com/kg/calculation/walking', "GSNA03_WC_as_atv_g0_h0", ''
FROM sport_accessibility
ON CONFLICT DO NOTHING;

INSERT INTO exposure_result(subject, exposure, calculation, value, unit)
SELECT CONCAT('https://www.theworldavatar.com/kg/location/', ogc_id_from_sgpostcode), 'https://theworldavatar.io/kg/c516543e-d9be-42e3-83e0-818769f8e5f2', 'https://www.theworldavatar.com/kg/calculation/cycling', "GSNA04_CC_as_atv_g0_h0", ''
FROM sport_accessibility
ON CONFLICT DO NOTHING;