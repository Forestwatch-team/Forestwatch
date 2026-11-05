# ForestWatch

ForestWatch is an interactive dashboard that shows satellite fire detections (NASA FIRMS) and annual tree cover loss (Global Forest Watch) for Australia. It is built for learning and awareness. It is an analytical tool, not an official reporting system.

## 1. Overview

The system loads two public data sources into a PostgreSQL database (hosted on Supabase) and shows them in a Streamlit dashboard with five tabs: Overview, Fire activity, Forest loss, Data quality, and Methodology and limits. Filters let users choose a date range and fire confidence level, and a country for forest loss.

## 2. Current data (checked 2 November 2026)

- **Fire detections:** VIIRS SNPP NRT, 13 to 17 October 2026, 11,894 rows.
- **Forest loss:** annual tree cover loss for Australia, 24 records.

## 3. Setup

1. Clone the repository: `git clone https://github.com/Forestwatch-team/Forestwatch.git`
2. Install dependencies (Python 3.12 or newer): `python -m pip install -r requirements.txt`. To run the tests also install `requirements-dev.txt`.
3. Create a file named `.env` in the project root with these five settings: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`. Ask the team for the values. Never commit this file.

## 4. How to run

- **Dashboard:** `python -m streamlit run app.py`
- **Tests:** `python -m pytest -v`
- **Data pipeline (team members only):** `python scripts/etl_pipeline.py`. It needs the data source keys in your `.env`.

**Warning:** `scripts/init_db.py` rebuilds the tables from `sql/schema.sql`. Run it only on an empty test database, never on the shared database.

## 5. Project structure

- `app.py`: the Streamlit dashboard
- `src/config.py`: reads settings from `.env`
- `src/database/`: database connection (`db.py`) and read-only queries (`queries.py`)
- `src/visualization/`: chart helpers
- `scripts/`: ETL pipeline and helper scripts
- `sql/`: database schema
- `tests/`: automated tests
- `docs/`: user manual
- `notebooks/`: exploratory analysis
- Raw data files are not stored in Git.

## 6. Data sources and attribution

- **Fire detections:** NASA FIRMS (Fire Information for Resource Management System), courtesy of NASA EOSDIS.
- **Tree cover loss:** Global Forest Watch, based on Hansen et al., University of Maryland.

Please credit both providers when you share results.

## 7. Limitations

- A fire detection is a satellite hot-pixel reading. It is not a confirmed fire and not a burned area. One fire can produce many detections.
- Tree cover loss is not the same as deforestation. It includes harvest, fire and disease.
- The database holds only 5 days of fire data (13 to 17 October 2026). A 12-month load has not been done.
- The fire table has no country column, so fire filters use date and confidence only.
- The map shows at most 20,000 detections. Times are in UTC.
- The last day of fire data may be partial.

## 8. Testing

Four automated tests pass (checked 2 November 2026). Manual checks of the dashboard, filters and database-unavailable message are recorded in the Testing Report. Some tests were not run, for example an empty database and the live data download. They are listed in the report.

## 9. Status

| Component | Status |
| :--- | :--- |
| Setup and environment | Completed |
| Database schema and data loading (team) | Completed for 13 to 17 October 2026 data |
| Dashboard (5 tabs, real Supabase data) | Completed |
| Automated tests (4) | Completed |
| Testing report | Completed |
| 12-month fire data load | Planned |
| Public deployment | Planned |
| Final submission pack | In progress |

## 10. Live demo

Not deployed yet.