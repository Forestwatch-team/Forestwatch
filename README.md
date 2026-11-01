# Forestwatch
The final product will be a deployed web application that presents environmental information through an interactive dashboard. Users will be able to explore forest-loss statistics, compare regions, view historical trends, and identify areas requiring further investigation.


# ForestWatch Project
This is a validated and deduplicated ETL data pipeline project designed to track and monitor forest logs, fires, and spatial metrics.


######################## Updated#############

# ForestWatch Project

## 1. Overview
ForestWatch is a modular, validated, and deduplicated environmental monitoring system designed to track active fire telemetry and canopy cover loss. It aggregates data from two primary public sources: NASA FIRMS (Fire Information for Resource Management System) and Global Forest Watch (GFW). Note: This is an analytical tool and not an official governmental reporting system.

## 2. Setup
1. Clone the repository: `git clone https://github.com/mtalha-19/Forestwatch.git`
2. Install dependencies: `python -m pip install -r requirements.txt`
3. Configure your local environment by creating a `.env` file referencing `.env.example`.

## 3. How to Run
- **Run Dashboard:** `python -m streamlit run app.py`
- **Run Pipeline:** `python scripts/etl_pipeline.py`
- **Run Tests:** `python -m pytest -v`

## 4. Project Structure
- `src/`: Core logic modules (api, ingestion, validation, transformation, database, visualization)
- `sql/`: Database schema and table definitions
- `tests/`: Automated unit tests
- `data/`: Raw and processed data storage (ignored by Git)

## 5. Data Sources & Attribution
- **FIRMS:** Thermal anomalies and active fire alerts courtesy of NASA EOSDIS.
- **GFW:** Annual tree cover and canopy disturbance metrics.

## 6. Limitations
- Hot-pixel thermal anomaly detections are not confirmed physical fires.
- Tree cover loss accounts for all canopy disturbances including natural logging and disease, not strictly permanent deforestation.

## 7. Status Table
| Component | Status |
| :--- | :--- |
| Setup & Environment | Completed |
| Database Schema & Pipeline | Completed |
| Dashboard UI & Visualization | Completed |
| Testing Suite | Completed |
| Deployment & Final Pack | In Progress |