from airflow.sdk import dag, task
from airflow.sdk.bases.hook import BaseHook
from airflow.sdk.bases.sensor import PokeReturnValue
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from include.stock_market.tasks import (
    _get_stock_prices,
    _store_prices,
    _get_formatted_csv,
    BUCKET_NAME,
    _get_minio_client,
)


SYMBOL = "NVDA"


@dag(
    start_date=datetime(2023, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["stock_market"],
)
def stock_market():

    # [Modernized/현대화됨] Converted to TaskFlow sensor / TaskFlow 센서로 변환
    @task.sensor(poke_interval=30, timeout=300, mode="poke")
    def is_api_available() -> PokeReturnValue:
        import requests

        api = BaseHook.get_connection("stock_api")
        url = f"{api.host}{api.extra_dejson['endpoint']}"
        print(url)
        response = requests.get(url, headers=api.extra_dejson["headers"])
        condition = response.json()["finance"]["result"] is None
        return PokeReturnValue(is_done=condition, xcom_value=url)

    # [Modernized/현대화됨] Wrapper task for _get_stock_prices / _get_stock_prices를 위한 래퍼 태스크
    @task
    def get_stock_prices(url, symbol):
        return _get_stock_prices(url, symbol)

    # [Modernized/현대화됨] Wrapper task for _store_prices / _store_prices를 위한 래퍼 태스크
    @task
    def store_prices(stock):
        return _store_prices(stock)

    # [Note] Keep DockerOperator as it runs a pre-built image. @task.docker is for running python functions in docker.
    # [참고] 사전 빌드된 이미지를 실행하므로 DockerOperator 유지. @task.docker는 도커 내에서 파이썬 함수를 실행할 때 사용.
    format_prices = DockerOperator(
        task_id="format_prices",
        image="airflow/stock-app",
        api_version="auto",
        auto_remove="success",
        docker_url="tcp://docker-proxy:2375",
        network_mode="container:spark-master",
        tty=True,
        xcom_all=False,
        mount_tmp_dir=False,
        environment={
            "SPARK_APPLICATION_ARGS": '{{ ti.xcom_pull(task_ids="store_prices") }}'
        },
    )

    # [Modernized/현대화됨] Wrapper task for _get_formatted_csv / _get_formatted_csv를 위한 래퍼 태스크
    @task
    def get_formatted_csv(path):
        return _get_formatted_csv(path)

    # [Replaced/교체됨] Create table using SQLExecuteQueryOperator / SQLExecuteQueryOperator를 사용한 테이블 생성
    create_table = SQLExecuteQueryOperator(
        task_id="create_table",
        conn_id="postgres",
        sql="""
            CREATE TABLE IF NOT EXISTS stock_market (
                timestamp BIGINT,
                close DOUBLE PRECISION,
                high DOUBLE PRECISION,
                low DOUBLE PRECISION,
                open DOUBLE PRECISION,
                volume BIGINT,
                date TEXT
            );
        """,
    )

    # [Replaced/교체됨] Load data to Postgres using Python task (replaces aql.load_file) / Python 태스크를 사용하여 Postgres로 데이터 로드 (aql.load_file 대체)
    @task
    def load_to_dw(file_path):
        # 1. Read file from MinIO
        minio_client = _get_minio_client()
        bucket_name = BUCKET_NAME

        # Ensure we have the full object name. The 'file_path' from xcom might need adjustment if it's full URI or just key.
        # previous get_formatted_csv returns the object name (e.g. key).
        obj = minio_client.get_object(bucket_name, file_path)

        # 2. Load to Postgres using COPY
        postgres_hook = PostgresHook(postgres_conn_id="postgres")
        conn = postgres_hook.get_conn()
        cursor = conn.cursor()

        # Use COPY command to load from stream
        # Note: We need to handle CSV format. The previous code didn't specify CSV options explicitly but likely assumed default or inferred.
        # Assuming standard CSV with header.
        sql = "COPY stock_market FROM STDIN WITH (FORMAT CSV, HEADER TRUE)"
        cursor.copy_expert(sql, obj)

        conn.commit()
        cursor.close()
        conn.close()
        # obj stream should be closed? minio response object is a stream.
        obj.close()
        obj.release_conn()

    # Task dependencies / 태스크 의존성
    stock_api_uri = is_api_available()
    stock_json = get_stock_prices(url=stock_api_uri, symbol=SYMBOL)
    stored_path = store_prices(stock=stock_json)

    # Chain definition / 체인 정의
    # store_prices -> format_prices (Docker) -> get_formatted_csv -> load_to_dw

    formatted_csv = get_formatted_csv(path=stored_path)

    # Enforce order: Docker task must finish before checking CSV
    # 순서 강제: CSV 확인 전에 Docker 태스크가 완료되어야 함
    stored_path >> format_prices >> formatted_csv

    formatted_csv >> create_table >> load_to_dw(file_path=formatted_csv)


stock_market()
