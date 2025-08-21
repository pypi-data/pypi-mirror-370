from astrafy_environment import AstrafyEnvironment

def get_gcs_bucket_path(environment: AstrafyEnvironment) -> str:
    """
    Constructs the GCS bucket path using the environment configuration.
    
    @param environment: AstrafyEnvironment instance with the configuration
    @return: The constructed GCS bucket path
    """
    return f"gs://{environment.bucket_folder_results}"

def upload_to_gcs(environment: AstrafyEnvironment) -> str:
    """
    Generates command to upload dbt artifacts to GCS.
    
    @param environment: AstrafyEnvironment instance with the configuration
    @return: The bash command string
    """
    bucket_path = get_gcs_bucket_path(environment)
    return f"""
    gcloud storage cp /app/target/*.json {bucket_path}/
    """

def download_failed_models(environment: AstrafyEnvironment) -> str:
    """
    Generates command to download previous dbt artifacts from GCS.
    
    @param environment: AstrafyEnvironment instance with the configuration
    @return: The bash command string
    """
    bucket_path = get_gcs_bucket_path(environment)
    return f"""
    mkdir -p /app/target
    gcloud storage cp -r {bucket_path}/* /app/target/
    """