ALTER TABLE sgpostcode ADD COLUMN iri TEXT;

UPDATE sgpostcode
SET iri = 'https://www.theworldavatar.com/kg/location/' || ogc_fid;
