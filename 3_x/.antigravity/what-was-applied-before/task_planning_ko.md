# Airflow 3.x 마이그레이션 작업 계획서

이 문서는 Airflow 2.x에서 3.x로의 구현을 마이그레이션하는 단계를 설명하며, 설정, 중단(deprecation) 처리, 그리고 DAG의 현대화를 우선순위로 둡니다.

## 1. Airflow 3.x 마이그레이션 필수 사항 (우선순위: 높음)
*목표: 2.x 기능과 동일하게 동작하는 3.x 환경을 구축합니다.*

- [ ] **의존성 마이그레이션 (Dependency Migration)**:
    - [ ] `migration-3_x/requirements.txt` 업데이트.
    - [ ] `astro-sdk-python` 추가 (`aql` 함수 사용에 필수).
    - [ ] `apache-airflow-providers-docker` 추가.
    - [ ] `apache-airflow-providers-amazon` 추가 (MinIO 용).
    - [ ] `apache-airflow-providers-postgres` 추가.
- [ ] **코드 마이그레이션 (Code Migration)**:
    - [ ] 루트의 `dags/`, `include/`, `plugins/`, `tests/` 폴더를 `migration-3_x/`로 복사.
    - [ ] `migration-3_x/.env` 업데이트 (해당되는 경우) 또는 환경 변수 이관 확인.
- [ ] **인프라 (Infrastructure)**:
    - [ ] `migration-3_x/docker-compose.override.yml`이 루트의 서비스(Spark, Metabase, MinIO)와 일치하는지 확인. *현재 `astro dev init` 기본값으로 인해 누락되었을 수 있음.*
    - [ ] `docker-compose.override.yml`의 내용을 3.x 폴더로 마이그레이션.

## 2. Provider 중단 및 커넥션 업데이트 (우선순위: 중간)
*목표: 특정 중단 사항, 특히 Postgres/SQL 커넥션 문제를 해결합니다.*

- [ ] **Provider 및 Operator 중단(Deprecation) 사항**:
    - [ ] **`PostgresOperator` 식별 및 교체**:
        - [ ] `PostgresOperator`는 deprecated 되었습니다.
        - [ ] **조치**: `airflow.providers.common.sql.operators.sql.SQLExecuteQueryOperator`로 교체해야 합니다.
        - [ ] `apache-airflow-providers-common-sql` 패키지가 설치되어 있는지 확인하고, 커넥션 타입이 호환되는지 점검합니다.
    - [ ] **Postgres 커넥션 현대화**:
        - [ ] `postgres` 커넥션 타입은 `apache-airflow-providers-postgres`에서 처리됩니다.
        - [ ] **리팩토링**: `common.sql` 표준에 맞추기 위해 "SQL Connection" (Generic)으로 전환을 고려합니다.
        - [ ] **점검**: `aql.load_file` (Astro SDK)이 일반 `sql` 커넥션 타입을 지원하는지 확인합니다. 지원하지 않는 경우 `postgres` 타입을 유지하되, 직접 SQL을 실행하는 태스크는 `SQLExecuteQueryOperator`를 사용하도록 변경합니다.
- [ ] **커넥션 목록**:
    - [ ] `connections_list_notes.yaml` 검토.
    - [ ] `minio`: `Amazon Web Services` 커넥션 타입 지원 확인 (`providers-amazon` 필요).
    - [ ] `stock_api`: `HTTP` 커넥션 타입 확인 (`providers-http` 필요).

## 3. 현대화된 DAG 작성 (우선순위: 중간)
*목표: `stock_market` DAG를 Airflow 3.x / TaskFlow 모범 사례로 리팩토링합니다.*

- [ ] **`PythonOperator` 제거**:
    - [ ] `get_stock_prices`, `store_prices`, `get_formatted_csv`를 `@task` 데코레이터 함수로 변환.
    - [ ] `include/stock_market/tasks.py`를 임포트 가능하게 하거나 작다면 인라인으로 리팩토링.
- [ ] **Docker 태스크 현대화**:
    - [ ] 더 깔끔한 문법을 위해 `DockerOperator`를 `@task.docker` (TaskFlow Docker)로 대체 가능한지 확인 (`apache-airflow-providers-docker>=4.0.0` 필요).
- [ ] **센서 최적화**:
    - [ ] `is_api_available`은 동기식 대기(synchronous wait)를 실행합니다. 3.x에서 유효하다면 워커 슬롯을 절약하기 위해 **Deferrable Operator** (Triggers)를 사용.
    - [ ] 커스텀 파이썬 센서를 `HttpSensor` (비동기)로 대체하거나, 커스텀 로직을 유지하되 Deferrable하게 만들 것을 제안.

## 4. 컴포넌트 업그레이드 (우선순위: 낮음)
*목표: 외부 서비스 업그레이드.*

- [ ] **Spark**:
    - [ ] 현재: `airflow/spark-master` (버전 고정 안됨/태그 의존).
    - [ ] 조치: Airflow 3.x 환경과 호환되는 최신 안정형 Spark 이미지 확인.
- [ ] **Metabase**:
    - [ ] 현재: `v0.52.8.4`.
    - [ ] 조치: 더 새로운 릴리스 확인 (예: v0.53+).
- [ ] **MinIO**:
    - [ ] 현재: `RELEASE.2024-06-13...`.
    - [ ] 최신 안정형 릴리스로 업데이트.

---
**다음 즉시 조치**: `migration-3_x`를 구동하기 위해 "의존성 마이그레이션" 및 "코드 마이그레이션" 실행.
