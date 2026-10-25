-- Drop tables if they exist to allow clean resets
DROP TABLE IF EXISTS validation_logs CASCADE;
DROP TABLE IF EXISTS fire_alerts CASCADE;
DROP TABLE IF EXISTS forest_loss CASCADE;

-- Table 1: Forest Loss Data
CREATE TABLE forest_loss (
    id SERIAL PRIMARY KEY,
    region VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    year INT NOT NULL CHECK (year >= 2000 AND year <= 2100),
    area_ha NUMERIC(12, 2) NOT NULL CHECK (area_ha >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 2: Real-time Fire Alerts
CREATE TABLE fire_alerts (
    id SERIAL PRIMARY KEY,
    latitude NUMERIC(9, 6) NOT NULL,
    longitude NUMERIC(9, 6) NOT NULL,
    confidence NUMERIC(5, 2) CHECK (confidence BETWEEN 0 AND 100),
    alert_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 3: ETL Data Validation Logs
CREATE TABLE validation_logs (
    id SERIAL PRIMARY KEY,
    source_file VARCHAR(255) NOT NULL,
    records_processed INT NOT NULL,
    records_failed INT NOT NULL,
    status VARCHAR(50) NOT NULL,
    log_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);