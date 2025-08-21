from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from airflow.configuration import conf


SLACK_CONN_ID = "slack_airflow"

DAG_OWNER_MAPPING = {
    "management": "U02TS6TVBP1", #Charles
    "finops": "U06CCADAA21", #Victor
    "billing": "U06CCADAA21", #Victor
    "monitoring": "U08RTHGR2N5", #Lucas
    "chatops": "U04PS4C43EC", #Nawfel
    "gitops": "U08RTHETYQZ", #Marcelo
    "google_ads": "U06U5P7SV7G", #Greta
    "sales_marketing": "U08B0Q00T9U", #Cris
    "web_analytics": "U085HU06BQ9", #Virginia
    "seo": "U085HU06BQ9", #Virginia
    "docs_pm": "U08C1H0EPED", #Elvira
    "security": "U08C4QC2DL0", #Rubén
}

def task_fail_slack_alert(context):
    webserver_url = conf.get('webserver', 'base_url')
    dag_id = context.get("task_instance").dag_id
    task_id = context.get("task_instance").task_id
    run_id = context.get("task_instance").run_id
    dag_url = f"{webserver_url}/dags/{dag_id}/runs/{run_id}"

    owner_tag = ""
    for prefix, user_id in DAG_OWNER_MAPPING.items():
        if dag_id.startswith(prefix):
            owner_tag = f"<@{user_id}>"
            break

    slack_msg = """
:red_circle: Task Failed.
*Task*: {task}  
*Dag*: {dag} 
*Dag URL*: <{url}|View in Airflow>
*Owner*: {owner}
""".format(
        task=task_id,
        dag=dag_id,
        url=dag_url,
        owner=owner_tag
    )
    failed_alert = SlackWebhookOperator(
        task_id="slack_fail_alert", 
        slack_webhook_conn_id=SLACK_CONN_ID,
        message=slack_msg,
    )
    return failed_alert.execute(context=context)
