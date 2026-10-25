DROP TABLE IF EXISTS forest_loss CASCADE;
DROP TABLE IF EXISTS fire_alerts CASCADE;
DROP TABLE IF EXISTS validation_logs CASCADE;

CREATE TABLE forest_loss (
    id SERIAL PRIMARY KEY,
    region VARCHAR(255),
    country VARCHAR(255),
    year INT,
    area_ha NUMERIC(12, 2),
    CONSTRAINT unique_forest_loss UNIQUE (region, country, year)
);

CREATE TABLE fire_alerts (
    id SERIAL PRIMARY KEY,
    latitude NUMERIC(10, 6),
    longitude NUMERIC(10, 6),
    confidence NUMERIC(5, 2),
    alert_date DATE,
    CONSTRAINT unique_fire_alert UNIQUE (latitude, longitude, alert_date)
);

CREATE TABLE validation_logs (
    id SERIAL PRIMARY KEY,
    source_file VARCHAR(255),
    records_processed INT,
    records_failed INT,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Optimization Indexes
CREATE INDEX IF NOT EXISTS idx_fire_alerts_date ON fire_alerts(alert_date);
CREATE INDEX IF NOT EXISTS idx_fire_alerts_location ON fire_alerts(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_forest_loss_country_year ON forest_loss(country, year);