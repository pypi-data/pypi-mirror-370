# Switch
LLM-Powered Code Conversion Plugin for Lakebridge

## Project Description
Switch is a Lakebridge transpiler plugin that transforms SQL and other source formats into Databricks-compatible notebooks using Large Language Models (LLMs). As a core component of the Lakebridge migration platform, Switch provides automated code conversion capabilities through a multi-stage processing pipeline designed for large-scale platform migrations.

## Project Support
Please note that all projects in the /databrickslabs github account are provided for your exploration only, and are not formally supported by Databricks with Service Level Agreements (SLAs).  They are provided AS-IS and we do not make any guarantees of any kind.  Please do not submit a support ticket relating to any issues arising from the use of these projects.

Any issues discovered through the use of this project should be filed as GitHub Issues on the Repo.  They will be reviewed as time permits, but there are no formal SLAs for support.

## Key Features
- **AI-Powered Conversion**: Leverages Large Language Models for intelligent code transformation
- **Multi-Format Support**: Converts various source formats including SQL, code files, and workflow definitions
- **Flexible Output**: Generates multiple output formats tailored to your migration needs
- **Built-in Templates**: Comprehensive conversion templates for common database and platform migrations
- **Cloud-Native Processing**: Scalable execution on Databricks platform infrastructure
- **Stateful Tracking**: Maintains conversion progress and results for large-scale migrations
- **Extensible Design**: Customizable template system for specialized conversion requirements

## Using the Project

### Primary Usage: Lakebridge Integration
Switch is primarily designed as a Lakebridge transpiler plugin. To use Switch for code conversion:

1. **Install Lakebridge**: Follow the [Lakebridge documentation](https://databrickslabs.github.io/lakebridge)
2. **Install Switch transpiler**: Use Lakebridge to install the Switch transpiler plugin
3. **Run conversion**: Use Lakebridge's transpile command with Switch

For complete usage instructions and configuration options, refer to the [Lakebridge documentation](https://databrickslabs.github.io/lakebridge).

### Alternative Usage: Direct Deployment
For advanced testing or direct control, you can deploy Switch directly to a Databricks workspace:

**Cell 1: Install Switch package**

From PyPI (stable):
```python
%pip install databricks-switch-plugin
```

Or from Test PyPI (development/preview versions):
```python
%pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple databricks-switch-plugin
```

**Cell 2: Deploy Switch to workspace**
```python
from databricks.sdk import WorkspaceClient
from switch.api.installer import SwitchInstaller

ws = WorkspaceClient()
installer = SwitchInstaller(ws)
result = installer.install()

print(f"Switch job created: {result.job_url}")
```

After installation, use the created job in Databricks Jobs UI to run conversions with your specific parameters.

## For Developers
For development setup, advanced usage, testing, and technical details, see [DEVELOPER.md](./DEVELOPER.md).
