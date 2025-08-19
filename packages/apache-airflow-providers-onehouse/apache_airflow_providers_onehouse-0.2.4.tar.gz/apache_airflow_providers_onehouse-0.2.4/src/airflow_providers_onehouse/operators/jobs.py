from typing import List

from airflow_providers_onehouse.operators.base_onehouse import BaseOnehouseOperator
from airflow_providers_onehouse.utils.onehouse import _extract_job_run_id


class OnehouseCreateJobOperator(BaseOnehouseOperator):
    """
    Operator to create a Spark Job in Onehouse.

    :param job_name: Name of the job to create.
    :param job_type: Type of job: 'PYTHON' or 'JAR'.
    :param parameters: List of parameters for the job.
    :param cluster: Name of the cluster to run the job on.
    :param conn_id: Airflow connection ID for Onehouse.
    :return : The job name of the created job.
    """

    # for Jinja template to render the job name at runtime
    template_fields = ("cluster_name",)

    def __init__(self, job_name: str, job_type: str, parameters: List[str], cluster_name: str, conn_id: str = "onehouse_default", *args, **kwargs):
        super().__init__(conn_id=conn_id, *args, **kwargs)
        self.job_name = job_name
        self.job_type = job_type
        self.parameters = parameters
        self.cluster_name = cluster_name

    def execute(self, context):
        sql = self._build_create_job_sql()
        self.log.info("Creating Onehouse job '%s' with SQL: %s", self.job_name, sql)
        request_id = self.hook.submit_sql(sql)
        self.log.info("Created Onehouse job '%s', request_id='%s'", self.job_name, request_id)
        self.hook.wait_for_status(request_id)
        return self.job_name

    def _build_create_job_sql(self) -> str:
        param_list = ', '.join(f"'{param}'" for param in self.parameters)
        return (
            f"CREATE JOB {self.job_name} "
            f"TYPE = '{self.job_type}' "
            f"PARAMETERS = ({param_list}) "
            f"CLUSTER = '{self.cluster_name}'"
        )


class OnehouseRunJobOperator(BaseOnehouseOperator):
    """
    Operator to run a Spark Job in Onehouse.

    :param job_name: Name of the job to run.
    :param conn_id: Airflow connection ID for Onehouse.
    :return: The job run ID of the started job.
    """

    # for Jinja template to render the job name at runtime
    template_fields = ("job_name",)

    def __init__(
            self,
            job_name: str,
            conn_id: str = "onehouse_default",
            *args,
            **kwargs,
    ) -> None:
        super().__init__(conn_id=conn_id, *args, **kwargs)
        self.job_name = job_name

    def execute(self, context):
        sql = self._build_run_job_sql()
        self.log.info("Running Onehouse job '%s' with SQL: %s", self.job_name, sql)
        request_id = self.hook.submit_sql(sql)
        self.log.info("Successfully started Onehouse job '%s', request_id='%s'", self.job_name, request_id)
        result = self.hook.wait_for_status(request_id)
        job_run_id = _extract_job_run_id(result)
        self.log.info("Job run ID: %s", job_run_id)
        return job_run_id

    def _build_run_job_sql(self) -> str:
        return f"RUN JOB {self.job_name}"


class OnehouseDeleteJobOperator(BaseOnehouseOperator):
    """
    Operator to delete a Spark Job in Onehouse.

    :param job_name: Name of the job to delete.
    :param conn_id: Airflow connection ID for Onehouse.
    :return: The job name of the deleted job.
    """

    # for Jinja template to render the job name at runtime
    template_fields = ("job_name",)

    def __init__(
            self,
            job_name: str,
            conn_id: str = "onehouse_default",
            *args,
            **kwargs,
    ) -> None:
        super().__init__(conn_id=conn_id, *args, **kwargs)
        self.job_name = job_name

    def execute(self, context):
        sql = self._build_delete_job_sql()
        self.log.info("Deleting Onehouse job '%s' with SQL: %s", self.job_name, sql)
        request_id = self.hook.submit_sql(sql)
        self.log.info("Successfully deleted Onehouse job '%s', request_id='%s'", self.job_name, request_id)
        self.hook.wait_for_status(request_id)
        return self.job_name

    def _build_delete_job_sql(self) -> str:
        return f"DELETE JOB {self.job_name}"


class OnehouseAlterJobOperator(BaseOnehouseOperator):
    """
    Operator to alter a Spark Job in Onehouse.

    :param job_name: Name of the job to alter.
    :param conn_id: Airflow connection ID for Onehouse.
    :return: The job name of the altered job.
    """

    template_fields = ("job_name", "cluster_name", "parameters")

    def __init__(self, job_name: str, cluster_name: str | None = None, parameters: List[str] | None = None, conn_id: str = "onehouse_default", *args, **kwargs):
        super().__init__(conn_id=conn_id, *args, **kwargs)
        self.job_name = job_name
        self.cluster_name = cluster_name
        self.parameters = parameters

    def execute(self, context):
        sql = self._build_alter_job_sql()
        self.log.info("Altering Onehouse job '%s' with SQL: %s", self.job_name, sql)
        request_id = self.hook.submit_sql(sql)
        self.log.info("Successfully altered Onehouse job '%s', request_id='%s'", self.job_name, request_id)
        self.hook.wait_for_status(request_id)
        return self.job_name
    
    def _build_alter_job_sql(self) -> str:
        parts = [f"ALTER JOB {self.job_name}"]
        clauses = []
        
        if self.cluster_name:
            clauses.append(f"SET CLUSTER = '{self.cluster_name}'")
        if self.parameters:
            param_list = ', '.join(f"'{param}'" for param in self.parameters)
            clauses.append(f"SET PARAMETERS = ({param_list})")
        
        return " ".join(parts + clauses)


class OnehouseCancelJobRunOperator(BaseOnehouseOperator):
    """
    Operator to cancel an in-progress Job run in Onehouse.

    :param job_run_id: ID of the Job run to cancel (should be surrounded by backticks).
    :param job_name: Name of the Job that is running.
    :param conn_id: Airflow connection ID for Onehouse.
    :return: The job run ID of the cancelled job.
    """

    # for Jinja template to render the job run ID and job name at runtime
    template_fields = ("job_run_id", "job_name")

    def __init__(
            self,
            job_run_id: str,
            job_name: str,
            conn_id: str = "onehouse_default",
            *args,
            **kwargs,
    ) -> None:
        super().__init__(conn_id=conn_id, *args, **kwargs)
        self.job_run_id = job_run_id
        self.job_name = job_name

    def execute(self, context):
        sql = self._build_cancel_job_run_sql()
        self.log.info("Cancelling Onehouse job run '%s' for job '%s' with SQL: %s", 
                      self.job_run_id, self.job_name, sql)
        request_id = self.hook.submit_sql(sql)
        self.log.info("Successfully cancelled Onehouse job run '%s', request_id='%s'", 
                      self.job_run_id, request_id)
        self.hook.wait_for_status(request_id)
        return self.job_run_id

    def _build_cancel_job_run_sql(self) -> str:
        return f"CANCEL JOB_RUN `{self.job_run_id}` JOB_NAME = '{self.job_name}'"
