-- ----------------------------------------------------------------------------
-- Reusable utilities for Postgresql databases.
-- ----------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS unaccent;


-- See: https://stackoverflow.com/a/45741630
CREATE OR REPLACE FUNCTION escape_regexp_pattern(pattern text)
RETURNS text AS $$
    SELECT regexp_replace(pattern, '([!$()*+.:<=>?[\\\]^{|}-])', '\\\1', 'g')
$$ LANGUAGE sql IMMUTABLE STRICT PARALLEL SAFE;


CREATE OR REPLACE FUNCTION slugify(input text, separator char default '-', keep char default '_', if_null text default 'none')
RETURNS text AS $$
    WITH step1 AS (
        -- Normalize the string: replace diacritics by standard characters, lower the string, etc
        -- Replace non-breaking space by normal space
        SELECT lower(unaccent(replace(input, E'\u00a0', ' '))) AS value
    )
    ,step2 AS (
        -- Remove special characters
        SELECT regexp_replace(value, '[^a-zA-Z0-9\s' || escape_regexp_pattern(separator) || COALESCE(escape_regexp_pattern(keep), '') || ']', '', 'g') AS value FROM step1
    )
    ,step3 AS (
        -- Replace spaces and successive separators by a single separator
        SELECT regexp_replace(value, '[\s' || escape_regexp_pattern(separator) || ']+', separator, 'g') AS value FROM step2
    )
    ,step4 AS (
        -- Strips separator and kept character
        SELECT trim(BOTH escape_regexp_pattern(separator) || COALESCE(escape_regexp_pattern(keep), '') FROM value) AS value FROM step3
    )
    SELECT CASE WHEN input IS NULL THEN if_null ELSE value END FROM step4;
$$ LANGUAGE sql IMMUTABLE;


CREATE OR REPLACE FUNCTION slugen(input text, separator char default '-', keep char default null)
RETURNS text AS $$
    SELECT slugify(replace(input, '_', '-'), separator, keep, null);
$$ LANGUAGE sql IMMUTABLE;


-- Reusable trigger function
CREATE OR REPLACE FUNCTION tgf_slug_from_name()
RETURNS trigger AS $$
BEGIN
    NEW.slug = slugen(NEW.name);
    RETURN NEW;
END
$$ LANGUAGE plpgsql;
