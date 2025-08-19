"""Switch job parameters and related definitions"""
import dataclasses
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from switch.notebooks.pyscripts.types.builtin_prompt import BuiltinPrompt
from switch.notebooks.pyscripts.types.comment_language import CommentLanguage
from switch.notebooks.pyscripts.types.log_level import LogLevel
from switch.notebooks.pyscripts.types.source_format import SourceFormat
from switch.notebooks.pyscripts.types.target_type import TargetType


@dataclass
class SwitchJobParameters:
    """Switch job execution parameters with validation and defaults

    This class serves multiple purposes:
    1. Execution parameters for SwitchJobExecutor
    2. Template parameters for SwitchInstaller
    3. Default value management
    """
    # Basic settings
    input_dir: Optional[str] = None
    output_dir: Optional[str] = None
    result_catalog: Optional[str] = None
    result_schema: Optional[str] = None
    builtin_prompt: Optional[BuiltinPrompt] = None

    # Conversion settings
    source_format: Optional[SourceFormat] = None
    target_type: Optional[TargetType] = None
    output_extension: Optional[str] = None

    # Execution settings
    endpoint_name: Optional[str] = None
    concurrency: Optional[int] = None
    max_fix_attempts: Optional[int] = None
    log_level: Optional[LogLevel] = None

    # Advanced settings
    token_count_threshold: Optional[int] = None
    comment_lang: Optional[CommentLanguage] = None
    conversion_prompt_yaml: Optional[str] = None
    sql_output_dir: Optional[str] = None

    # Complex optional parameters
    request_params: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Load config defaults and convert string parameters to enum types"""
        # Load defaults from config file for None values
        try:
            config_defaults = _load_switch_config_defaults()

            # Apply config defaults only to None values (preserve explicit parameters)
            if self.source_format is None:
                self.source_format = config_defaults.get('source_format')
            if self.target_type is None:
                self.target_type = config_defaults.get('target_type')
            if self.output_extension is None:
                self.output_extension = config_defaults.get('output_extension')
            if self.endpoint_name is None:
                self.endpoint_name = config_defaults.get('endpoint_name')
            if self.concurrency is None:
                self.concurrency = config_defaults.get('concurrency')
            if self.max_fix_attempts is None:
                self.max_fix_attempts = config_defaults.get('max_fix_attempts')
            if self.log_level is None:
                self.log_level = config_defaults.get('log_level')
            if self.token_count_threshold is None:
                self.token_count_threshold = config_defaults.get('token_count_threshold')
            if self.comment_lang is None:
                self.comment_lang = config_defaults.get('comment_lang')
            if self.conversion_prompt_yaml is None:
                self.conversion_prompt_yaml = config_defaults.get('conversion_prompt_yaml')
            if self.sql_output_dir is None:
                self.sql_output_dir = config_defaults.get('sql_output_dir')
        except ValueError:
            # Config file not found - continue without defaults
            pass

        # Convert string parameters to enum types if needed
        if isinstance(self.log_level, str):
            self.log_level = LogLevel(self.log_level)
        if isinstance(self.source_format, str):
            self.source_format = SourceFormat(self.source_format)
        if isinstance(self.builtin_prompt, str):
            self.builtin_prompt = BuiltinPrompt(self.builtin_prompt)
        if isinstance(self.comment_lang, str):
            self.comment_lang = CommentLanguage(self.comment_lang)
        if isinstance(self.target_type, str):
            self.target_type = TargetType(self.target_type)

    def validate(self, require_all: bool = True) -> None:
        """Validate parameters

        Args:
            require_all: If True, validate all required parameters. 
                        If False, only validate provided parameters.

        Raises:
            ValueError: If validation fails
        """
        # Validate required parameters if needed
        if require_all:
            if not self.input_dir:
                raise ValueError("input_dir is required")
            if not self.output_dir:
                raise ValueError("output_dir is required")
            if not self.result_catalog:
                raise ValueError("result_catalog is required")
            if not self.result_schema:
                raise ValueError("result_schema is required")

            # Either builtin_prompt or conversion_prompt_yaml must be specified
            if not self.builtin_prompt and not self.conversion_prompt_yaml:
                raise ValueError(
                    "Either builtin_prompt or conversion_prompt_yaml must be specified"
                )

        # Validate source format if provided
        if self.source_format and self.source_format not in SourceFormat:
            raise ValueError(
                f"source_format must be one of {list(SourceFormat)}, "
                f"got '{self.source_format}'"
            )

        # Validate target type if provided
        if self.target_type and self.target_type not in TargetType:
            raise ValueError(
                f"target_type must be one of {list(TargetType)}, "
                f"got '{self.target_type}'"
            )

        # Validate output_extension for file target type
        if self.target_type == TargetType.FILE and not self.output_extension:
            raise ValueError(
                "output_extension is required when target_type is 'file'"
            )

        # Validate numeric parameters if they're not None
        if self.token_count_threshold is not None and self.token_count_threshold <= 0:
            raise ValueError("token_count_threshold must be positive")
        if self.concurrency is not None and self.concurrency <= 0:
            raise ValueError("concurrency must be positive")
        if self.max_fix_attempts is not None and self.max_fix_attempts < 0:
            raise ValueError("max_fix_attempts must be non-negative")

    def to_job_template(self) -> Dict[str, str]:
        """Convert fields to job template dictionary for Databricks job creation.

        Creates a template with empty strings for required parameters
        and default values for optional parameters.

        Returns:
            Dictionary with string values suitable for Databricks job creation
        """
        # Define required parameters that should be empty in template
        required_fields = {"input_dir", "output_dir", "result_catalog", "result_schema"}

        # Define fields that should always be empty in template
        template_empty_fields = {"builtin_prompt", "conversion_prompt_yaml", "output_extension", "request_params", "sql_output_dir"}

        # Process all dataclass fields dynamically
        template_params = {}
        for field in dataclasses.fields(self):
            field_name = field.name

            if field_name in required_fields or field_name in template_empty_fields:
                # Required and template-empty fields get empty strings
                template_params[field_name] = ""
            else:
                # Optional parameters use current values or empty string
                value = getattr(self, field_name)
                template_params[field_name] = self._serialize_field_value(field_name, value)

        return template_params

    def to_job_params(self) -> Dict[str, str]:
        """Convert fields to job parameters for Databricks job run.

        Includes only non-None values with actual runtime parameter values.

        Returns:
            Dictionary with string values suitable for Databricks job run
        """
        params = {}

        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            if value is not None:
                params[field.name] = self._serialize_field_value(field.name, value)

        return params

    def _serialize_field_value(self, field_name: str, value: Any) -> str:
        """Serialize field value to string for job parameters
        
        Args:
            field_name: Name of the dataclass field
            value: Value to serialize
            
        Returns:
            String representation suitable for Databricks job parameters
        """
        if value is None:
            return ""
        
        # Handle enum types
        if hasattr(value, 'value'):
            return value.value
        
        # Handle request_params special case (JSON serialization)
        if field_name == 'request_params' and isinstance(value, dict):
            return json.dumps(value)
        
        # Handle all other types as string
        return str(value)


def _load_switch_config_defaults() -> Dict[str, Any]:
    """Load default values from switch/lsp/config.yml.

    Returns:
        Dict containing default values from config file

    Raises:
        ValueError: If config file cannot be found or parsed
    """
    config_path = Path(__file__).parent.parent.parent / "lsp" / "config.yml"

    if not config_path.exists():
        raise ValueError(
            f"Switch configuration file not found at {config_path}"
        )

    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f)

    # Extract default values from config options
    options = config_data.get('options', {}).get('all', [])
    defaults = {}

    for option in options:
        flag = option.get('flag')
        default_value = option.get('default')
        if flag and default_value is not None:
            # Handle special default values
            if default_value == "<none>":
                defaults[flag] = None
            else:
                defaults[flag] = default_value

    return defaults
