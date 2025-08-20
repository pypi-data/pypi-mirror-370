#TO BE REMOVED
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from airflow.sdk import DAG, BaseOperator
from airflow.utils.trigger_rule import TriggerRule

from gcs_utils import upload_to_gcs, download_failed_models
from astrafy_environment import AstrafyEnvironment
from k8s_utils import node_affinity, gke_bash
  


def dbt_image(data_product:str,tag_name: str) -> str:
    """
    @return the reference to the DBT image built for the given tag_name
    @param tag_name: the name of tag
    """
    return f'europe-west1-docker.pkg.dev/prj-astrafy-artifacts/mds/dbt/{data_product}:{tag_name}'


def dbt_target_arg(environment: AstrafyEnvironment) -> str:
    return f"""--target="{environment.data_product}-{environment.env}-ci-airflow" """


def dbt_vars(other_vars: dict = None):
    """
    Builds the dbt --vars argument with the default value taken from airflow vars and environment:
    - dag_id,
    - dag_ts,
    - source_db_main
    """
    ts = "{{ ts }}"
    run_id = "{{ run_id }}"
    defaults = f""" --vars '{{ "dag_id": "{ run_id }" , "dag_ts": "{ ts }", "orchestrator": "Airflow", "job_run_id": "{run_id}" """
    if other_vars is not None:
        for key in other_vars:
            defaults = defaults + f""", "{key}": "{other_vars[key]}" """
    defaults = defaults + "}'"
    return defaults


def dbt_in_pod(dag: DAG, task_id: str, tag_version: str, data_product:str, env_vars:str,cmd: str,               
               trigger_rule: TriggerRule = TriggerRule.ONE_SUCCESS,
               affinity: object = node_affinity(),
               service_account: str = 'dbt-ksa') -> BaseOperator:
    """
    Instantiates a GKEStartPodOperator to run a dbt command. It uses all the default variables to simplify the work
    needed to create a DBT job
    @param trigger_rule: (optional) The trigger rule, default is ALL_SUCCESS
    @param affinity: the affinity to select the node pool of execution. Default to node_affinity() which use the
    'composer' node pool.
    @param dag:
    @param task_id:
    @param cmd:
    @param tag_version:
    @param service_account: if a specific service_account is needed ('dbt-ksa' by default)
    @return: the GKEStartPodOperator
    """
    return gke_bash(dag, task_id, dbt_image(data_product,tag_version), cmd, env_vars,trigger_rule, affinity,service_account)

def dbt(
        profile_arg: str,
        target_arg: str,
        environment: AstrafyEnvironment,
        dbt_command: str = "build",
        vars_arg: str = dbt_vars(),
        other_args: str = ""):
    """
    Builds the complete dbt command and uploads the dbt result files to the GCS bucket managed folder for further reuse. 
    It fails if no `bucket_folder_results` is set in the environment.

    @param profile_arg: the profile arg if the default (--profiles-dir=/app/_profiles_v2) doesn't apply
    @param target_arg: the target arg if the default doesn't apply (--target="{environment.env}")
    @param environment: AstrafyEnvironment instance with the configuration
    @param dbt_command: the dbt command ex: `run`, `build`, `test --select models/vc` defaults to `build`
    @param vars_arg: the variables of the dbt command. In the form of '--vars { "var1": "val1", "var2": "val2"}'.
                     By default, use the result of dbt_vars() which sets dag_id, dag_ts, orchestrator,
                     and job_run_id variables.
    @param other_args: any additional args to pass to the dbt command
    @return: the complete command string
    """

    upload_cmd = upload_to_gcs(environment)

    return f"""
    dbt {dbt_command} --profiles-dir={profile_arg} {target_arg} {vars_arg} {other_args}; dbt_ret=$?;

    {upload_cmd}
    gcp=$?

    if [ $dbt_ret -ne 0 -o $gcp -ne 0 ]; then
        exit 1;
    else
        exit 0;
    fi
    """


def dbt_freshness_and_upload_cmd(
        profile_arg,
        target_arg: str,
        environment: AstrafyEnvironment,
        dbt_command: str = "",
        vars_arg: str = dbt_vars(),
        other_args: str = ""):
    """
    Execute the given command and upload the dbt result files (manifest.json and run-results.json)
    to the datalake bucket for further treatments.
    @param dbt_command: the arguments for the dbt run command (ex: --select models/vc )
    @param vars_arg: the variables of the dbt command. In the form of '--vars { "var1": "val1", "var2": "val2"}'.
                     By default, use the result of dbt_vars() which sets dag_id, dat_ts, source_db_main,
                     source_db_legacy variables. If you want more variables, you should probably call dbt_vars() with
                     some extra vars.
    @param other_args: any additional args to pass to the dbt command
    @param profile_arg: the profile arg if the default (--profiles-dir=/app/_profiles_v2) doesn't apply
    @param target_arg: the target arg if the default doesn't apply (--target="{environment.env}")
    @return: the complete command string
    """
    return dbt(profile_arg,target_arg, environment,f"source freshness {dbt_command}",vars_arg,other_args)


