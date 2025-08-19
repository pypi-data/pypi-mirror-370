"""E2E test utilities for Switch testing

This module contains utilities specifically designed for Switch E2E testing.
These are NOT intended for production use - they are internal E2E testing tools only.
"""
import logging
import random
import string
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Any

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.workspace import ImportFormat

from switch.api.installer import SwitchInstaller
from switch.notebooks.pyscripts.types.builtin_prompt import BuiltinPrompt

logger = logging.getLogger(__name__)


class SwitchSchemaManager:
    """Test-only schema manager for Switch testing

    WARNING: This class is for testing only. Do not use in production code.

    Provides schema lifecycle management:
    - Generate unique schema names to prevent conflicts
    - Create test schemas using SQL warehouse
    - Drop test schemas with CASCADE
    - Consistent collision prevention patterns
    """

    def __init__(self, workspace_client: WorkspaceClient, warehouse_id: str):
        """Initialize schema manager with workspace client and warehouse ID

        Args:
            workspace_client: Databricks workspace client instance
            warehouse_id: SQL warehouse ID for executing schema operations
        """
        self.workspace_client = workspace_client
        self.warehouse_id = warehouse_id

    def generate_unique_schema_name(self, prefix: str = "e2e_switch") -> str:
        """Generate unique schema name using timestamp + random suffix

        Uses the same collision prevention pattern as table naming in 
        analyze_input_files.py for consistency and proven reliability.

        Args:
            prefix: Schema name prefix

        Returns:
            str: Unique schema name in format: {prefix}_{timestamp}_{random}
        """
        time_part = datetime.now().strftime("%Y%m%d%H%M%S")
        random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        return f"{prefix}_{time_part}_{random_part}"

    def create_schema(self, catalog: str, schema_name: str) -> None:
        """Create schema using SQL warehouse

        Args:
            catalog: Catalog name
            schema_name: Schema name to create

        Raises:
            Exception: If schema creation fails
        """
        logger.info(f"Creating schema {catalog}.{schema_name} using SQL warehouse")

        sql = f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema_name}"

        try:
            self.workspace_client.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=sql
            )
            logger.info(f"✅ Successfully created schema {catalog}.{schema_name}")
        except Exception as e:
            logger.error(f"❌ Failed to create schema {catalog}.{schema_name}: {e}")
            raise

    def drop_schema(self, catalog: str, schema_name: str) -> None:
        """Drop schema using SQL warehouse

        Args:
            catalog: Catalog name
            schema_name: Schema name to drop

        Raises:
            Exception: If schema drop fails
        """
        logger.info(f"Dropping schema {catalog}.{schema_name} using SQL warehouse")

        sql = f"DROP SCHEMA IF EXISTS {catalog}.{schema_name} CASCADE"

        try:
            self.workspace_client.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=sql
            )
            logger.info(f"✅ Successfully dropped schema {catalog}.{schema_name}")
        except Exception as e:
            logger.error(f"❌ Failed to drop schema {catalog}.{schema_name}: {e}")
            raise


