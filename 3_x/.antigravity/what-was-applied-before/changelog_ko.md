# 마이그레이션 변경 이력 (Migration Changelog)

## [미배포 (Unreleased)]

### 추가됨 (Added)
- 마이그레이션 단계를 추적하기 위해 `changelog.md` 및 `changelog_ko.md` 생성.
- `migration-3_x/requirements.txt` 업데이트:
    - `aql` 지원을 위해 `astro-sdk-python` 추가.
    - `apache-airflow-providers-docker` 추가.
    - `apache-airflow-providers-amazon` (MinIO 용) 추가.
    - `apache-airflow-providers-postgres` 추가.
    - `apache-airflow-providers-common-sql` (`SQLExecuteQueryOperator` 용) 추가.
- `dags`, `include`, `plugins`, `tests` 디렉토리를 루트에서 `migration-3_x/`로 복사.
- `spark` 디렉토리를 루트에서 `migration-3_x/`로 복사.
- `migration-3_x/docker-compose.override.yml` 생성:
    - 2.x 환경의 모든 서비스 (`minio`, `spark`, `metabase`, `docker-proxy`)를 이관.
    - 이관된 서비스에 영문/한글 이중 주석 추가.
- `migration-3_x/airflow_settings.yaml`에 커넥션 설정:
    - 노트 내용을 바탕으로 `minio`, `postgres`, `stock_api` 커넥션 정의.
    - Astro SDK 호환성을 위해 `postgres` 커넥션 타입을 유지함을 확인 (일반 SQL 대신).
- `dags/stock_market.py` 현대화:
    - `get_stock_prices`, `store_prices`, `get_formatted_csv`의 `PythonOperator`를 `@task` 데코레이터로 교체.
    - `is_api_available`을 `@task.sensor`로 업데이트.
    - TaskFlow 의존성 정의, `DockerOperator`에 대해서는 명시적 bitshift 혼용.
    - 사용하지 않는 `PythonOperator` 임포트 제거.
- `migration-3_x/docker-compose.override.yml`의 외부 컴포넌트 업그레이드:
    - MinIO: `RELEASE.2024-06-13` -> `RELEASE.2025-10-15T17-29-55Z`.
    - Metabase: `v0.52.8.4` -> `v0.58.4`.
    - Spark: `airflow/spark-master` (`bde2020/spark-base:3.3.0-hadoop3.3` 기반) 확인했으나, 해당 베이스 이미지의 최신 안정형 태그가 없음.
- Airflow 3.x 호환성을 위해 `migration-3_x/docker-compose.override.yml` 수정:
    - `webserver` 서비스를 `api-server`로 이름 변경.
    - 더 이상 사용되지 않는 `version: "3.1"` 필드 제거.
    - `AirflowConfigException` 해결 및 Airflow 3에서 Astro SDK 1.3+ 지원을 위해 `AIRFLOW__CORE__ALLOWED_DESERIALIZATION_CLASSES: 'airflow\.* astro\.*'` 환경변수 추가 (Pickling 대신 네이티브 직렬화 사용).
    - 레거시 라이브러리가 여전히 해당 설정을 체크하므로 `AIRFLOW__CORE__ENABLE_XCOM_PICKLING: 'false'` 환경변수 복구.
- `migration-3_x/requirements.txt` 업데이트:
    - Airflow 3와의 호환성을 보장하고 레거시 `enable_xcom_pickling` 체크를 피하기 위해 `astro-sdk-python` 버전을 `>=1.6.0`으로 상향.
- `migration-3_x/Dockerfile` 업데이트:
    - `astro-sdk-python` (v1.8.1) 코드를 수동으로 패치하는 `sed` 명령어 추가.
    - `ModuleNotFoundError: No module named 'airflow.hooks.dbapi'` 해결을 위해 `astro/databases/base.py`의 임포트 경로를 `airflow.providers.common.sql.hooks.sql`로 변경하는 패치 추가.
    - `ValueError: No mandatory attributes allowed` 해결을 위해 `astro/files/base.py`의 `File.path` 필드에 기본값 `""`을 할당하는 패치 추가 (부모 클래스 `Dataset`과의 attrs 상속 충돌 해결).
    - 빌드 시 권한 오류 해결을 위해 `USER root` / `USER astro` 전환 구문 추가.
- `migration-3_x/requirements.txt` 업데이트:
    - `include/stock_market/tasks.py`에서 명시적으로 `import minio`를 사용함에 따라 `minio` 패키지 추가.
- `dags/stock_market.py` 업데이트:
    - `File` 생성자에 `name="stock_market_raw_file"` 추가. Airflow 3에서 `File`이 `Asset`을 상속받으면서 (SDK의 attrs 처리 방식으로 인해) `name` 필드가 필수 인자가 됨.
