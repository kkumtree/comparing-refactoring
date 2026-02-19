# Migration Changelog

## [Unreleased]

### Added
- Created `changelog.md` and `changelog_ko.md` to track migration steps.
- Updated `migration-3_x/requirements.txt`:
    - Added `astro-sdk-python` for `aql` support.
    - Added `apache-airflow-providers-docker`.
    - Added `apache-airflow-providers-amazon` (MinIO).
    - Added `apache-airflow-providers-postgres`.
    - Added `apache-airflow-providers-common-sql` (for `SQLExecuteQueryOperator`).
- Copied `dags`, `include`, `plugins`, and `tests` directories from root to `migration-3_x/`.
- Copied `spark` directory from root to `migration-3_x/`.
- Created `migration-3_x/docker-compose.override.yml`:
    - Ported all services (`minio`, `spark`, `metabase`, `docker-proxy`) from the 2.x environment.
    - Added bilingual comments (EN/KO) to indicate ported services.
- Configured connections in `migration-3_x/airflow_settings.yaml`:
    - Defined `minio`, `postgres`, and `stock_api` connections from notes.
    - Verified `postgres` connection type is maintained for Astro SDK compatibility (instead of generic SQL).
- Modernized `dags/stock_market.py`:
    - Replaced `PythonOperator` with `@task` decorators for `get_stock_prices`, `store_prices`, `get_formatted_csv`.
    - Updated `is_api_available` to `@task.sensor`.
    - Defined TaskFlow dependencies, mixing explicit bitshift for `DockerOperator`.
    - Removed unused `PythonOperator` import.
- Upgraded external components in `migration-3_x/docker-compose.override.yml`:
    - MinIO: `RELEASE.2024-06-13` -> `RELEASE.2025-10-15T17-29-55Z`.
    - Metabase: `v0.52.8.4` -> `v0.58.4`.
    - Spark: Checked `airflow/spark-master` (based on `bde2020/spark-base:3.3.0-hadoop3.3`); no newer stable tag found for this base image.
- Fixed `migration-3_x/docker-compose.override.yml` for Airflow 3.x compatibility:
    - Renamed `webserver` service to `api-server`.
    - Removed obsolete `version: "3.1"` field.
    - Added `AIRFLOW__CORE__ALLOWED_DESERIALIZATION_CLASSES: 'airflow\.* astro\.*'` to resolve `AirflowConfigException` and support Astro SDK 1.3+ on Airflow 3 (native serialization).
    - Restored `AIRFLOW__CORE__ENABLE_XCOM_PICKLING: 'false'` as legacy libs still explicitly check for it.
- Updated `migration-3_x/requirements.txt`:
    - Bumped `astro-sdk-python` to `>=1.6.0` to ensure compatibility with Airflow 3 and avoid legacy `enable_xcom_pickling` checks.
- Updated `migration-3_x/Dockerfile`:
    - Added `sed` patch to manually fix `astro-sdk-python` (v1.8.1) checking for removed `enable_xcom_pickling` config.
    - Added `sed` patch to fix `ModuleNotFoundError: No module named 'airflow.hooks.dbapi'` by redirecting import to `airflow.providers.common.sql.hooks.sql` in `astro/databases/base.py`.
    - Added `sed` patch to fix `ValueError: No mandatory attributes allowed` by assigning default value `""` to `File.path` in `astro/files/base.py`, resolving conflict with `Dataset` parent class defaults.
    - Wrapped patches in `USER root` / `USER astro` block to fix permission errors during build.
- Updated `migration-3_x/requirements.txt`:
    - Added `minio` package, which is explicitly imported in `include/stock_market/tasks.py` but was missing from the text.
- Updated `dags/stock_market.py`:
    - Added `name="stock_market_raw_file"` to `File` constructor. In Airflow 3, `File` inherits from `Asset` (via Dataset), making `name` a required argument due to `attrs` inheritance quirks in the SDK.
