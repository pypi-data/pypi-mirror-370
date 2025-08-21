import pendulum
from kubernetes.client import models as k8s
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.sdk import Variable, Param
from datetime import datetime, timedelta

class ConfigVars:

    def __init__(self):
        COMMON_GITLAB_PAT = Variable.get("COMMON_GITLAB_PAT")
        env_vars = [
            set_env_vars(name="STG_PROJECT_ID", key="STG_PROJECT_ID"),
            set_env_vars(name="LZ_PROJECT_ID", key="LZ_PROJECT_ID"),
            set_env_vars(name="DM_PROJECT_ID", key="DM_PROJECT_ID"),
            set_env_vars(name="DW_PROJECT_ID", key="DW_PROJECT_ID"),
            set_env_vars(name="COMMON_GITLAB_PAT", value=COMMON_GITLAB_PAT)
        ]
        self.env_vars = env_vars


class DbtRunDefaults:
    image_pull_policy = "Always"
    cmds = ["/bin/bash", "-c"]

    get_logs = True
    service_account_name = 'dbt-ksa'
    namespace = "dbt"
    affinity = {'nodeAffinity': {'requiredDuringSchedulingIgnoredDuringExecution':
        {'nodeSelectorTerms': [
            {'matchExpressions': [
                {'key': 'node_pool',
                 'operator': 'In',
                 'values': ['dbt']
                 }
            ]
            }
        ]
        }
    }
    }

    def __init__(self, data_product, environment):
        self.dbt_target_gke = f'{data_product}-{environment}-ci-airflow'
        self.dbt_target = f""" --target="{self.dbt_target_gke}" """
        self.run_id = '{{ run_id }}'
        self.dag_ts = '{{ ts }}'
        self.dbt_profile = f""" --profiles-dir=/app/artifacts"""
        self.dbt_vars = f""" --vars '{{"dag_id": "{self.run_id}" , "dag_ts": "{self.dag_ts}", "orchestrator": "Airflow", 
        "job_run_id": "{self.run_id}"}}'"""
        self.dbt_args = f"""{self.dbt_vars}{self.dbt_target}{self.dbt_profile}"""
        self.docker_image = "europe-west1-docker.pkg.dev/prj-astrafy-artifacts/mds"

def default_dag(data_product, ENV, **kwargs):
    dag = {
        "dag_id": f'{data_product}-k8s-dag-{ENV}',
        "schedule": '0 10 * * *',
        "description": f'Dag for the {data_product} data product - {ENV}',
        "max_active_tasks": 10,
        "catchup": False,
        "is_paused_upon_creation": True,
        "tags": ['k8s', data_product],
        "max_active_runs": 1,
        "dagrun_timeout": timedelta(seconds=36000),
        "sla_miss_callback": None,
        "params": {"is_full_refresh": Param(False, type="boolean")},
        "start_date": pendulum.datetime(2022, 10, 10, tz="Europe/Amsterdam"), 
        "doc_md": __doc__,
    }
    
    dag.update(kwargs)
    
    return dag


def cd_to_local_package(package: str) -> str:
    return f"cd /app/data_products/{package}/"


def set_env_vars(name: str, value=None, key=None):
    if value:
        env_var = k8s.V1EnvVar(name=name, value=value)
        return env_var
    if key:
        env_var = k8s.V1EnvVar(name=name, value_from=k8s.V1EnvVarSource(
            config_map_key_ref=k8s.V1ConfigMapKeySelector(name="internal-data-dbt-config-map", key=key)))
        return env_var

def setup_env_vars(data_product, environment, additional_vars=None):
    """
    Set up environment variables for a given data product and environment,
    with the option to add additional variables.
    """
    config_vars = ConfigVars()

    # Extend with additional environment variables specific to the DAG
    additional_env_vars = [
        set_env_vars(name="DATA_PRODUCT", value=data_product),
        set_env_vars(name="ENV", value=environment)
    ]

    if additional_vars:
        additional_env_vars.extend([
            set_env_vars(name=var_name, value=var_value) for var_name, var_value in additional_vars.items()
        ])

    config_vars.env_vars.extend(additional_env_vars)
    return config_vars.env_vars

def construct_dbt_run_command(dbt_defaults, selector, mode):
    """
    Construct a DBT command using the DbtRunDefaults settings, a selector, and a specified mode.
    """
    dbt_selector = f"--selector {selector}"
    return f"dbt run {dbt_defaults.dbt_args} {dbt_selector} {mode};exit $?"

def create_dbt_task(task_id, name, command, dbt_defaults, env_vars, data_product):
    """
    Create a KubernetesPodOperator task for running DBT commands.
    """
    DP_VERSION = Variable.get(f"DP_{data_product.upper()}_VERSION")
    return KubernetesPodOperator(
        task_id=task_id,
        name=name,
        image=f"{dbt_defaults.docker_image}/dbt/{data_product}:{DP_VERSION}",
        cmds=dbt_defaults.cmds,
        arguments=[command],
        image_pull_policy=dbt_defaults.image_pull_policy,
        namespace=dbt_defaults.namespace,
        get_logs=dbt_defaults.get_logs,
        service_account_name=dbt_defaults.service_account_name,
        affinity=dbt_defaults.affinity,
        env_vars=env_vars,
    )