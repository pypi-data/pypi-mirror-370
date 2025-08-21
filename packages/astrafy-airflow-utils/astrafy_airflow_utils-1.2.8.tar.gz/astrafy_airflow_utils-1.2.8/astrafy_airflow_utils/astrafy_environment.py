import copy
from airflow.models import Variable
from dataclasses import dataclass
from kubernetes.client import models as k8s

@dataclass
class AstrafyEnvironment:
    """
    This class contains the default environment variables available during the DAG execution.
    """
   
    def __init__(self, data_product, sub_data_product=None):
        self.data_product: str                  = data_product
        self.sub_data_product: str              = sub_data_product
        self.env: str                           = Variable.get('ENV', 'dev')
        self.airflow_connection_name: str       = 'airbyte_default'
        self.airbyte_conn_id: str               = 'e6ccfe77-09d9-4829-a3fc-ce1327853337'
        self.monitoring_project: str            =  'internal-monitoring-dev-7e9d' if self.env == 'dev' else "internal-monitoring-prd-afa4"
        
        base_bucket_path                        = f"dbt-target-{self.env}-{self.data_product.replace('_', '-')}/dp-{self.data_product.replace('_', '-')}"
        if self.sub_data_product:
            self.bucket_folder_results: str = f"{base_bucket_path}/{self.sub_data_product.replace('_', '-')}"
        else:
            self.bucket_folder_results: str = base_bucket_path
            
        self.COMMON_GITLAB_PAT                  = Variable.get("COMMON_GITLAB_PAT","")
        self.GCLOUD_PROJECT = Variable.get("GCLOUD_PROJECT","")
        self.SLACK_CHANNEL_TEST = Variable.get("SLACK_CHANNEL_TEST","")
        self.SLACK_TOKEN = Variable.get("SLACK_TOKEN","")
        

        env_vars = [
            self.set_env_vars(name="STG_PROJECT_ID", key="STG_PROJECT_ID"),
            self.set_env_vars(name="LZ_PROJECT_ID", key="LZ_PROJECT_ID"),
            self.set_env_vars(name="DM_PROJECT_ID", key="DM_PROJECT_ID"),
            self.set_env_vars(name="DW_PROJECT_ID", key="DW_PROJECT_ID"),
            self.set_env_vars(name="COMMON_GITLAB_PAT", value=self.COMMON_GITLAB_PAT),
            self.set_env_vars(name="DATA_PRODUCT", value=self.data_product),
            self.set_env_vars(name="GCLOUD_PROJECT", value=self.GCLOUD_PROJECT),
            self.set_env_vars(name="SLACK_CHANNEL_TEST", value=self.SLACK_CHANNEL_TEST),
            self.set_env_vars(name="SLACK_TOKEN", value=self.SLACK_TOKEN),
        ]
        
        self.env_vars = env_vars
    
    def set_env_vars(self,name: str, value=None, key=None):
        if value:
            env_var = k8s.V1EnvVar(name=name, value=value)
            return env_var
        if key:
            env_var = k8s.V1EnvVar(name=name, value_from=k8s.V1EnvVarSource(
                config_map_key_ref=k8s.V1ConfigMapKeySelector(name="internal-data-dbt-config-map", key=key)))
            return env_var 
        
    def add_env_vars(self,additional_vars=None):
        """
        Set up environment variables for a given data product and environment,
        with the option to add additional variables.
        """

        # Extend with additional environment variables specific to the DAG
        if additional_vars:
            config_vars = copy.deepcopy(self.env_vars)
            print(additional_vars)
            config_vars.extend([
                self.set_env_vars(name=var_name, value=var_value) for var_name, var_value in additional_vars.items()
            ])

            self.env_vars  = copy.deepcopy(config_vars)
        
        return self.env_vars   
        