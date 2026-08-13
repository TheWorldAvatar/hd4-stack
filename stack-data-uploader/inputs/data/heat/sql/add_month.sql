ALTER TABLE utci_raster ADD COLUMN IF NOT EXISTS month int;
ALTER TABLE utci_raster ADD COLUMN IF NOT EXISTS stat character varying;

UPDATE utci_raster
SET month = ((regexp_match(filename, 'UTCI_4m_M(\d+)_(Max|Mean|Min)'))[1])::int;

UPDATE utci_raster
SET stat = LOWER((regexp_match(filename, 'UTCI_4m_M(\d+)_(Max|Mean|Min)'))[2]);

CREATE INDEX ON utci_raster(month);
CREATE INDEX ON utci_raster(stat);