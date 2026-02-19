# Changelog - Airflow 3.x Migration & Refactoring

## [2026-02-14] Migration Updates

### Dependency Updates
- **Added** `apache-airflow-providers-common-sql` to support modern SQL execution patterns.
- **Added** `flask-appbuilder` to enable UI widget support in Hooks and suppress `PostgresHook` initialization info messages.
- **Removed** `astro-sdk-python` and `sqlalchemy` to reduce dependency complexity and reliance on third-party abstractions.
- **Ensured** `astro-sdk-python` and other provider packages are compatible with Airflow 3.x. Wait, "Ensured astro-sdk-python... compatible" should be removed if I removed the package.
- **Ensured** provider packages are compatible with Airflow 3.x.
- **Environment**: Switched to `uv` for dependency management as requested.

### Code Refactoring
#### `dags/stock_market.py`
- **Imports Updated**:
    - `airflow.decorators` → `airflow.sdk` (for `@dag`, `@task`).
    - `airflow.hooks.base` → `airflow.sdk.bases.hook` (for `BaseHook`).
    - `airflow.sensors.base` → `airflow.sdk.bases.sensor` (for `PokeReturnValue`).
    - `airflow.sensors.base` → `airflow.sdk.bases.sensor` (for `PokeReturnValue`).
- **Standard Operators**:
    - Replaced `astro-sdk` (`aql.load_file`) with standard Airflow patterns:
        - `SQLExecuteQueryOperator`: Used for creating the `stock_market` table.
        - `PythonOperator` (`@task`): Implemented data loading from MinIO to Postgres using `PostgresHook` and `COPY` command.
- **Monkeypatch Removal**: Removed `astro.files.File` monkeypatch as the SDK is no longer used.

#### `include/stock_market/tasks.py`
- **Imports Updated**:
    - `airflow.hooks.base` → `airflow.sdk.bases.hook` (for `BaseHook`).

### Infrastructure Fixes
- **Docker Proxy**: Added `hostname: docker-proxy` to `docker-compose.override.yml` to resolve DNS resolution failures causing `AirflowException`.

### Deprecation Handling
- **PostgresOperator**: Checked for usage of deprecated `PostgresOperator`. No explicit usages were found in the current DAGs.
    - *Note*: For future SQL tasks, use `airflow.providers.common.sql.operators.sql.SQLExecuteQueryOperator` instead of `PostgresOperator`.
- **Docker Provider**: Updated `apache-airflow-providers-docker` to latest version to resolve internal deprecation warnings.
- **Dockerfile**: Removed legacy `sed` commands that were patching `astro-sdk` (which is now removed), fixing the Docker build error.
