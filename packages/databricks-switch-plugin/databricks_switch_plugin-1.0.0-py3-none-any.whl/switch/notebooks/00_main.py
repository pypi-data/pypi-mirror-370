# Databricks notebook source
# MAGIC %md
# MAGIC # Switch
# MAGIC Switch is a Databricks-native conversion tool that transforms SQL from various dialects into Databricks-compatible notebooks using Large Language Models (LLMs). Originally focused on SQL-to-Databricks-notebook conversion, Switch has been enhanced to support generic file transformations and multiple output formats. This notebook serves as the main entry point for the conversion process, routing to appropriate orchestrators based on `target_type`.
# MAGIC
# MAGIC **For complete documentation, requirements, and usage instructions**, see the [Switch Overview Documentation](https://databrickslabs.github.io/lakebridge/docs/transpile/switch_overview/).

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Set Up Configuration Parameters
# MAGIC Major configuration parameters are set up in this section.

# COMMAND ----------

# DBTITLE 1,Setup Environment
# MAGIC %pip install -e ../..
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# DBTITLE 1,Import Libraries
import json

from pyscripts.types.builtin_prompt import BuiltinPrompt
from pyscripts.types.comment_language import CommentLanguage
from pyscripts.types.log_level import LogLevel
from pyscripts.types.source_format import SourceFormat
from pyscripts.types.target_type import TargetType

# COMMAND ----------

# DBTITLE 1,Configurations
# Route parameters (1.x)
dbutils.widgets.dropdown("target_type", TargetType.NOTEBOOK.value, TargetType.get_supported_types(), "1-1 Route: Target Type")
dbutils.widgets.text("output_extension", "", "1-2 Route: Output Extension (file only)")

# Input parameters (2.x)
dbutils.widgets.text("input_dir", "", "2-1 Input: Directory Pattern")
dbutils.widgets.text("endpoint_name", "databricks-claude-sonnet-4", "2-2 Input: Serving Endpoint Name")
dbutils.widgets.text("result_catalog", "", "2-3 Input: Result Catalog")
dbutils.widgets.text("result_schema", "", "2-4 Input: Result Schema")
dbutils.widgets.text("token_count_threshold", "20000", "2-5 Input: Token Count Threshold")

# Conversion parameters (3.x)
dbutils.widgets.dropdown("source_format", SourceFormat.SQL.value, SourceFormat.get_supported_formats(), "3-1 Convert: Source Format")
dbutils.widgets.dropdown("builtin_prompt", "", [""] + BuiltinPrompt.get_supported_prompts(), "3-2 Convert: Built-in Prompt")
dbutils.widgets.dropdown("comment_lang", CommentLanguage.ENGLISH.value, CommentLanguage.get_supported_languages(), "3-3 Convert: Comment Language")
dbutils.widgets.text("concurrency", "4", "3-4 Convert: Concurrency Requests")
dbutils.widgets.dropdown("log_level", LogLevel.INFO.value, LogLevel.get_supported_levels(), "3-5 Convert: Log Level")
dbutils.widgets.text("max_fix_attempts", "1", "3-6 Convert: Max Fix Attempts")
dbutils.widgets.text("request_params", "", "3-7 Convert: Request Params (Optional)")
dbutils.widgets.text("conversion_prompt_yaml", "", "3-8 Convert: Conversion YAML (Optional)")

# Output parameters (4.x)
dbutils.widgets.text("output_dir", "", "4-1 Output: Directory")
dbutils.widgets.text("sql_output_dir", "", "4-2 Output: SQL Notebook Directory (Optional)")

# COMMAND ----------

# DBTITLE 1,Load Configurations
# Routing parameters
target_type = dbutils.widgets.get("target_type")
output_extension = dbutils.widgets.get("output_extension")

# Input and processing parameters
input_dir = dbutils.widgets.get("input_dir")
endpoint_name = dbutils.widgets.get("endpoint_name")
result_catalog = dbutils.widgets.get("result_catalog")
result_schema = dbutils.widgets.get("result_schema")
token_count_threshold = int(dbutils.widgets.get("token_count_threshold"))

# Conversion parameters
source_format = dbutils.widgets.get("source_format")
comment_lang = dbutils.widgets.get("comment_lang")
concurrency = int(dbutils.widgets.get("concurrency"))
request_params = dbutils.widgets.get("request_params")
log_level = dbutils.widgets.get("log_level")
builtin_prompt = dbutils.widgets.get("builtin_prompt")
max_fix_attempts = int(dbutils.widgets.get("max_fix_attempts"))

# Output parameters
output_dir = dbutils.widgets.get("output_dir")
sql_output_dir = dbutils.widgets.get("sql_output_dir")

