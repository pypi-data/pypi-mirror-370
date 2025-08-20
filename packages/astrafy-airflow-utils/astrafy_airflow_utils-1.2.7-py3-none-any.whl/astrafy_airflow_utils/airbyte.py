#TO BE REMOVED
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from airflow.providers.airbyte.operators.airbyte import AirbyteTriggerSyncOperator
from airflow.sdk import DAG
from astrafy_environment import AstrafyEnvironment


def airbyte_sync(task_id,env: AstrafyEnvironment,dag: DAG = None,) ->AirbyteTriggerSyncOperator:
    dag = dag
    async_source_destination = AirbyteTriggerSyncOperator(
        task_id=task_id,
        airbyte_conn_id=env.airflow_connection_name,
        connection_id=env.airbyte_conn_id,
        asynchronous=False,
        timeout=3600,
        wait_seconds=3,
        dag=dag
        )
    return async_source_destination