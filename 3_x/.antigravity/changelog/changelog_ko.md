# 변경 로그 - Airflow 3.x 마이그레이션 및 리팩토링

## [2026-02-14] 마이그레이션 업데이트

### 의존성 업데이트 (Dependency Updates)
- **추가됨**: 최신 SQL 실행 패턴을 지원하기 위해 `apache-airflow-providers-common-sql` 패키지를 추가했습니다.
- **추가됨**: Hook의 UI 위젯 지원을 활성화하고 `PostgresHook` 초기화 시 발생하는 정보 메시지를 억제하기 위해 `flask-appbuilder`를 추가했습니다.
- **제거됨**: 의존성 복잡성을 줄이고 서드파티 추상화에 대한 의존도를 낮추기 위해 `astro-sdk-python` 및 `sqlalchemy`를 제거했습니다.
- **확인됨**: 프로바이더 패키지가 Airflow 3.x와 호환되는지 확인했습니다.
- **환경**: 요청하신 대로 의존성 관리를 위해 `uv`로 전환했습니다.

### 코드 리팩토링 (Code Refactoring)
#### `dags/stock_market.py`
- **임포트(Import) 업데이트**:
    - `airflow.decorators` → `airflow.sdk` (`@dag`, `@task` 사용 시).
    - `airflow.hooks.base` → `airflow.sdk.bases.hook` (`BaseHook` 사용 시).
    - `airflow.sensors.base` → `airflow.sdk.bases.sensor` (`PokeReturnValue` 사용 시).
    - `airflow.sensors.base` → `airflow.sdk.bases.sensor` (`PokeReturnValue` 사용 시).
- **표준 오퍼레이터(Standard Operators)**:
    - `astro-sdk` (`aql.load_file`)를 표준 Airflow 패턴으로 대체했습니다:
        - `SQLExecuteQueryOperator`: `stock_market` 테이블 생성에 사용되었습니다.
        - `PythonOperator` (`@task`): `PostgresHook`과 `COPY` 명령어를 사용하여 MinIO에서 Postgres로 데이터를 로드하도록 구현했습니다.
- **몽키패치(Monkeypatch) 제거**: SDK를 더 이상 사용하지 않으므로 `astro.files.File` 몽키패치를 제거했습니다.

#### `include/stock_market/tasks.py`
- **임포트(Import) 업데이트**:
    - `airflow.hooks.base` → `airflow.sdk.bases.hook` (`BaseHook` 사용 시).

### 인프라 수정 (Infrastructure Fixes)
- **Docker Proxy**: `docker-compose.override.yml`에 `hostname: docker-proxy`를 추가하여 `AirflowException`을 유발하던 DNS 해석 실패 문제를 해결했습니다.

### 사용 중단 처리 (Deprecation Handling)
- **PostgresOperator**: 사용 중단된 `PostgresOperator`의 사용 여부를 확인했습니다. 현재 DAG 코드 내에서 명시적인 사용은 발견되지 않았습니다.
    - *참고*: 향후 SQL 태스크를 추가할 때는 `PostgresOperator` 대신 `airflow.providers.common.sql.operators.sql.SQLExecuteQueryOperator`를 사용하십시오.
- **Docker Provider**: 내부적으로 발생하는 사용 중단 경고를 해결하기 위해 `apache-airflow-providers-docker`를 최신 버전으로 업데이트했습니다.
- **Dockerfile**: `astro-sdk` (현재 제거됨)를 패치하던 레거시 `sed` 명령어를 제거하여 Docker 빌드 오류를 수정했습니다.

