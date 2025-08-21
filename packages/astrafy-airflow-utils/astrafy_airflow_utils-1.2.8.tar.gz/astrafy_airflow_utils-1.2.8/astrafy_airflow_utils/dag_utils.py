import pendulum
from datetime import datetime, timedelta
from airflow.sdk import Param

def default_dag(data_product, ENV, schedule= '0 10 * * *',start_date=pendulum.datetime(2022, 10, 10, tz="Europe/Amsterdam"),**kwargs):
    dag = {
        "dag_id": f'{data_product}-k8s-dag-{ENV}',
        "schedule": schedule,
        "description": f'Dag for the {data_product} data product - {ENV}',
        "max_active_tasks": 10,
        "catchup": False,
        "is_paused_upon_creation": True,
        "tags": ['k8s', data_product],
        "max_active_runs": 1,
        "dagrun_timeout": timedelta(seconds=36000),
        "sla_miss_callback": None,
        "params": {"is_full_refresh": Param(False, type="boolean")},
        "start_date": start_date,
        "doc_md": __doc__,
    }
    
    dag.update(kwargs)
    
    return dag