class SwitchCleanupManager:
    """Test-only cleanup manager for Switch resources

    WARNING: This class is for testing only. Do not use in production code.

    Provides centralized cleanup functionality for:
    - Switch Databricks jobs created during testing
    - Delta tables with Switch naming conventions
    - Workspace directories created during testing
    """

    def __init__(self, workspace_client: WorkspaceClient, warehouse_id: str):
        """Initialize cleanup manager

        Args:
            workspace_client: Databricks workspace client for cleanup operations
            warehouse_id: SQL warehouse ID for schema operations
        """
        self.workspace_client = workspace_client
        self.current_user = workspace_client.current_user.me().user_name
        self.schema_manager = SwitchSchemaManager(workspace_client, warehouse_id)

    def cleanup_switch_jobs(self) -> None:
        """Clean up all Switch jobs for current user

        This method scans all jobs in the workspace and deletes Switch jobs
        belonging to the current user. Useful for cleaning up orphaned jobs
        from previous test runs.

        Uses production constants from SwitchInstaller:
        - Job name: SwitchInstaller.JOB_NAME
        - Tag key: SwitchInstaller.JOB_TAG_CREATED_BY
        """
        self._log_cleanup_section("Starting comprehensive Switch job cleanup")

        try:
            switch_jobs = self._find_switch_jobs()
            if not switch_jobs:
                logger.info("No Switch jobs found to clean up")
                self._log_cleanup_section("Comprehensive cleanup completed (no jobs found)")
                return

            deleted_count = self._delete_switch_jobs(switch_jobs)
            self._log_cleanup_section(f"Comprehensive cleanup completed: {deleted_count}/{len(switch_jobs)} jobs deleted")

        except Exception as e:
            logger.error(f"Error during comprehensive Switch job cleanup: {e}")
            logger.error("=== Comprehensive cleanup failed ===", exc_info=True)

    def cleanup_switch_schemas(self, catalog: str, prefix: str = "e2e_switch") -> None:
        """Clean up Switch test schemas in specified catalog

        Removes schemas following Switch E2E naming convention:
        {catalog}.{prefix}_{timestamp}_{random}

        Args:
            catalog: Target catalog name
            prefix: Schema prefix (defaults to "e2e_switch")
        """
        self._log_cleanup_section(f"Starting Switch schema cleanup in {catalog}")
        logger.info(f"Looking for schemas with prefix: {prefix}_")

        try:
            # List schemas in the catalog
            schemas_to_delete = []
            try:
                schemas = self.workspace_client.schemas.list(catalog_name=catalog)
                for schema in schemas:
                    if schema.name.startswith(f"{prefix}_"):
                        schemas_to_delete.append(schema.name)
                        logger.info(f"Found Switch schema: {catalog}.{schema.name}")

            except Exception as e:
                logger.error(f"Error listing schemas in {catalog}: {e}")
                return

            if not schemas_to_delete:
                logger.info(f"No Switch schemas found with prefix '{prefix}_' in {catalog}")
                self._log_cleanup_section("Schema cleanup completed (no schemas found)")
                return

            # Delete each schema using schema manager
            deleted_count = 0
            for schema_name in schemas_to_delete:
                try:
                    logger.info(f"Dropping schema: {catalog}.{schema_name}")
                    self.schema_manager.drop_schema(catalog, schema_name)
                    logger.info(f"✓ Successfully dropped schema: {catalog}.{schema_name}")
                    deleted_count += 1

                except Exception as e:
                    logger.error(f"✗ Failed to drop schema {catalog}.{schema_name}: {e}")

            self._log_cleanup_section(f"Schema cleanup completed: {deleted_count}/{len(schemas_to_delete)} schemas dropped")

        except Exception as e:
            logger.error(f"Error during Switch schema cleanup: {e}")
            logger.error("=== Schema cleanup failed ===", exc_info=True)

    def cleanup_all_if_requested(self, catalog: Optional[str] = None, prefix: str = "e2e_switch") -> None:
        """Perform comprehensive cleanup

        Args:
            catalog: Optional catalog for schema cleanup
            prefix: Schema prefix for cleanup (default: "e2e_switch")
        """
        logger.info("Performing comprehensive cleanup")

        # Always cleanup jobs
        self.cleanup_switch_jobs()

        # Cleanup schemas if catalog provided
        if catalog:
            self.cleanup_switch_schemas(catalog, prefix)
        else:
            logger.info("No catalog provided - skipping schema cleanup")

        logger.info("=== Comprehensive cleanup completed ===")

    def _log_cleanup_section(self, message: str) -> None:
        """Log cleanup section header with consistent formatting"""
        logger.info(f"=== {message} ===")

    def _find_switch_jobs(self) -> List[Any]:
        """Find all Switch jobs for current user
        
        Returns:
            List of Switch jobs matching current user
        """
        # Use production constants from SwitchInstaller
        job_name = SwitchInstaller.JOB_NAME
        created_by_tag = SwitchInstaller.JOB_TAG_CREATED_BY

        logger.info(f"Current user: {self.current_user}")
        logger.info(f"Looking for Switch jobs with name: '{job_name}' and created_by tag: '{self.current_user}'")

        # Find all Switch jobs for current user
        logger.info("Fetching all jobs from workspace...")
        switch_jobs = []
        all_jobs = []

        try:
            job_count = 0
            for job in self.workspace_client.jobs.list():
                job_count += 1
                all_jobs.append(job)

                if job.settings and job.settings.name:
                    logger.debug(f"Job {job.job_id}: '{job.settings.name}' - checking name and tags")

                    # Check if job name matches Switch job name
                    if job.settings.name == job_name:
                        # Check if created_by tag matches current user
                        if (job.settings.tags and 
                            created_by_tag in job.settings.tags and 
                            job.settings.tags[created_by_tag] == self.current_user):
                            logger.info(f"MATCH: Job {job.job_id}: '{job.settings.name}' (created_by: {job.settings.tags[created_by_tag]})")
                            switch_jobs.append(job)
                        else:
                            created_by_value = job.settings.tags.get(created_by_tag, "<no tag>") if job.settings.tags else "<no tags>"
                            logger.debug(f"NO MATCH (owner): Job {job.job_id}: '{job.settings.name}' (created_by: {created_by_value})")
                    else:
                        logger.debug(f"NO MATCH (name): Job {job.job_id}: '{job.settings.name}'")
                else:
                    logger.debug(f"Job {job.job_id}: No name or settings")

            logger.info(f"Total jobs scanned: {job_count}")
            logger.info(f"All job names (first 10):")
            for i, job in enumerate(all_jobs[:10]):
                name = job.settings.name if (job.settings and job.settings.name) else "<no name>"
                logger.info(f"  {i+1}. Job {job.job_id}: '{name}'")

        except Exception as e:
            logger.error(f"Error listing jobs: {e}")
            return []

        if switch_jobs:
            logger.info(f"Found {len(switch_jobs)} Switch job(s) to clean up:")
            for job in switch_jobs:
                logger.info(f"  - Job ID: {job.job_id}, Name: '{job.settings.name}'")

        return switch_jobs

    def _delete_switch_jobs(self, switch_jobs: List[Any]) -> int:
        """Delete Switch jobs with safety checks
        
        Args:
            switch_jobs: List of Switch jobs to delete
            
        Returns:
            Number of successfully deleted jobs
        """
        deleted_count = 0
        for job in switch_jobs:
            try:
                logger.info(f"Processing job {job.job_id}: '{job.settings.name}'")

                # Check if job is currently running
                try:
                    runs = list(self.workspace_client.jobs.list_runs(job_id=job.job_id, active_only=True))
                    if runs:
                        logger.warning(f"Skipping job {job.job_id} - has {len(runs)} active runs")
                        continue
                    else:
                        logger.info(f"Job {job.job_id} has no active runs - safe to delete")
                except Exception as e:
                    logger.warning(f"Could not check active runs for job {job.job_id}: {e}")
                    logger.info(f"Proceeding with deletion of job {job.job_id}")

                # Delete the job
                logger.info(f"Deleting job {job.job_id}...")
                self.workspace_client.jobs.delete(job.job_id)
                logger.info(f"✓ Successfully deleted Switch job {job.job_id}: '{job.settings.name}'")
                deleted_count += 1

            except Exception as e:
                logger.error(f"✗ Failed to delete job {job.job_id}: {e}")

        return deleted_count


