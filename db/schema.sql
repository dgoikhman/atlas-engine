-- Atlas Engine: one schema shared by every atlas.
-- Plain lat/lng columns; add PostGIS when geo queries demand it.

CREATE TABLE IF NOT EXISTS geo (
  id SERIAL PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,          -- 'cleveland-oh', 'toledo-oh-43605'
  kind TEXT NOT NULL,                 -- 'metro' | 'zip' | 'city' | 'county' | 'parcel'
  name TEXT NOT NULL,
  state TEXT,
  parent_id INT REFERENCES geo(id),
  lat DOUBLE PRECISION, lng DOUBLE PRECISION
);

-- Every atlas writes metric observations here. One long table beats
-- per-atlas schemas: a new atlas is new metric names, zero migrations.
CREATE TABLE IF NOT EXISTS metric (
  id BIGSERIAL PRIMARY KEY,
  geo_id INT NOT NULL REFERENCES geo(id),
  atlas TEXT NOT NULL,                -- 'rentals' | 'franchises' | 'str' | ...
  name TEXT NOT NULL,                 -- 'home_value','rent','fdd_item7_low',...
  value DOUBLE PRECISION,
  text_value TEXT,
  as_of DATE NOT NULL,
  source TEXT NOT NULL,               -- 'zillow_zhvi','census_acs','mn_cards',...
  UNIQUE (geo_id, atlas, name, as_of, source)
);

-- Entities that aren't places: franchise brands, ordinances, crews.
CREATE TABLE IF NOT EXISTS entity (
  id SERIAL PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,          -- 'subway', 'nashville-str-ordinance'
  atlas TEXT NOT NULL,
  kind TEXT NOT NULL,                 -- 'franchise_brand' | 'ordinance' | 'crew'
  name TEXT NOT NULL,
  data JSONB NOT NULL DEFAULT '{}'    -- extracted structured payload
);

-- Raw source documents (FDD PDFs, ordinance pages) with change detection.
CREATE TABLE IF NOT EXISTS source_doc (
  id BIGSERIAL PRIMARY KEY,
  url TEXT NOT NULL,
  entity_id INT REFERENCES entity(id),
  sha256 TEXT NOT NULL,               -- re-extract only when the hash changes
  fetched_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  extracted_at TIMESTAMPTZ,
  extraction JSONB
);

-- The named index per atlas, with the factor breakdown pages render.
CREATE TABLE IF NOT EXISTS score (
  geo_id INT NOT NULL REFERENCES geo(id),
  atlas TEXT NOT NULL,
  score DOUBLE PRECISION NOT NULL,    -- 0-100
  factors JSONB NOT NULL,
  computed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (geo_id, atlas)
);

-- Alerts: the retention engine. A row per (email, watch expression).
CREATE TABLE IF NOT EXISTS alert_sub (
  id BIGSERIAL PRIMARY KEY,
  email TEXT NOT NULL,
  atlas TEXT NOT NULL,
  geo_slug TEXT,
  rule TEXT NOT NULL,                 -- 'new_star_opportunity' | 'score_change' | 'new_fdd'
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
