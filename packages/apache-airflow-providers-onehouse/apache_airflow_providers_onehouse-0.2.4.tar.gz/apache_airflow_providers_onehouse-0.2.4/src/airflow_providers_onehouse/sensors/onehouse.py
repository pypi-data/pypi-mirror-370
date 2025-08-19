from airflow.exceptions import AirflowException
from airflow_providers_onehouse.sensors.base_onehouse import BaseOnehouseSensor
from airflow_providers_onehouse.utils.onehouse import _extract_job_run_details, _extract_cluster_creation_status, _extract_job_details
from airflow_providers_onehouse.utils.enums import SparkJobRunStatus, ApiOperationStatus


class OnehouseJobRunSensor(BaseOnehouseSensor):
    """
    Sensor to monitor a Onehouse Spark job run until it completes.
    """

    template_fields = ("job_name", "job_run_id")

    def __init__(
            self,
            job_name: str,
            job_run_id: str,
            conn_id: str = "onehouse_default",
            *args,
            **kwargs,
    ):
        super().__init__(conn_id=conn_id, *args, **kwargs)
        self.job_name = job_name
        self.job_run_id = job_run_id

    def poke(self, context):
        sql = f"DESCRIBE JOB_RUN `{self.job_run_id}` JOB_NAME = '{self.job_name}'"
        self.log.info("Polling Onehouse job run: %s", sql)
        request_id = self.hook.submit_sql(sql)
        self.log.info("Polling Onehouse job run, request_id='%s'", request_id)
        result = self.hook.wait_for_status(request_id)

        job_run_details = _extract_job_run_details(self.job_run_id, result)
        raw_status = job_run_details["status"]
        status = raw_status.value if isinstance(raw_status, SparkJobRunStatus) else str(raw_status).strip().upper()
        job_run_response = job_run_details["job_run_response"]

        self.log.info(f"Normalized job run status: %s", status)
        self.log.debug("Full job run response: %s", job_run_response)

        if status == SparkJobRunStatus.COMPLETED.value:
            return True
        elif SparkJobRunStatus.is_active(status):
            return False
        elif SparkJobRunStatus.is_failure(status):
            raise AirflowException(f"Job run ended with failure state: {status} and response: {job_run_response}")
        elif status == SparkJobRunStatus.NOT_RUN.value:
            self.log.warning("Job run status 'NOT_RUN'; retrying.")
            return False
        else:
            raise AirflowException(f"Unexpected job status: {status} and response: {job_run_response}")


class OnehouseCreateClusterSensor(BaseOnehouseSensor):
    """
    Sensor to monitor the creation of a Onehouse cluster.
    """

    template_fields = ("cluster_name",)

    def __init__(
            self,
            cluster_name: str,
            conn_id: str = "onehouse_default",
            *args,
            **kwargs,
    ):
        super().__init__(conn_id=conn_id, *args, **kwargs)
        self.cluster_name = cluster_name

    def poke(self, context):
        sql = f"DESCRIBE CLUSTER {self.cluster_name}"
        self.log.info("Polling Onehouse cluster: %s", sql)
        request_id = self.hook.submit_sql(sql)
        self.log.info("Polling Onehouse cluster, request_id='%s'", request_id)
        result = self.hook.wait_for_status(request_id)

        cluster_creation_details = _extract_cluster_creation_status(self.cluster_name, result)
        raw_status = cluster_creation_details["status"]
        status = raw_status.value if isinstance(raw_status, ApiOperationStatus) else str(raw_status).strip().upper()
        cluster_creation_response = cluster_creation_details["cluster_response"]

        self.log.info(f"Normalized cluster creation status: %s", status)
        self.log.debug("Full cluster creation response: %s", cluster_creation_response)

        if status == ApiOperationStatus.SUCCESS.value:
            return True
        elif status == ApiOperationStatus.PENDING.value:
            return False
        elif ApiOperationStatus.is_failure(status):
            raise AirflowException(f"Cluster creation ended with failure state: {status} and response: {cluster_creation_response}")
        else:
            raise AirflowException(f"Unexpected cluster creation status: {status} and response: {cluster_creation_response}")


class OnehouseDescribeJobSensor(BaseOnehouseSensor):
    """
    Sensor to monitor the description of a Onehouse job.
    """

    template_fields = ("job_name",)

    def __init__(self, job_name: str, conn_id: str = "onehouse_default", *args, **kwargs):
        super().__init__(conn_id=conn_id, *args, **kwargs)
        self.job_name = job_name

    def poke(self, context):
        sql = f"DESCRIBE JOB {self.job_name}"
        self.log.info("Polling Onehouse job: %s", sql)
        request_id = self.hook.submit_sql(sql)
        self.log.info("Polling Onehouse job, request_id='%s'", request_id)
        result = self.hook.wait_for_status(request_id)

        job_details = _extract_job_details(self.job_name, result)
        raw_status = job_details["status"]
        status = raw_status.value if isinstance(raw_status, ApiOperationStatus) else str(raw_status).strip().upper()
        job_response = job_details["job_response"]

        self.log.info(f"Normalized job status: %s", status)
        self.log.debug("Full job response: %s", job_response)

        if status == ApiOperationStatus.SUCCESS.value:
            return True
        elif status == ApiOperationStatus.PENDING.value:
            return False
        elif ApiOperationStatus.is_failure(status):
            raise AirflowException(f"Job description ended with failure state: {status} and response: {job_response}")
        else:
            raise AirflowException(f"Unexpected job description status: {status} and response: {job_response}")
