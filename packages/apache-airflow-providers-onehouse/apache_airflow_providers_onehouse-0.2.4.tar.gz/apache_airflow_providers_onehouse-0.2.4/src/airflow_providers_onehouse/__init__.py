from airflow_providers_onehouse.hooks.onehouse import OnehouseHook
from airflow_providers_onehouse.operators.jobs import (
    OnehouseCreateJobOperator,
    OnehouseRunJobOperator,
    OnehouseAlterJobOperator,
    OnehouseCancelJobRunOperator
)
from airflow_providers_onehouse.operators.clusters import (
    OnehouseCreateClusterOperator,
    OnehouseDeleteClusterOperator,
    OnehouseAlterClusterOperator
)
from airflow_providers_onehouse.sensors.onehouse import (
    OnehouseJobRunSensor,
    OnehouseCreateClusterSensor,
    OnehouseDescribeJobSensor
)

# Import version from clean version file (no dependencies)
from ._version import __version__

def get_provider_info():
    return {
        "package-name": "apache-airflow-providers-onehouse",
        "name": "Onehouse",
        "description": "A custom Airflow provider for Onehouse integration",
        "versions": [__version__],
        
        # List all hooks
        "hook-class-names": [
            "airflow_providers_onehouse.hooks.onehouse.OnehouseHook"
        ],
        
        # List all operators
        "operator-class-names": [
            "airflow_providers_onehouse.operators.jobs.OnehouseCreateJobOperator",
            "airflow_providers_onehouse.operators.jobs.OnehouseRunJobOperator",
            "airflow_providers_onehouse.operators.clusters.OnehouseCreateClusterOperator",
            "airflow_providers_onehouse.operators.clusters.OnehouseDeleteClusterOperator",
            "airflow_providers_onehouse.operators.jobs.OnehouseAlterJobOperator",
            "airflow_providers_onehouse.operators.jobs.OnehouseCancelJobRunOperator"
        ],
        
        # List all sensors
        "sensor-class-names": [
            "airflow_providers_onehouse.sensors.onehouse.OnehouseJobRunSensor",
            "airflow_providers_onehouse.sensors.onehouse.OnehouseCreateClusterSensor",
            "airflow_providers_onehouse.sensors.onehouse.OnehouseDescribeJobSensor"
        ],
    }

# Make classes available at package level
__all__ = [
    "OnehouseHook",
    "OnehouseCreateJobOperator",
    "OnehouseRunJobOperator",
    "OnehouseCreateClusterOperator",
    "OnehouseDeleteClusterOperator",
    "OnehouseAlterClusterOperator",
    "OnehouseAlterJobOperator",
    "OnehouseJobRunSensor",
    "OnehouseCreateClusterSensor",
    "OnehouseDescribeJobSensor",
    "OnehouseCancelJobRunOperator"
]