class SwitchExamplesManager:
    """Test-only examples manager for Switch testing

    WARNING: This class is for testing only. Do not use in production code.

    Provides comprehensive examples management:
    - Upload Switch example files to workspace
    - Resolve workspace paths for examples
    - Support for selective dialect/format uploading
    - Efficient batch upload operations
    """

    def __init__(self, workspace_client: WorkspaceClient):
        """Initialize examples manager

        Args:
            workspace_client: Databricks workspace client for file operations
        """
        self.workspace_client = workspace_client

    def get_examples_root_path(self) -> Path:
        """Get the path to Switch examples directory

        Returns:
            Path to switch/examples directory
        """
        # From switch/switch/testing/test_utils.py go back to switch root
        current_file = Path(__file__)
        switch_root = current_file.parent.parent.parent  # testing -> switch -> switch
        return switch_root / "examples"

    def get_example_workspace_path(self, base_dir: str, builtin_prompt: BuiltinPrompt) -> str:
        """Get workspace path for example input files based on builtin_prompt

        Args:
            base_dir: Base directory in workspace (e.g., "/Workspace/Users/.../test_base_dir")
            builtin_prompt: The builtin prompt type to get path for

        Returns:
            Workspace path to the example input directory for the given prompt

        Raises:
            ValueError: If no example files are available for the given builtin_prompt
        """
        if builtin_prompt in [BuiltinPrompt.MYSQL, BuiltinPrompt.SNOWFLAKE, BuiltinPrompt.ORACLE,
                             BuiltinPrompt.POSTGRESQL, BuiltinPrompt.REDSHIFT, BuiltinPrompt.TERADATA,
                             BuiltinPrompt.NETEZZA, BuiltinPrompt.TSQL]:
            return f"{base_dir}/examples/sql/{builtin_prompt.value}/input"
        elif builtin_prompt in [BuiltinPrompt.PYTHON, BuiltinPrompt.SCALA]:
            return f"{base_dir}/examples/code/{builtin_prompt.value}/input"
        elif builtin_prompt == BuiltinPrompt.AIRFLOW:
            return f"{base_dir}/examples/workflow/airflow/input"
        else:
            raise ValueError(f"No example files available for builtin_prompt: {builtin_prompt}")

    def upload_examples_to_workspace(self, base_dir: str, 
                                   sql_dialects: Optional[List[str]] = None,
                                   code_types: Optional[List[str]] = None,
                                   include_workflow: bool = True) -> None:
        """Upload Switch example files to workspace

        Args:
            base_dir: Base directory in workspace for examples (e.g., "/Workspace/Users/.../examples")
            sql_dialects: List of SQL dialects to upload (default: all 8 dialects)
            code_types: List of code types to upload (default: ['python', 'scala'])
            include_workflow: Whether to upload workflow examples (default: True)
        """
        logger.info("=== Starting Switch examples upload to workspace ===")

        # Set defaults
        if sql_dialects is None:
            sql_dialects = ['mysql', 'snowflake', 'oracle', 'postgresql', 'redshift', 'teradata', 'netezza', 'tsql']
        if code_types is None:
            code_types = ['python', 'scala']

        examples_root = self.get_examples_root_path()
        logger.info(f"Local examples root: {examples_root}")
        logger.info(f"Workspace base directory: {base_dir}")

        # Upload SQL examples
        self._upload_sql_examples(base_dir, sql_dialects)

        # Upload code examples  
        self._upload_code_examples(base_dir, code_types)

        # Upload workflow examples
        if include_workflow:
            self._upload_workflow_examples(base_dir)

        logger.info("=== Examples upload completed ===")

    def _upload_sql_examples(self, base_dir: str, dialects: List[str]) -> None:
        """Upload SQL dialect examples to workspace

        Args:
            base_dir: Base directory in workspace
            dialects: List of SQL dialects to upload
        """
        logger.info(f"Uploading SQL examples for dialects: {dialects}")
        examples_root = self.get_examples_root_path()

        for dialect in dialects:
            local_dir = examples_root / "sql" / dialect / "input"
            workspace_dir = f"{base_dir}/sql/{dialect}/input"
            self._upload_directory_to_workspace(local_dir, workspace_dir)

    def _upload_code_examples(self, base_dir: str, code_types: List[str]) -> None:
        """Upload code examples to workspace

        Args:
            base_dir: Base directory in workspace
            code_types: List of code types to upload (e.g., ['python', 'scala'])
        """
        logger.info(f"Uploading code examples for types: {code_types}")
        examples_root = self.get_examples_root_path()

        for code_type in code_types:
            local_dir = examples_root / "code" / code_type / "input"
            workspace_dir = f"{base_dir}/code/{code_type}/input"
            self._upload_directory_to_workspace(local_dir, workspace_dir)

    def _upload_workflow_examples(self, base_dir: str) -> None:
        """Upload workflow examples to workspace

        Args:
            base_dir: Base directory in workspace
        """
        logger.info("Uploading workflow examples")
        examples_root = self.get_examples_root_path()

        local_dir = examples_root / "workflow" / "airflow" / "input"
        workspace_dir = f"{base_dir}/workflow/airflow/input"
        self._upload_directory_to_workspace(local_dir, workspace_dir)

    def _upload_directory_to_workspace(self, local_dir: Path, workspace_dir: str) -> None:
        """Upload a local directory to workspace

        Args:
            local_dir: Local directory path
            workspace_dir: Target workspace directory path
        """
        if not local_dir.exists():
            logger.warning(f"Local directory {local_dir} does not exist, skipping")
            return

        logger.info(f"Uploading {local_dir} -> {workspace_dir}")

        # Create workspace directory
        self.workspace_client.workspace.mkdirs(workspace_dir)

        # Upload all files in the directory
        file_count = 0
        for file_path in local_dir.iterdir():
            if file_path.is_file():
                workspace_file_path = f"{workspace_dir}/{file_path.name}"
                with open(file_path, 'rb') as f:
                    content = f.read()
                self.workspace_client.workspace.upload(
                    path=workspace_file_path,
                    content=content,
                    format=ImportFormat.AUTO,
                    overwrite=True
                )
                logger.info(f"  ✓ Uploaded: {workspace_file_path}")
                file_count += 1

        logger.info(f"  Directory upload completed: {file_count} files")
