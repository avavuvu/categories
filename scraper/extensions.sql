CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;

CREATE OR REPLACE FUNCTION normalize_text(input TEXT) RETURNS TEXT AS $$
  SELECT trim(regexp_replace(lower(unaccent(input)), '[^a-z0-9]+', ' ', 'g'));
$$ LANGUAGE SQL IMMUTABLE;
