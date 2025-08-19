from enum import Enum


class SparkJobRunStatus(str, Enum):
    COMPLETED = "SPARK_JOB_RUN_STATUS_COMPLETED"
    RUNNING = "SPARK_JOB_RUN_STATUS_RUNNING"
    QUEUED = "SPARK_JOB_RUN_STATUS_QUEUED"
    FAILED = "SPARK_JOB_RUN_STATUS_FAILED"
    CANCELED = "SPARK_JOB_RUN_STATUS_CANCELED"
    NOT_RUN = "SPARK_JOB_RUN_STATUS_NOT_RUN"
    INVALID = "SPARK_JOB_RUN_STATUS_INVALID"

    @classmethod
    def is_failure(cls, status: str) -> bool:
        return status in {cls.FAILED, cls.CANCELED, cls.INVALID}

    @classmethod
    def is_active(cls, status: str) -> bool:
        return status in {cls.RUNNING, cls.QUEUED}


class ApiOperationStatus(str, Enum):
    SUCCESS = "API_OPERATION_STATUS_SUCCESS"
    FAILED = "API_OPERATION_STATUS_FAILED"
    PENDING = "API_OPERATION_STATUS_PENDING"
    INVALID = "API_OPERATION_STATUS_INVALID"

    @classmethod
    def is_failure(cls, status: str) -> bool:
        return status in {cls.FAILED, cls.INVALID}

    @classmethod
    def is_terminal(cls, status: str) -> bool:
        return status in {cls.SUCCESS, cls.FAILED, cls.INVALID}