def dbt_test_and_upload_cmd(
        profile_arg,
        target_arg: str,
        environment: AstrafyEnvironment,
        dbt_command: str = "",
        vars_arg: str = dbt_vars(),
        other_args: str = ""):
    """
    Execute the given command and upload the dbt result files (manifest.json and run-results.json)
    to the datalake bucket for further treatments.

    @deprecated use dbt_cmd() instead.
    @param dbt_command: the arguments for the dbt run command (ex: --select models/vc )
    @param vars_arg: the variables of the dbt command. In the form of '--vars { "var1": "val1", "var2": "val2"}'.
                     By default, use the result of dbt_vars() which sets dag_id, dat_ts, source_db_main,
                     source_db_legacy variables. If you want more variables, you should probably call dbt_vars() with
                     some extra vars.
    @param other_args: any additional args to pass to the dbt command
    @param profile_arg: the profile arg if the default (--profiles-dir=/app/_profiles_v2) doesn't apply
    @param target_arg: the target arg if the default doesn't apply (--target="{environment.env}")
    @return: the complete command string
    """
    return dbt(profile_arg,target_arg, environment,f"test {dbt_command}",vars_arg,other_args)


def dbt_run_and_upload_cmd(
        profile_arg,
        target_arg: str,
        environment: AstrafyEnvironment,
        dbt_command: str = "",
        vars_arg: str = dbt_vars(),
        other_args: str = ""):
    """
    Builds the complete dbt command with the upload of the dbt result files (manifest.json and run-results.json)
    to the datalake bucket for further analysis.
    @param dbt_command: the arguments for the dbt run command (ex: --select models/vc )
    @param vars_arg: the variables of the dbt command. In the form of '--vars { "var1": "val1", "var2": "val2"}'.
                     By default, use the result of dbt_vars() which sets dag_id, dat_ts, source_db_main,
                     source_db_legacy variables. If you want more variables, you should probably call dbt_vars() with
                     some extra vars.
    @param other_args: any additional args to pass to the dbt command
    @param profile_arg: the profile arg if the default (--profiles-dir=/app/_profiles_v2) doesn't apply
    @param target_arg: the target arg if the default doesn't apply (--target="{environment.env}")
    @return: the complete command string
    """
    return dbt(profile_arg,target_arg, environment,f"run {dbt_command}",vars_arg,other_args)


def dbt_seed_and_upload_cmd(
        profile_arg,
        target_arg: str,
        environment: AstrafyEnvironment,
        dbt_command: str = "",
        vars_arg: str = dbt_vars(),
        other_args: str = ""):
    """
    Builds the complete dbt command for seed with the upload of the dbt result files (manifest.json and run-results.json)
    to the datalake bucket for further analysis.
    @param dbt_command: the arguments for the dbt run command (ex: --select models/vc )
    @param vars_arg: the variables of the dbt command. In the form of '--vars { "var1": "val1", "var2": "val2"}'.
                     By default, use the result of dbt_vars() which sets dag_id, dat_ts, source_db_main,
                     source_db_legacy variables. If you want more variables, you should probably call dbt_vars() with
                     some extra vars.
    @param other_args: any additional args to pass to the dbt command
    @param profile_arg: the profile arg if the default (--profiles-dir=/app/_profiles_v2) doesn't apply
    @param target_arg: the target arg if the default doesn't apply (--target="{environment.env}")
    @return: the complete command string
    """
    return dbt(profile_arg,target_arg, environment,f"seed {dbt_command}",vars_arg,other_args)

def dbt_run_only_failed(
        profile_arg: str,
        target_arg: str,
        environment: AstrafyEnvironment,
        dbt_command: str = "build",
        vars_arg: str = dbt_vars(),
        other_args: str = ""):
    """
    On DAG's try nº 2 it automatically downloads whatever it failed/errored on the last run 
    from the managed folder given bucket in order to retry to execute it, 
    on others tries it simply runs the util's dbt command.

    @param profile_arg: the profile arg if the default doesn't apply
    @param target_arg: the target arg if the default doesn't apply
    @param environment: AstrafyEnvironment instance with the configuration
    @param dbt_command: the dbt command ex: `run`, `build`, `test --select models/vc` defaults to `build`
    @param vars_arg: the variables of the dbt command
    @param other_args: any additional args to pass to the dbt command
    @return: the complete command string
    """

    download_failed_models_cmd = download_failed_models(environment)
    upload_cmd = upload_to_gcs(environment)

    return f"""
    if [ {{{{ ti.try_number }}}} -eq 2 ]; then
        {download_failed_models_cmd}
        gcp=$?;

        dbt {dbt_command} --select result:fail+ result:error+ --state /app/target --profiles-dir={profile_arg} {target_arg} {vars_arg} {other_args}; dbt_ret=$?;
    else
        dbt {dbt_command} --profiles-dir={profile_arg} {target_arg} {vars_arg} {other_args}; dbt_ret=$?;
        
        {upload_cmd}
        gcp=$?;
    fi
    
    
    if [ $dbt_ret -ne 0 -o $gcp -ne 0 ]; then
        exit 1;
    else
        exit 0;
    fi
    """