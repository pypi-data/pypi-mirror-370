"""
---
author:

- name: Nawfel Bacha
- email: nawfel@astrafy.io
- updated on: 06-12-2024

---
## **READ CAREFULLY**
## 1. How Monitoring Flow works:
Each monitoring DAG is dedicated to a specific data source and runs on its own schedule:

- airbyte: Runs twice a day
- airflow: Runs twice a day
- bq_monitoring: Runs twice a day
- gke_monitoring: Runs once a day
- Cloud Asset inventory: Runs once a day

#### 1.1 Execution options
Each DAG has one parameter that can be configured:

1. `is_full_refresh`: Boolean parameter to specify whether to run in full-refresh or incremental mode
   - Set to `true` to run in full-refresh mode
   - Leave as `false` (default) to run in incremental mode

To configure parameters:
1. Go to the DAG and select "Trigger DAG w/ config"
2. Specify parameters in JSON format, e.g:
   ```json
   {
     "is_full_refresh": true
   }
   ```
3. If no config is provided, DAG runs incrementally
"""
# IMPORT ASTRAFY AIRFLOW LIBRARY
from astrafy_airflow_utils.astrafy_environment import AstrafyEnvironment
from astrafy_airflow_utils.dbt import dbt_in_pod, dbt_image, dbt
from astrafy_airflow_utils.k8s_utils import gke_bash, node_affinity
from astrafy_airflow_utils.dag_utils import default_dag
from astrafy_airflow_utils.elementary import get_elementary_command
from astrafy_airflow_utils.slack_alert import task_fail_slack_alert

# IMPORT NEEDED FOR THE DAG
import logging
from datetime import timedelta
from airflow.utils.trigger_rule import TriggerRule
from airflow.sdk import DAG, Variable, TaskGroup, task
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.providers.standard.operators.python import get_current_context

logger = logging.getLogger(__name__)

# Set constants
DATA_PRODUCT = 'monitoring'
ENV = Variable.get('ENV', 'dev')

SERVICE_ACCOUNT = "sa-dp-monitoring-dev@astrafy-gke-dev.iam.gserviceaccount.com"

MONITORING_CONFIGS = {
    'bq': "0 11 * * *",
    'looker': "0 15 * * *",
    'cai': "30 11 * * *"
}

# Create a DAG for each monitoring source
for tag, schedule in MONITORING_CONFIGS.items():
    environment = AstrafyEnvironment(DATA_PRODUCT, sub_data_product=tag)
    environment.add_env_vars({"GIT_KEY": f"{Variable.get('GIT_KEY')}"})
    environment.add_env_vars({"USER": "airflow"})
    dag_id = f'{DATA_PRODUCT}-{tag}-k8s-dag-{ENV}'
    image_version = Variable.get(f"DP_MONITORING_{tag.upper()}_VERSION")
    with DAG(**default_dag(
            data_product=DATA_PRODUCT,
            ENV=ENV,
            schedule=schedule,
            default_args={
                'owner': 'lucas.reis',
                'retries': 1,
                'retry_delay': timedelta(seconds=60),
                'on_failure_callback': task_fail_slack_alert
            },
            dag_id=dag_id
    )
             ) as dag:
        full_refresh_arg = (
            "{{'--full-refresh' if dag_run.conf.get('is_full_refresh') else ''}}"
        )

        with TaskGroup(group_id='Ingestion') as Ingestion:
            if tag == 'cai':
                load_cai_append = gke_bash(
                    dag=dag,
                    task_id="cai_to_bq_append",
                    image="europe-west1-docker.pkg.dev/prj-astrafy-artifacts/utils/asset-inventory:latest",
                    # IMPORTANT: use /bin/sh -c (not bash) and pass a single shell string
                    cmds=["/bin/sh", "-c"],
                    arguments=(
                        "python /app/src/main.py "
                        "--impersonate-service-account sa-asset-inventory-fetch@astrafy-gke.iam.gserviceaccount.com "
                        "--organization-id 225464104659 "
                        "--bq-project-id internal-data-lz-prd-86b7 "
                        "--bq-dataset-id bqdts_asset_inventory "
                        "--table-prefix cai_assets "
                        "--partition-key read-time "
                        f"{full_refresh_arg}"
                    ),
                    env_vars=environment.env_vars,
                    trigger_rule=TriggerRule.ALL_SUCCESS,
                    affinity=node_affinity(),
                    service_account="dbt-ksa"
                )

                clone_tables_cai = KubernetesPodOperator(
                    image_pull_policy="Always",
                    is_delete_operator_pod=True,
                    namespace='dbt',
                    get_logs=True,
                    image="europe-west1-docker.pkg.dev/prj-astrafy-artifacts/mds/clone-tables:latest",
                    service_account_name='dbt-ksa',
                    cmds=["python", "clone_tables.py"],
                    arguments=[
                        "--src_project", "internal-data-lz-prd-86b7",
                        "--src_dataset", "bqdts_asset_inventory",
                        "--dest_project", "internal-data-lz-dev-7c5c",
                        "--dest_dataset", "bqdts_asset_inventory",
                        "--impersonated_sa", "sa-asset-inventory-fetch@astrafy-gke.iam.gserviceaccount.com"
                    ],
                    name="clone-tables-cai",
                    task_id="clone-tables-cai",
                )

                load_cai_append >> clone_tables_cai

        with TaskGroup(group_id='Transformations') as Transformations:
            dbt_in_pod(
                dag=dag,
                task_id="dbt_run",
                tag_version=image_version,
                data_product=DATA_PRODUCT,
                env_vars=environment.env_vars,
                cmd=dbt(
                    profile_arg="/app",
                    target_arg=f"--target={environment.env}",
                    environment=environment,
                    dbt_command=f"run",
                    other_args=full_refresh_arg
                )
            )


        edr_report = gke_bash(
            dag, "upload_edr_report",
            dbt_image(DATA_PRODUCT, image_version),
            get_elementary_command(SERVICE_ACCOUNT,
                                   f"bqdts_{DATA_PRODUCT}_elementary", f"csb-europe-west1-dbt-elementary-{ENV}",
                                   environment.monitoring_project, DATA_PRODUCT, 
                                   sub_data_product=tag),
            environment.env_vars, TriggerRule.ONE_SUCCESS, node_affinity(), 'dbt-ksa'
        )

    if tag == "cai" and ENV == "prd":
        Ingestion >> Transformations >> edr_report
    else:
        Transformations >> edr_report
