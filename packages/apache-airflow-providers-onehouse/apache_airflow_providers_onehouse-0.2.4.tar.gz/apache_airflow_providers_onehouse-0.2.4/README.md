# Apache Airflow Provider for Onehouse

[![PyPI version](https://img.shields.io/pypi/v/apache-airflow-providers-onehouse)](https://pypi.org/project/apache-airflow-providers-onehouse/)
[![Build Status](https://github.com/onehouseinc/airflow-providers-onehouse/workflows/Publish%20to%20PyPI/badge.svg)](https://github.com/onehouseinc/airflow-providers-onehouse/actions/workflows/publish-to-pypi.yml)

This is the Apache Airflow provider for Onehouse. It provides operators and sensors for managing Onehouse resources through Apache Airflow.

## Requirements

- Apache Airflow >= 2.9.2
- Python >= 3.10

## Installation

You can install this provider package via pip:

```bash
pip install apache-airflow-providers-onehouse
```

## Configuration

1. Set up an Airflow connection with the following details:

   - Connection Id: `onehouse_default` (or your custom connection id)
   - Connection Type: `Generic`
   - Host: `https://api.onehouse.ai`
   - Extra: Configure the following JSON:
     ```json
     {
       "project_uid": "your-project-uid",
       "user_id": "your-user-id",
       "api_key": "your-api-key",
       "api_secret": "your-api-secret",
       "link_uid": "your-link-uid",
       "region": "your-region"
     }
     ```

## Usage

### Basic Example DAG

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow_providers_onehouse.operators.clusters import (
    OnehouseCreateClusterOperator,
    OnehouseDeleteClusterOperator,
)
from airflow_providers_onehouse.operators.jobs import (
    OnehouseCreateJobOperator,
    OnehouseRunJobOperator,
    OnehouseDeleteJobOperator,
)
from airflow_providers_onehouse.sensors.onehouse import OnehouseJobRunSensor, OnehouseCreateClusterSensor

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

cluster_name = "cluster_1"
job_name = "job_1"

bucket_name = "bucket-name"
job_path = "s3a://{bucket_name}/path/to/hello_world_job.py"
venv_path = "s3a://{bucket_name}/path/to/venv.tar.gz"

with DAG(
        dag_id="example_dag",
        default_args=default_args,
        description="Example DAG",
        schedule_interval=None,
        start_date=datetime(2025, 4, 28),
        catchup=False,
        tags=["onehouse", "example", "dag"],
) as dag:

    create_cluster = OnehouseCreateClusterOperator(
        task_id="create_onehouse_cluster",
        cluster_name=cluster_name,
        cluster_type="Spark",
        max_ocu=1,
        min_ocu=1,
        conn_id="onehouse_default",
    )

    wait_for_cluster_ready = OnehouseCreateClusterSensor(
        task_id="wait_for_cluster_ready",
        cluster_name="{{ ti.xcom_pull(task_ids='create_onehouse_cluster') }}",
        conn_id="onehouse_default",
        poke_interval=30,
        timeout=60 * 30,
    )

    create_onehouse_job = OnehouseCreateJobOperator(
        task_id="create_onehouse_job",
        job_name=job_name,
        job_type="PYTHON",
        parameters=[
            "--conf", f"spark.archives={venv_path}#environment",
            "--conf", "spark.pyspark.python=./environment/bin/python",
            job_path,
        ],
        cluster_name=cluster_name,
        conn_id="onehouse_default",
    )

    run_onehouse_job = OnehouseRunJobOperator(
        task_id="run_onehouse_job",
        job_name=job_name,
        conn_id="onehouse_default",
    )

    wait_for_job = OnehouseJobRunSensor(
        task_id="wait_for_job_completion",
        job_name=job_name,
        job_run_id="{{ ti.xcom_pull(task_ids='run_onehouse_job') }}",
        conn_id="onehouse_default",
        poke_interval=30,
        timeout=60 * 60,
    )

    delete_onehouse_job = OnehouseDeleteJobOperator(
        task_id="delete_onehouse_job",
        job_name=job_name,
        conn_id="onehouse_default",
    )

    delete_onehouse_cluster = OnehouseDeleteClusterOperator(
        task_id="delete_onehouse_cluster",
        cluster_name=cluster_name,
        conn_id="onehouse_default",
    )

    (
            create_cluster
            >> wait_for_cluster_ready
            >> create_onehouse_job
            >> run_onehouse_job
            >> wait_for_job
            >> delete_onehouse_job
            >> delete_onehouse_cluster
    ) 
```