# Determine which conversion YAML to use
_conversion_prompt_yaml = dbutils.widgets.get("conversion_prompt_yaml")
if _conversion_prompt_yaml:
    conversion_prompt_yaml = _conversion_prompt_yaml
else:
    if not builtin_prompt:
        raise ValueError(
            "Either 'conversion_prompt_yaml' or 'builtin_prompt' must be specified. "
            f"Supported built-in prompts: {', '.join(BuiltinPrompt.get_supported_prompts())}"
        )
    template = BuiltinPrompt.from_name(builtin_prompt)
    conversion_prompt_yaml = str(template.path)

print("Configuration loaded:")
print(f"  Target type: {target_type}")
print(f"  Output extension: {output_extension}")
print(f"  Input directory: {input_dir}")
print(f"  Output directory: {output_dir}")
print(f"  Conversion YAML: {conversion_prompt_yaml}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Execute Conversion
# MAGIC Based on `target_type`, this notebook executes the appropriate conversion process.

# COMMAND ----------

# DBTITLE 1,Execute Conversion Process
if target_type == TargetType.NOTEBOOK.value:
    print("Routing to notebook conversion orchestrator...")
    orchestrator_result = dbutils.notebook.run("orchestrators/orchestrate_to_notebook", 0, {
        "input_dir": input_dir,
        "endpoint_name": endpoint_name,
        "result_catalog": result_catalog,
        "result_schema": result_schema,
        "token_count_threshold": str(token_count_threshold),
        "source_format": source_format,
        "conversion_prompt_yaml": conversion_prompt_yaml,
        "comment_lang": comment_lang,
        "concurrency": str(concurrency),
        "request_params": request_params,
        "log_level": log_level,
        "max_fix_attempts": str(max_fix_attempts),
        "output_dir": output_dir,
        "sql_output_dir": sql_output_dir,
    })
    print("Notebook conversion completed.")

elif target_type == TargetType.FILE.value:
    print(f"Routing to file conversion orchestrator (output extension: {output_extension})...")
    orchestrator_result = dbutils.notebook.run("orchestrators/orchestrate_to_file", 0, {
        "input_dir": input_dir,
        "endpoint_name": endpoint_name,
        "result_catalog": result_catalog,
        "result_schema": result_schema,
        "token_count_threshold": str(token_count_threshold),
        "source_format": source_format,
        "conversion_prompt_yaml": conversion_prompt_yaml,
        "comment_lang": comment_lang,
        "concurrency": str(concurrency),
        "request_params": request_params,
        "log_level": log_level,
        "output_dir": output_dir,
        "output_extension": output_extension,
    })
    print("File conversion completed.")

else:
    raise ValueError(f"Invalid target_type: {target_type}. Must be 'notebook' or 'file'.")

# COMMAND ----------

# DBTITLE 1,Parse Orchestrator Results
# Parse orchestrator results to extract result table and SQL conversion data
if target_type == TargetType.NOTEBOOK.value:
    notebook_results = json.loads(orchestrator_result)
    result_table = notebook_results["result_table"]
    sql_conversion_results = notebook_results["sql_conversion_results"]
else:
    result_table = orchestrator_result
    sql_conversion_results = None

print(f"Result table: {result_table}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Conversion Results
# MAGIC High-level statistics and detailed output information for the completed conversion process.

# COMMAND ----------

# DBTITLE 1,Load Notebook Utils
# MAGIC %run ./notebook_utils

# COMMAND ----------

# DBTITLE 1,Conversion and Export Results
# Display main conversion and export results
display_main_results(result_table, output_dir, target_type)

# Display SQL conversion results if applicable (notebook target with sql_output_dir)
if target_type == TargetType.NOTEBOOK.value and sql_output_dir and sql_conversion_results:
    display_sql_conversion_summary(sql_conversion_results, sql_output_dir)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Next Steps
# MAGIC The conversion process is now complete. The results are available in the specified output directory. Review these results thoroughly to ensure the converted content meets your requirements and functions as expected.
# MAGIC
# MAGIC **Important Notes:**
# MAGIC
# MAGIC 1. **Files with 'Not converted' status:**
# MAGIC    - Often due to exceeding token count threshold or processing errors
# MAGIC    - Check the `input_tokens` column and consider splitting large files or increasing the threshold
# MAGIC    - Re-run conversion after making adjustments
# MAGIC
# MAGIC 2. **Files with 'Converted with errors' status:**
# MAGIC    - Review detailed error messages in the `error_details` column
# MAGIC    - For syntax errors: Manually fix the issues in the output files
# MAGIC    - For conversion errors: Verify LLM endpoint availability and retry if needed
# MAGIC
# MAGIC 3. **For notebook targets:** Import converted notebooks into Databricks and test functionality
# MAGIC 4. **For file targets:** Verify output format and integrate with your downstream systems
