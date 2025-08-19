from __future__ import annotations

from ..http import HttpExecutor
from ..models.cohort import JobStatus


class JobsService:
    """Service for monitoring background job execution status.

    Many WebAPI operations (like cohort generation) run as background jobs.
    This service provides utilities to check the status of these jobs using
    their execution IDs.
    """

    def __init__(self, http: HttpExecutor):
        self._http = http

    def status(self, execution_id: int) -> JobStatus:
        """Get the current status of a background job.

        Parameters
        ----------
        execution_id : int
            The execution ID returned when starting a background job
            (e.g., from cohort generation).

        Returns
        -------
        JobStatus
            Current job status with status string and execution ID.

        Examples
        --------
        >>> # Start a cohort generation
        >>> job = client.cohortdefinition_generate(cohort_id=123, source_key="SYNPUF1K")
        >>>
        >>> # Check job status
        >>> status = client.jobs.status(job.execution_id)
        >>> print(f"Job status: {status.status}")

        Notes
        -----
        Common job statuses:
        - "STARTED": Job has begun execution
        - "RUNNING": Job is currently executing
        - "COMPLETED": Job finished successfully
        - "FAILED": Job encountered an error
        - "STOPPED": Job was manually stopped
        """
        data = self._http.get(f"/job/{execution_id}")
        if isinstance(data, dict):
            return JobStatus(status=data.get("status", "UNKNOWN"), executionId=data.get("executionId"))
        return JobStatus(status="UNKNOWN")
