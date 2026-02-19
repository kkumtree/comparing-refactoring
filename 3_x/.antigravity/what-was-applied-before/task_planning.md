# Airflow 3.x Migration Task Plan

This document outlines the steps to migrate the implementation from Airflow 2.x to 3.x, prioritizing the setup, deprecation handling, and modernization of DAGs.

## 1. Airflow 3.x Migration Requirements (Priority: High)
*Goal: Establish a functional 3.x environment matching the 2.x capabilities.*

- [ ] **Dependency Migration**:
    - [ ] Update `migration-3_x/requirements.txt`.
    - [ ] Add `astro-sdk-python` (Critical for `aql` functions).
    - [ ] Add `apache-airflow-providers-docker`.
    - [ ] Add `apache-airflow-providers-amazon` (for MinIO).
    - [ ] Add `apache-airflow-providers-postgres`.
- [ ] **Code Migration**:
    - [ ] Copy `dags/`, `include/`, `plugins/`, and `tests/` from root to `migration-3_x/`.
    - [ ] Update `migration-3_x/.env` (if applicable) or ensure environment variables are carried over.
- [ ] **Infrastructure**:
    - [ ] Verify `migration-3_x/docker-compose.override.yml` matches the services in root (Spark, Metabase, MinIO). *Currently it might be missing based on `astro dev init` default.*
    - [ ] Migrate the contents of `docker-compose.override.yml` to the 3.x folder.

## 2. Provider Deprecation & Connection Updates (Priority: Medium)
*Goal: Address specific deprecations, particularly Postgres/SQL connections.*

- [ ] **Provider & Operator Deprecations**:
    - [ ] **Identify & Replace `PostgresOperator`**:
        - [ ] The `PostgresOperator` is deprecated.
        - [ ] **Action**: Replace with `airflow.providers.common.sql.operators.sql.SQLExecuteQueryOperator`.
        - [ ] Ensure `apache-airflow-providers-common-sql` is installed and connection types are compatible.
    - [ ] **Postgres Connection Modernization**:
        - [ ] The `postgres` connection type is handled by `apache-airflow-providers-postgres`.
        - [ ] **Refactoring**: Move towards "SQL Connection" (Generic) if aligning with `common.sql` standards.
        - [ ] **Check**: Verify if `aql.load_file` (Astro SDK) supports the generic `sql` connection type. If not, maintain `postgres` type but note the operator change for raw SQL tasks.
- [ ] **Connection List**:
    - [ ] Review `connections_list_notes.yaml`.
    - [ ] `minio`: Ensure `Amazon Web Services` connection type is supported (requires `providers-amazon`).
    - [ ] `stock_api`: `HTTP` connection type (requires `providers-http`).

## 3. Modernized DAG Writing (Priority: Medium)
*Goal: Refactor `stock_market` DAG to Airflow 3.x / TaskFlow best practices.*

- [ ] **Remove `PythonOperator`**:
    - [ ] Convert `get_stock_prices`, `store_prices`, `get_formatted_csv` to `@task` decorated functions.
    - [ ] Refactor `include/stock_market/tasks.py` to be importable or inline them if small.
- [ ] **Modernize Docker Task**:
    - [ ] Check if `DockerOperator` can be replaced with `@task.docker` (TaskFlow Docker) for cleaner syntax (requires `apache-airflow-providers-docker>=4.0.0`).
- [ ] **Sensor Optimization**:
    - [ ] `is_api_available` executes a synchronous wait. Use **Deferrable Operators** (Triggers) if valid in 3.x to save worker slots.
    - [ ] Suggest replacing custom python sensor with `HttpSensor` (async) or keep custom logic but make it deferrable.

## 4. Component Upgrades (Priority: Low)
*Goal: Upgrade external services.*

- [ ] **Spark**:
    - [ ] Current: `airflow/spark-master` (Version unpinned/tag dependent).
    - [ ] Action: Check for latest stable Spark images compatible with Airflow 3.x environment.
- [ ] **Metabase**:
    - [ ] Current: `v0.52.8.4`.
    - [ ] Action: Check for newer releases (e.g. v0.53+).
- [ ] **MinIO**:
    - [ ] Current: `RELEASE.2024-06-13...`.
    - [ ] Update to latest stable release.

---
**Next Immediate Action**: Execute "Dependency Migration" and "Code Migration" to get `migration-3_x` running.
