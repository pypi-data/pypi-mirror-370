from airflow.sensors.base import BaseSensorOperator
from airflow_providers_onehouse.hooks.onehouse import OnehouseHook


class BaseOnehouseSensor(BaseSensorOperator):
    """
    Abstract base class for Onehouse sensors.
    Handles hook creation and common config.
    """

    def __init__(self, conn_id: str = "onehouse_default", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conn_id = conn_id
        self.hook = OnehouseHook(conn_id=self.conn_id)
