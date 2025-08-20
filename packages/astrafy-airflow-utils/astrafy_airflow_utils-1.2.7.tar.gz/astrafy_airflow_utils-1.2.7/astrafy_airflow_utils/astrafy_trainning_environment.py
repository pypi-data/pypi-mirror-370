import os
from typing import Dict, Optional
import copy
from kubernetes.client import models as k8s

class AstrafyTrainingEnvironment:
    """
    A class to manage environment-specific configurations for project, dataset, and service account.
    Allows overriding default values via constructor parameters.
    """

    def __init__(self, environment: str = None,package: str = None, configs: Optional[Dict[str, Dict[str, str]]] = None):
        """
        Initializes the AstrafyTrainingEnvironment with the given environment and optional overrides for project, dataset, and service account.
        If no environment is provided, it attempts to determine it from the OS environment variable 'ENVIRONMENT'.

        Args:
            environment (str, optional): The environment (e.g., 'dev', 'prd'). Defaults to None.
            configs (Dict[str, Dict[str, str]], optional): A dictionary containing environment-specific configurations. Defaults to None.
        """
        self.environment = environment or os.getenv('ENVIRONMENT')
        self.package = package
        env_vars = [
            self.set_env_vars(name="STG_PROJECT_ID", key="STG_PROJECT_ID"),
            self.set_env_vars(name="LZ_PROJECT_ID", key="LZ_PROJECT_ID"),
            self.set_env_vars(name="DM_PROJECT_ID", key="DM_PROJECT_ID"),
            self.set_env_vars(name="DW_PROJECT_ID", key="DW_PROJECT_ID"),
            self.set_env_vars(name="PACKAGE", value=self.package),
            self.set_env_vars(name="ENV", value=self.environment),
        ]
        
        self.env_vars = env_vars

        if not self.environment:
            raise ValueError("Environment not specified. Please provide an environment or set the 'ENVIRONMENT' environment variable.")

        self.config = self._load_config(configs)


    def _load_config(self, configs: Optional[Dict[str, Dict[str, str]]] = None) -> Dict:
        """
        Loads the configuration based on the environment, using provided configs if available.

        Returns:
            Dict: A dictionary containing the configuration for the specified environment.

        Raises:
            ValueError: If the environment is not supported.
        """
        # Define default configurations for different environments
        default_config = {
            "dev": {
                "project": "dev-project-id",
                "dataset": "dev_dataset",
                "service_account": "dev-service-account@dev-project-id.iam.gserviceaccount.com"
            },
            "prd": {
                "project": "prd-project-id",
                "dataset": "prd_dataset",
                "service_account": "prd-service-account@prd-project-id.iam.gserviceaccount.com"
            }
        }

        if configs and self.environment in configs:
            # Merge the provided configs with the default configs
            config = default_config.get(self.environment, {}).copy()  # Start with a copy of the default config
            config.update(configs[self.environment])  # Update with values from configs
        else:
            config = default_config.get(self.environment, {})

        if not config:
            raise ValueError(f"Unsupported environment: {self.environment}. Supported environments are: {', '.join(default_config.keys())}")

        return config
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
    def get_project(self) -> str:
        """
        Returns the project ID for the current environment.

        Returns:
            str: The project ID.
        """
        return self.config["project"]

    def get_dataset(self) -> str:
        """
        Returns the dataset ID for the current environment.

        Returns:
            str: The dataset ID.
        """
        return self.config["dataset"]

    def get_service_account(self) -> str:
        """
        Returns the service account for the current environment.

        Returns:
            str: The service account for the current environment.
        """
        return self.config["service_account"]

