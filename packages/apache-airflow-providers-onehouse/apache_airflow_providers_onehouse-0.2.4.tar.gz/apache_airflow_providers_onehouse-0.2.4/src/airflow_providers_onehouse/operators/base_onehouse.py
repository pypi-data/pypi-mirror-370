from airflow.models import BaseOperator
from airflow_providers_onehouse.hooks.onehouse import OnehouseHook


class BaseOnehouseOperator(BaseOperator):
    """
    Abstract base class for Onehouse operators.
    Handles hook creation and common config.
    """

    def __init__(self, conn_id: str = "onehouse_default", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conn_id = conn_id
        self.hook = OnehouseHook(conn_id=self.conn_id)
