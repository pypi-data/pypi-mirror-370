def _extract_job_run_id(response: dict) -> str:
    """
    Extracts the job run ID from the response.
    :param response: The response from the Onehouse API.
    :return: The job run ID.
    """
    return response["apiResponse"]["runJobApiResponse"]["jobRunId"]


def _extract_job_run_details(job_run_id: str, response: dict) -> dict:
    try:
        job_run_response = response["apiResponse"]["describeJobRunApiResponse"]
        status = job_run_response["sparkJobRun"]["status"]
        return {"status": status, "job_run_response": job_run_response}
    except KeyError as e:
        raise ValueError(
            f"Failed to extract job run status for job_run_id={job_run_id}."
            f" Response: {response}. Error: {e}"
        )


def _extract_cluster_creation_status(cluster_name: str, response: dict) -> dict:
    try:
        cluster_response = response["apiResponse"]
        status = response["apiStatus"]
        return {"status": status, "cluster_response": cluster_response}
    except KeyError as e:
        raise ValueError(
            f"Failed to extract cluster creation status for cluster_name={cluster_name}."
            f" Response: {response}. Error: {e}"
        )


def _extract_job_details(job_name: str, response: dict) -> dict:
    try:
        job_response = response["apiResponse"]["describeJobApiResponse"]
        status = response["apiStatus"]
        return {"status": status, "job_response": job_response}
    except KeyError as e:
        raise ValueError(
            f"Failed to extract job status for job_name={job_name}."
            f" Response: {response}. Error: {e}"
        )
