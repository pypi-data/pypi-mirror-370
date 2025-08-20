#TO BE REMOVED
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

def get_elementary_command(service_account, dataset, bucket, project, data_product):
    elementary_command = f"""
        mkdir -p ./profiles;
        echo \"\"\"
        elementary:
            outputs:
                default:
                    type: bigquery
                    project: {project}
                    dataset: {dataset}
                    job_execution_timeout_seconds: 300
                    job_retries: 1
                    location: EU
                    method: oauth
                    priority: interactive
                    threads: 1
                    impersonate_service_account: {service_account}
            target: default
        \"\"\" >> ./profiles/profiles.yml;
        edr send-report --gcs-bucket-name {bucket} --bucket-file-path {data_product}/elementary_report.html --profiles-dir ./profiles"""
    return elementary_command