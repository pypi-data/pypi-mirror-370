"""Switch job runner for SQL conversion operations"""
import logging

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import Run

from switch.api.job_parameters import SwitchJobParameters

logger = logging.getLogger(__name__)


class SwitchJobRunner:
    """Run Switch conversion using Databricks Jobs API"""

    def __init__(self, workspace_client: WorkspaceClient, job_id: int):
        """Initialize with workspace client and job ID

        Args:
            workspace_client: Databricks workspace client instance
            job_id: Databricks job ID (from installer)
        """
        self.workspace_client = workspace_client
        self.job_id = job_id

    def run_async(self, parameters: SwitchJobParameters) -> int:
        """Run batch SQL conversion asynchronously

        Args:
            parameters: Job parameters

        Returns:
            run_id: Job run ID for tracking the run

        Raises:
            ValueError: If parameters validation fails
            Exception: If job fails to start
        """
        job_params = self._prepare_job_params(parameters)

        # Run the job with parameters
        try:
            response = self.workspace_client.jobs.run_now(
                job_id=self.job_id,
                notebook_params=job_params
            )
            run_id = response.run_id
            logger.info(f"Started job run {run_id} for job {self.job_id}")
            return run_id
        except Exception as e:
            logger.error(f"Failed to start job {self.job_id}: {e}")
            raise

    def run_sync(self, parameters: SwitchJobParameters, timeout_seconds: int = 7200) -> Run:
        """Run batch SQL conversion synchronously and wait for completion

        Args:
            parameters: Job parameters
            timeout_seconds: Maximum time to wait for completion (default: 2 hours)

        Returns:
            Run: Completed run information with result

        Raises:
            ValueError: If parameters validation fails
            Exception: If job fails or encounters error
        """
        job_params = self._prepare_job_params(parameters)

        # Run the job synchronously and wait for completion
        try:
            from datetime import timedelta
            timeout_delta = timedelta(seconds=timeout_seconds)

            run = self.workspace_client.jobs.run_now_and_wait(
                job_id=self.job_id,
                notebook_params=job_params,
                timeout=timeout_delta
            )
            if run.state and run.state.life_cycle_state:
                logger.info(f"Job run {run.run_id} completed with state: {run.state.life_cycle_state}")
            else:
                logger.warning(f"Job run {run.run_id} completed but state information is unavailable")
            return run
        except Exception as e:
            logger.error(f"Failed to run job {self.job_id} synchronously: {e}")
            raise

    def _prepare_job_params(self, parameters: SwitchJobParameters) -> dict:
        """Validate parameters and convert to job format

        Args:
            parameters: Job parameters

        Returns:
            Dictionary of job parameters

        Raises:
            ValueError: If parameters validation fails
        """
        # Validate all required parameters
        parameters.validate(require_all=True)

        # Convert parameters to job format
        return parameters.to_job_params()
