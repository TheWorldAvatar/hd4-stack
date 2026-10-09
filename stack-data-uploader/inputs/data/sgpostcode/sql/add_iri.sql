ALTER TABLE sgpostcode
ADD COLUMN IF NOT EXISTS iri TEXT,
ADD COLUMN IF NOT EXISTS name TEXT;

UPDATE sgpostcode
SET iri  = 'https://www.theworldavatar.com/kg/location/' || ogc_fid,
    name = 'Postal code: ' || postal_code;
