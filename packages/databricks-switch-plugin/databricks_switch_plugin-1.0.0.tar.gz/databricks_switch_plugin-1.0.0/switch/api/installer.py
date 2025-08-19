"""Switch installer for Databricks workspace deployment"""
import logging
import os
from dataclasses import dataclass
from typing import Optional

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import Task, NotebookTask, Source
from databricks.sdk.service.workspace import ImportFormat

from switch.api.job_parameters import SwitchJobParameters

logger = logging.getLogger(__name__)


@dataclass
class InstallResult:
    """Result of installation"""
    job_id: int
    job_name: str
    job_url: str
    switch_home: str
    created_by: str


@dataclass
class UninstallResult:
    """Result of uninstallation"""
    success: bool
    message: str = ""


class SwitchInstaller:
    """Switch installer for Databricks

    Simple API with only two public methods:
    - install(): Install Switch (optionally removes previous installation)
    - uninstall(): Remove Switch installation
    """
    # Directory and path constants
    _WORKSPACE_BASE_DIR_NAME = ".lakebridge-switch"
    _MAIN_NOTEBOOK_PATH = "switch/notebooks/00_main"

    # Job configuration constants
    JOB_NAME = "lakebridge-switch"
    JOB_TAG_CREATED_BY = "created_by"
    _JOB_MAX_CONCURRENT_RUNS = 1000

    # Main task configuration constants
    _MAIN_TASK_KEY = "00_main"
    _MAIN_TASK_MAX_RETRIES = 0

    def __init__(self, workspace_client: WorkspaceClient):
        """Initialize with workspace client

        Args:
            workspace_client: Databricks workspace client instance
        """
        self.workspace_client = workspace_client

    def install(self,
                default_parameters: Optional[SwitchJobParameters] = None,
                previous_job_id: Optional[int] = None,
                previous_switch_home: Optional[str] = None) -> InstallResult:
        """Install Switch for current user. Optionally cleans up previous installation.

        Args:
            default_parameters: Optional default parameters for the job template
            previous_job_id: Previous job ID to clean up before installation
            previous_switch_home: Previous switch home to clean up before installation

        Returns:
            InstallResult with job information

        Raises:
            Exception: If installation fails
        """
        # Clean up previous installation if specified
        if previous_job_id or previous_switch_home:
            logger.info(f"Cleaning up previous installation: job_id={previous_job_id}, switch_home={previous_switch_home}")

            uninstall_result = self.uninstall(
                job_id=previous_job_id,
                switch_home=previous_switch_home
            )

            if uninstall_result.success:
                logger.info("Successfully cleaned up previous installation")
            else:
                logger.warning(f"Partial cleanup: {uninstall_result.message}")

        # Start fresh installation
        logger.info("Starting installation")

        # Deploy Switch package
        notebook_path = self._deploy_switch_package()

        # Create job with default parameters
        job_id = self._create_job(notebook_path, default_parameters)
        switch_home = self._get_switch_home()
        job_url = self._get_job_url(job_id)
        created_by = self._get_current_user()

        logger.info(f"Successfully installed Switch: job_id={job_id}, job_name={self.JOB_NAME}")

        return InstallResult(
            job_id=job_id,
            job_name=self.JOB_NAME,
            job_url=job_url,
            switch_home=switch_home,
            created_by=created_by
        )

    def uninstall(self,
                  job_id: Optional[int] = None,
                  switch_home: Optional[str] = None) -> UninstallResult:
        """Uninstall Switch

        Args:
            job_id: Job ID to delete (if provided)
            switch_home: Switch home to delete. If None, uses current user's default location.

        Returns:
            UninstallResult indicating success or failure
        """
        errors = []

        # Delete job if specified
        if job_id:
            if self._delete_job(job_id):
                logger.info(f"Successfully deleted job {job_id}")
            else:
                errors.append(f"Failed to delete job {job_id}")
                logger.error(f"Failed to delete job {job_id}")

        # If switch_home is not provided, use current user's default location
        if not switch_home:
            switch_home = self._get_switch_home()

        # Delete Switch home directory
        if self._delete_switch_home(switch_home):
            logger.info(f"Successfully deleted Switch home {switch_home}")
        else:
            errors.append(f"Failed to delete Switch home {switch_home}")
            logger.warning(f"Could not delete Switch home {switch_home}")

        # Determine overall success based on errors
        success = not errors
        if success:
            message = "Successfully uninstalled Switch"
            if job_id:
                message += f" (job_id={job_id}, switch_home={switch_home})"
        else:
            message = f"Failed to uninstall Switch: {'; '.join(errors)}"

        return UninstallResult(
            success=success,
            message=message
        )

    def _deploy_switch_package(self) -> str:
        """Deploy Switch package to workspace for both PyPI and development installations.

        Uploads all Switch files required for 'pip install -e ../..' to work in notebooks.
        Project root files (pyproject.toml, README.md, LICENSE, NOTICE) are all referenced
        by pyproject.toml and must be present together.

        Handles two different installation scenarios:
        - PyPI installation: Files are located in site-packages root (non-standard location
          due to custom build configuration that includes project files in wheel)
        - Development installation: Files are in the normal project root directory

        Recursively uploads Switch package files while preserving directory structure
        and skipping unwanted files (.pyc, .pyo, hidden files).

        Returns:
            str: Path to the main notebook for job creation
        """
        switch_home = self._get_switch_home()

        # Clean and recreate switch home directory
        if self._exists(switch_home):
            logger.warning(f"Switch home directory {switch_home} already exists. Removing it.")
            self.workspace_client.workspace.delete(switch_home, recursive=True)
        self.workspace_client.workspace.mkdirs(switch_home)

        # Setup directory paths
        switch_package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        switch_project_dir = os.path.dirname(switch_package_dir)  # Parent of switch package

        # Get site-packages directory for PyPI installations
        import switch
        site_packages_dir = os.path.dirname(os.path.dirname(switch.__file__))

        # Define search locations: PyPI install location first, then development location
        search_locations = [site_packages_dir, switch_project_dir]
        # Upload project root files (pyproject.toml, README.md, LICENSE, NOTICE)
        project_files = ["pyproject.toml", "README.md", "LICENSE", "NOTICE"]
        for filename in project_files:
            dest_path = f"{switch_home}/{filename}"
            if not self._upload_file_from_locations(filename, search_locations, dest_path):
                if filename == "pyproject.toml":
                    logger.warning(f"{filename} not found in any expected location")

        # Upload all files from switch package directory recursively
        for root, _, files in os.walk(switch_package_dir):
            for file_name in files:
                # Skip unwanted files
                if (file_name.startswith('.') or 
                    file_name.endswith(('.pyc', '.pyo')) or
                    file_name == '__pycache__'):
                    continue

                local_path = os.path.join(root, file_name)
                # Keep the directory structure: switch/api/, switch/notebooks/, etc.
                rel_path = os.path.relpath(local_path, os.path.dirname(switch_package_dir))
                remote_path = f"{switch_home}/{rel_path}"

                # Create parent directory if needed
                parent_dir = os.path.dirname(remote_path)
                if parent_dir != switch_home:
                    self.workspace_client.workspace.mkdirs(parent_dir)

                # Upload file
                with open(local_path, 'rb') as f:
                    content = f.read()
                self.workspace_client.workspace.upload(
                    path=remote_path,
                    content=content,
                    format=ImportFormat.AUTO,
                    overwrite=True
                )
                logger.debug(f"Uploaded {rel_path}")

        logger.info(f"Uploaded Switch package to {switch_home}")
        return self._get_notebook_path()

    def _create_job(self, notebook_path: str, default_parameters: Optional[SwitchJobParameters] = None) -> int:
        """Create Databricks job with Switch notebook and parameter template.

        Creates a job template with all Switch parameters, using provided defaults
        where available and empty strings for required user-provided parameters.

        Args:
            notebook_path: Path to the main Switch notebook in workspace
            default_parameters: Optional default parameter values for the job template

        Returns:
            int: Created job ID

        Raises:
            ValueError: If job creation fails or job_id is None
        """
        # Use provided parameters or create empty defaults
        if default_parameters is None:
            default_parameters = SwitchJobParameters()

        # Create job template parameters using centralized method
        template_params = default_parameters.to_job_template()

        # Define the main task for the job
        task = Task(
            task_key=self._MAIN_TASK_KEY,
            max_retries=self._MAIN_TASK_MAX_RETRIES,
            notebook_task=NotebookTask(
                notebook_path=notebook_path,
                base_parameters=template_params,
                source=Source.WORKSPACE
            )
        )

        # Create the job with created_by tag
        current_user = self._get_current_user()
        tags = {self.JOB_TAG_CREATED_BY: current_user}

        response = self.workspace_client.jobs.create(
            name=self.JOB_NAME,
            tasks=[task],
            max_concurrent_runs=self._JOB_MAX_CONCURRENT_RUNS,
            tags=tags
        )
        if response.job_id is None:
            raise ValueError("Failed to create job: job_id is None")
        logger.info(f"Created job template {response.job_id}: {self.JOB_NAME}")

        return response.job_id

    def _delete_switch_home(self, switch_home: str) -> bool:
        """Delete Switch home directory from workspace"""
        try:
            if self._exists(switch_home):
                self.workspace_client.workspace.delete(switch_home, recursive=True)
                logger.info(f"Deleted Switch home directory: {switch_home}")
            else:
                logger.debug(f"Switch home directory not found: {switch_home}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete Switch home directory {switch_home}: {e}")
            return False

    def _delete_job(self, job_id: int) -> bool:
        """Delete Switch job"""
        try:
            self.workspace_client.jobs.delete(job_id)
            logger.info(f"Deleted job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete job {job_id}: {e}")
            return False

    def _upload_file_from_locations(self, filename: str, locations: list[str], dest_path: str) -> bool:
        """Upload a file from first available location"""
        for location in locations:
            file_path = os.path.join(location, filename)
            if os.path.exists(file_path):
                logger.debug(f"Found {filename} at {file_path}, uploading to {dest_path}")
                with open(file_path, 'rb') as f:
                    content = f.read()
                self.workspace_client.workspace.upload(
                    path=dest_path,
                    content=content,
                    format=ImportFormat.AUTO
                )
                return True

        logger.debug(f"{filename} not found in any of the provided locations")
        return False

    def _get_current_user(self) -> str:
        """Get current user name"""
        user_name = self.workspace_client.current_user.me().user_name
        if user_name is None:
            raise ValueError("Unable to retrieve current user name")
        return user_name

    def _get_switch_home(self) -> str:
        """Get the Switch home directory"""
        current_user = self._get_current_user()
        return f"/Workspace/Users/{current_user}/{self._WORKSPACE_BASE_DIR_NAME}"

    def _get_notebook_path(self) -> str:
        """Get the main notebook path"""
        switch_home = self._get_switch_home()
        return f"{switch_home}/{self._MAIN_NOTEBOOK_PATH}"

    def _get_job_url(self, job_id: int) -> str:
        """Get the Databricks job URL for a given job ID"""
        return f"{self.workspace_client.config.host}/jobs/{job_id}"

    def _exists(self, path: str) -> bool:
        """Check if a path exists in the workspace"""
        try:
            self.workspace_client.workspace.get_status(path)
            return True
        except Exception:
            return False
