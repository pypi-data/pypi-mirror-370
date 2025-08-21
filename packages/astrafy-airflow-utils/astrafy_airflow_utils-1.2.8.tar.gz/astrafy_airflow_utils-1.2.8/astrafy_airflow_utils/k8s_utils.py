from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator

def node_affinity(node_pool_name: object = 'dbt') -> object:
    """
    Create the affinity parameter to execute the Pod in the given node_pool_name
    Most of the executions should be run in the default node pool ('dbt').
    If the execution needs more performances, please use 'performance'.
    @param node_pool_name: the name of the node pool to execute the pod.
    """
    return {
        'nodeAffinity': {
            'requiredDuringSchedulingIgnoredDuringExecution': {
                'nodeSelectorTerms': [
                    {
                        'matchExpressions': [
                            {
                                'key': 'node_pool',
                                'operator': 'In',
                                'values': [node_pool_name]
                            }
                        ]
                    }
                ]
            }
        }
    }
def gke_bash(dag, task_id, image, arguments, env_vars, trigger_rule,affinity,service_account,cmds = ["/bin/bash", "-c"]):
    """
    Creates a pod operator with the defaults values for the Data lake.
    @param dag: The DAG object to which the task belongs.
    @param task_id: The unique identifier for the task.
    @param image: The Docker image to be used for the pod.
    @param arguments: The command to be executed inside the pod.
    @param affinity: (optional) The node affinity settings for the pod. Defaults to node_affinity().
    @return: a KubernetesPodOperator with the default values

    """
    return KubernetesPodOperator(
        image_pull_policy="Always",
        image_pull_secrets="jfrog",
        is_delete_operator_pod=True,
        startup_timeout_seconds=600,
        cmds=cmds,
        namespace='dbt',
        get_logs=True,
        trigger_rule=trigger_rule,
        service_account_name=service_account,
        env_vars=env_vars,
        affinity=affinity,
        image=image,
        task_id=task_id,
        name=task_id,
        arguments=[arguments],
        dag=dag)