args = {
    'start_date': datetime.utcnow(),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1
}

dag_%COMPONENT_NAME% = DAG(dag_id='NestedConditon_%COMPONENT_NAME%', default_args=args)
task_%COMPONENT_NAME% = BashOperator(
    task_id='task_%COMPONENT_NAME%',
    depends_on_past=False,
    bash_command='%COMPONENT_NAME%.py',
    params={'script': '%COMPONENT_NAME%.py', 'retry' : '1'},
    dag=dag_%COMPONENT_NAME%
)
print("Nested condition component %COMPONENT_NAME% called")
