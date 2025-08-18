ALTER TABLE sgpostcode
ADD COLUMN iri TEXT,
ADD COLUMN name TEXT;

UPDATE sgpostcode
SET iri  = 'https://www.theworldavatar.com/kg/location/' || ogc_fid,
    name = 'Postal code: ' || postal_code;