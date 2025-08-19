import requests
import time
import json
from airflow.hooks.base import BaseHook
from airflow.exceptions import AirflowException
from airflow_providers_onehouse.utils.enums import *


class OnehouseHook(BaseHook):
    """
    Hook to interact with Onehouse SQL API.
    """

    def __init__(self, conn_id: str = "onehouse_default") -> None:
        super().__init__()
        self.conn_id = conn_id
        (
            self.base_url,
            self.project_uid,
            self.user_id,
            self.api_key,
            self.api_secret,
            self.link_uid,
            self.region,
        ) = self._get_conn()

    def _get_conn(self):
        connection = self.get_connection(self.conn_id)
        base_url = connection.host
        if not base_url:
            raise AirflowException("Host is required for Onehouse connection")
        extras = connection.extra_dejson

        try:
            project_uid = extras["project_uid"]
            user_id = extras["user_id"]
            api_key = extras["api_key"]
            api_secret = extras["api_secret"]
            link_uid = extras["link_uid"]
            region = extras["region"]
        except KeyError as e:
            raise AirflowException(f"Missing required Onehouse connection parameter: {e}")

        return base_url, project_uid, user_id, api_key, api_secret, link_uid, region

    def _get_headers(self) -> dict:
        """
        Constructs the headers required for Onehouse API requests.
        """
        return {
            "x-onehouse-project-uid": self.project_uid,
            "x-onehouse-uuid": self.user_id,
            "x-onehouse-api-key": self.api_key,
            "x-onehouse-api-secret": self.api_secret,
            "x-onehouse-link-uid": self.link_uid,
            "x-onehouse-region": self.region,
            "Content-Type": "application/json",
        }

    # TO-DO: Add sync version of submit_sql, get_status, wait_for_status methods
    def submit_sql(self, sql: str) -> str:
        """
        Submits a SQL command to Onehouse SQL API using required headers.
        Logs request ID and gRPC error message if available.
        """
        url = f"{self.base_url}/v1/resource/"

        headers = self._get_headers()

        payload = {"statement": sql}

        response = requests.post(url, headers=headers, json=payload)
        grpc_message = response.headers.get("grpc-message")

        if response.status_code != 200:
            error_message = (
                f"Failed to submit SQL to Onehouse. "
                f"Status Code: {response.status_code}. "
                f"gRPC Message: {grpc_message}. "
                f"Response Body: {response.text}"
            )
            raise AirflowException(error_message)

        try:
            response_json = response.json()
            request_id = response_json["requestId"]
        except (json.JSONDecodeError, KeyError) as e:
            error_message = (
                f"Invalid response from Onehouse API. "
                f"Status Code: {response.status_code}. "
                f"gRPC Message: {grpc_message}. "
                f"Response Body: {response.text}. "
                f"Error: {str(e)}"
            )
            raise AirflowException(error_message)

        # Log success path as well
        self.log.info(
            "Successfully submitted SQL. Request ID: %s, gRPC Message: %s",
            request_id,
            grpc_message,
        )

        return request_id

    def get_status(self, request_id: str) -> dict:
        """
        Retrieves the status and response of a submitted SQL command using the request ID.
        Logs gRPC error message if available.
        """

        url = f"{self.base_url}/v1/status/{request_id}"

        headers = self._get_headers()

        response = requests.get(url, headers=headers)

        grpc_message = response.headers.get("grpc-message")

        if response.status_code != 200:
            error_message = (
                f"Failed to retrieve status from Onehouse. "
                f"Status Code: {response.status_code}. "
                f"gRPC Message: {grpc_message}. "
                f"Response Body: {response.json()}"
            )
            raise AirflowException(error_message)

        return response.json()

    def wait_for_status(self, request_id: str, poll_interval: int = 10, timeout: int = 300) -> dict:
        """
        Polls the Onehouse status endpoint until a terminal state is reached or timeout occurs.

        :param request_id: The request ID to poll status for
        :param poll_interval: Poll frequency in seconds (default: 10s)
        :param timeout: Max wait time in seconds (default: 300s / 5 min)
        :return: The final response JSON
        :raises AirflowException: if failed
        """
        start_time = time.time()

        while True:
            result = self.get_status(request_id)
            api_status = result.get("apiStatus")
            api_response = result.get("apiResponse")

            self.log.info("Polling status for request_id=%s → response=%s", request_id, api_response)

            if ApiOperationStatus.is_terminal(api_status):
                if api_status == ApiOperationStatus.SUCCESS:
                    self.log.info("Request %s completed successfully.", request_id)
                    return result
                else:
                    raise AirflowException(f"Request {request_id} ended with terminal state: {api_status}")

            if time.time() - start_time > timeout:
                raise AirflowException(f"Timeout while waiting for status of request {request_id}")

            time.sleep(poll_interval)
