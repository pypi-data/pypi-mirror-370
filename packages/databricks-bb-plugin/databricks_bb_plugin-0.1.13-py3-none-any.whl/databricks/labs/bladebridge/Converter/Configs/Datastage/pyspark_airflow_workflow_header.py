# This is a standard header for workflow %WORKFLOW_NAME%
from datetime import datetime, timedelta
import os
import pendulum
from airflow import DAG
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from airflow.models import Variable

default_args = {
    'start_date': datetime.utcnow(),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1
}

dag = DAG('%WORKFLOW_NAME%',
        description='Main',
        default_args=default_args,
        schedule_interval='@once',
        start_date=datetime.now(),
        )

pyspark_app_home = 'home'
