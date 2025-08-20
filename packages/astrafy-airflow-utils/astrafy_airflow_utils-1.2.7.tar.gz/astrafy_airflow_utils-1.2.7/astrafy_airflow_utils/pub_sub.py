from airflow.sdk import DAG, BaseOperator
from airflow.providers.google.cloud.operators.pubsub import PubSubPublishMessageOperator
from airflow.utils.trigger_rule import TriggerRule


def build_pubsub_message(message_dict) -> dict:

    return {
        'data': bytes(str(message_dict), encoding='utf-8')
    }


def notification_job_for_table(
        task_id: str,
        message_dict,
        downstream_project,
        topic,
        impersonation_chain="",
        trigger_rule: TriggerRule = TriggerRule.ALL_SUCCESS,
        dag: DAG = None,) -> BaseOperator:
    """
        Creates an Airflow job to send a Pub/Sub notification message for the list of given tables
        or log a message based on the environment.

        Parameters
        ----------
        task_id
            The ID of the Airflow task
        task_group
            The group Task of Airflow to group the tasks
        table
            The modified table
        flow
            The flow concerned by the notification
        dataset
            The dataset concerned by the notification
        mode
            The mode for the job Can be 'incremental' or 'full'
        downstream_project
            The downstream project where topic is
        topic
            The topic name
        env
            The environment identifier 
        trigger_rule
            Trigger rule of the messaging system based on your logic
        dag
            The dag in which the operator must be instantiated
        
        
        

        Returns
        -------
        operator
            Returns an PubSubOperator that will publish the normalized message

        Raises
        ------
        ValueError
            If an unsupported mode is provided.

        """
    dag = dag

    job= PubSubPublishMessageOperator(
        dag=dag,
        task_id=task_id,
        trigger_rule=trigger_rule,
        project_id=downstream_project,
        topic=topic,
        impersonation_chain=impersonation_chain,
        messages=[build_pubsub_message(message_dict)])
    
    return job
