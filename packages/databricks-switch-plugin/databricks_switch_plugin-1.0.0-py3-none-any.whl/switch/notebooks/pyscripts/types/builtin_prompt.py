"""Built-in prompt type definitions for Switch."""
from enum import Enum
from pathlib import Path


class PromptCategory(str, Enum):
    """Prompt categories matching directory structure"""
    SQL_TO_DATABRICKS_PYTHON_NOTEBOOK = "sql_to_databricks_python_notebook"
    DATABRICKS_NOTEBOOK_TO_DATABRICKS_NOTEBOOK = "databricks_notebook_to_databricks_notebook"
    CODE_TO_DATABRICKS_PYTHON_NOTEBOOK = "code_to_databricks_python_notebook"
    WORKFLOW_TO_DATABRICKS_JOBS = "workflow_to_databricks_jobs"


class BuiltinPrompt(str, Enum):
    """Built-in prompts with automatic categorization"""

    # SQL dialects
    MYSQL = "mysql"
    SNOWFLAKE = "snowflake"
    ORACLE = "oracle"
    POSTGRESQL = "postgresql"
    REDSHIFT = "redshift"
    TERADATA = "teradata"
    NETEZZA = "netezza"
    TSQL = "tsql"

    # Databricks notebook conversions
    PYTHON_TO_SQL = "python_to_sql"

    # Generic conversions
    PYTHON = "python"
    SCALA = "scala"
    AIRFLOW = "airflow"

    @property
    def category(self) -> PromptCategory:
        """Auto-classify template category"""
        sql_dialects = {
            self.MYSQL, self.SNOWFLAKE, self.ORACLE, self.POSTGRESQL,
            self.REDSHIFT, self.TERADATA, self.NETEZZA, self.TSQL
        }
        if self in sql_dialects:
            return PromptCategory.SQL_TO_DATABRICKS_PYTHON_NOTEBOOK
        elif self == self.PYTHON_TO_SQL:
            return PromptCategory.DATABRICKS_NOTEBOOK_TO_DATABRICKS_NOTEBOOK
        elif self in {self.PYTHON, self.SCALA}:
            return PromptCategory.CODE_TO_DATABRICKS_PYTHON_NOTEBOOK
        elif self == self.AIRFLOW:
            return PromptCategory.WORKFLOW_TO_DATABRICKS_JOBS
        else:
            raise ValueError(f"Unknown prompt category: {self.value}")

    # Properties
    @property
    def path(self) -> Path:
        """Complete absolute path to built-in prompt file"""
        return self._base_dir() / "resources" / "builtin_prompts" / self._relative_path

    @property
    def _relative_path(self) -> Path:
        """Relative path from builtin_prompts/"""
        return Path(self.category.value) / f"{self.value}.yml"

    # Instance methods
    def exists(self) -> bool:
        """Check if built-in prompt file exists"""
        return self.path.exists()

    # Class methods
    @classmethod
    def from_name(cls, name: str) -> 'BuiltinPrompt':
        """Type-safe built-in prompt creation with clear errors"""
        try:
            return cls(name)
        except ValueError:
            supported = ', '.join(cls.get_supported_prompts())
            raise ValueError(f"Unsupported built-in prompt '{name}'. Supported: {supported}")

    @classmethod
    def get_supported_prompts(cls) -> list[str]:
        """All supported built-in prompts"""
        return [prompt.value for prompt in cls]

    @classmethod
    def get_common_instruction_path(cls) -> Path:
        """Get path to common instruction YAML"""
        return cls._base_dir() / "resources" / "builtin_prompts" / "common" / "sql_to_databricks_notebook_common_python.yml"

    # Static methods
    @staticmethod
    def _base_dir() -> Path:
        """Base directory"""
        return Path(__file__).parent.parent.parent.parent
