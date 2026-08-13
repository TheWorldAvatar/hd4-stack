ALTER TABLE greenness_accessibility
ADD COLUMN IF NOT EXISTS ogc_id_from_sgpostcode integer UNIQUE;

UPDATE greenness_accessibility a 
SET ogc_id_from_sgpostcode = s.ogc_fid 
FROM sgpostcode s 
WHERE a.postal_code = s.postal_code;

INSERT INTO exposure_result(subject, exposure, calculation, value, unit)
SELECT CONCAT('https://www.theworldavatar.com/kg/location/', ogc_id_from_sgpostcode), 'https://theworldavatar.io/kg/32272d28-648f-4d34-94ee-cf3c8d9ca787', 'https://www.theworldavatar.com/kg/calculation/walking', "GGNA01_WC_ap_atv_g0_h0", ''
FROM greenness_accessibility
ON CONFLICT DO NOTHING;

INSERT INTO exposure_result(subject, exposure, calculation, value, unit)
SELECT CONCAT('https://www.theworldavatar.com/kg/location/', ogc_id_from_sgpostcode), 'https://theworldavatar.io/kg/32272d28-648f-4d34-94ee-cf3c8d9ca787', 'https://www.theworldavatar.com/kg/calculation/cycling', "GGNA02_CC_ap_atv_g0_h0", ''
FROM greenness_accessibility
ON CONFLICT DO NOTHING;