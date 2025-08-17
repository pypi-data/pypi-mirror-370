# MCP Airflow API Prompt Template

## 1. Overview

This MCP server provides natural language tools for managing Apache Airflow clusters via REST API. All prompts and tool outputs are designed for minimal, LLM-friendly English responses.

**IMPORTANT: Current Date Context** - Relative dates should be resolved against the server's current time (handled internally by the tools).

**Resource-Optimized Design**: This MCP server has been optimized for efficient resource usage:
- **Optimized Default Limits**: Functions use default limits of 20 for better memory usage and faster response times
- **Comprehensive Pagination**: All listing functions include detailed pagination metadata
- **Flexible Scaling**: Users can specify higher limits (up to 1000) when needed for bulk operations

## 2. Mandatory Guidelines

- **Be Concise**: Responses should be brief and to the point.
- **Use Simple Language**: Avoid complex vocabulary or jargon.
- **Limit Technical Details**: Provide essential technical information.
- **No Personal Opinions**: Responses must be neutral and factual.
- **Respect Privacy**: Never include personal data unless explicitly requested.
- **Error Handling**: If unsure about a request, ask clarifying questions instead of making assumptions.
- **Consistent Format**: Follow the specified output format strictly.
- **No Unsolicited Advice**: Only provide advice or suggestions when requested.

## 3. Available MCP Tools

### Basic DAG Management
 `list_dags(limit=20, offset=0, fetch_all=False, id_contains=None, name_contains=None)`: List DAGs with pagination and optional filters. Set `fetch_all=True` to retrieve all pages automatically.
### Cluster Management & Health
- `get_health`: Get the health status of the Airflow webserver instance.
- `get_version`: Get version information of the Airflow instance.

### Pool Management
- `list_pools(limit, offset)`: List all pools in the Airflow instance.
- `get_pool(pool_name)`: Get detailed information about a specific pool.

### Variable Management
- `list_variables(limit, offset, order_by)`: List all variables stored in Airflow.
- `get_variable(variable_key)`: Get detailed information about a specific variable by its key.

### Task Instance Management
- `list_task_instances_all(dag_id, dag_run_id, execution_date_gte, execution_date_lte, start_date_gte, start_date_lte, end_date_gte, end_date_lte, duration_gte, duration_lte, state, pool, queue, limit, offset)`: List task instances across all DAGs with comprehensive filtering.
- `get_task_instance_details(dag_id, dag_run_id, task_id)`: Get detailed information about a specific task instance.
- `list_task_instances_batch(dag_ids, dag_run_ids, task_ids, execution_date_gte, execution_date_lte, start_date_gte, start_date_lte, end_date_gte, end_date_lte, duration_gte, duration_lte, state, pool, queue)`: List task instances in batch for bulk operations.
- `get_task_instance_extra_links(dag_id, dag_run_id, task_id)`: List extra links for a specific task instance.
- `get_task_instance_logs(dag_id, dag_run_id, task_id, try_number, full_content, token)`: Get logs for a specific task instance and try number.

### XCom Management
- `list_xcom_entries(dag_id, dag_run_id, task_id, limit, offset)`: List XCom entries for a specific task instance.
- `get_xcom_entry(dag_id, dag_run_id, task_id, xcom_key, map_index)`: Get a specific XCom entry for a task instance.

### DAG Analysis & Monitoring
- `dag_details(dag_id)`: Get comprehensive details for a specific DAG.
- `dag_graph(dag_id)`: Get task dependency graph structure for a DAG.
- `list_tasks(dag_id)`: List all tasks for a specific DAG.
- `dag_code(dag_id)`: Retrieve source code for a specific DAG.
- `list_event_logs(dag_id, task_id, run_id, limit=20, offset=0)`: List event log entries with filtering. **Optimized**: Default limit is 20 for better performance.
- `get_event_log(event_log_id)`: Get a specific event log entry by ID.
- `all_dag_event_summary()`: Get event count summary for all DAGs. **Improved**: Uses limit=1000 for DAG retrieval.
- `list_import_errors(limit=20, offset=0)`: List import errors with filtering. **Optimized**: Default limit is 20 for better performance.
- `get_import_error(import_error_id)`: Get a specific import error by ID.
- `all_dag_import_summary()`: Get import error summary for all DAGs.
- `dag_run_duration(dag_id, limit=50)`: Get run duration statistics for a DAG. **Improved**: Default limit increased from 10 to 50.
- `dag_task_duration(dag_id, run_id)`: Get task duration info for a DAG run.
- `dag_calendar(dag_id, start_date, end_date, limit=20)`: Get calendar/schedule info for a DAG. **Optimized**: Default limit is 20, configurable up to 1000.

## 4. Tool Map

| Tool Name           | Role/Description                          | Input Args                    | Output Fields                        |
|---------------------|-------------------------------------------|-------------------------------|--------------------------------------|
| **Basic DAG Management** |                                     |                               |                                      |
| list_dags           | List DAGs with pagination or all with fetch_all | limit (int), offset (int), fetch_all (bool) | dag_id, dag_display_name, is_active, is_paused, owners, tags, total_entries, has_more_pages, next_offset, pagination_info |
| running_dags        | List running DAG runs                     | None                          | dag_id, run_id, state, execution_date, start_date, end_date |
| failed_dags         | List failed DAG runs                      | None                          | dag_id, run_id, state, execution_date, start_date, end_date |
| trigger_dag         | Trigger a DAG run                         | dag_id (str)                  | dag_id, run_id, state, execution_date, start_date, end_date |
| pause_dag           | Pause a DAG                               | dag_id (str)                  | dag_id, is_paused                    |
| unpause_dag         | Unpause a DAG                             | dag_id (str)                  | dag_id, is_paused                    |
| **Cluster Management & Health** |                                   |                               |                                      |
| get_health          | Get health status of webserver            | None                          | metadatabase, scheduler, status      |
| get_version         | Get version information                   | None                          | version, git_version, build_date, api_version |
| **Pool Management** |                                           |                               |                                      |
| list_pools          | List all pools in Airflow                | limit, offset                 | pools, total_entries, slots usage   |
| get_pool            | Get specific pool details                 | pool_name (str)               | name, slots, occupied_slots, running_slots, queued_slots, open_slots, description, utilization_percentage |
| **Variable Management** |                                       |                               |                                      |
| list_variables      | List all variables in Airflow            | limit, offset, order_by       | variables, total_entries, key-value pairs |
| get_variable        | Get specific variable details             | variable_key (str)            | key, value, description, is_encrypted |
| **Task Instance Management** |                               |                               |                                      |
| list_task_instances_all | List task instances with filtering    | dag_id, dag_run_id, dates, state, pool, queue, limit, offset | task_instances, total_entries, applied_filters |
| get_task_instance_details | Get detailed task instance info     | dag_id, dag_run_id, task_id   | Comprehensive task details, execution info, state, timing |
| list_task_instances_batch | Batch list task instances           | dag_ids, dag_run_ids, task_ids, dates, state, pool, queue | task_instances, total_entries, applied_filters |
| get_task_instance_extra_links | List extra links for task       | dag_id, dag_run_id, task_id   | task_id, dag_id, dag_run_id, extra_links, total_links |
| get_task_instance_logs | Get logs for task instance           | dag_id, dag_run_id, task_id, try_number, full_content, token | content, continuation_token, metadata |
| **XCom Management** |                                           |                               |                                      |
| list_xcom_entries   | List XCom entries for task instance      | dag_id, dag_run_id, task_id, limit, offset | dag_id, dag_run_id, task_id, xcom_entries, total_entries |
| get_xcom_entry      | Get specific XCom entry                   | dag_id, dag_run_id, task_id, xcom_key, map_index | key, value, timestamp, execution_date, run_id |
| **DAG Analysis & Monitoring** |                                   |                               |                                      |
| get_dag             | Get comprehensive DAG details             | dag_id (str)                  | dag_id, schedule_interval, start_date, owners, tags, description, etc. |
| dag_graph           | Get task dependency graph                 | dag_id (str)                  | dag_id, tasks, dependencies, total_tasks |
| list_tasks          | List all tasks for a specific DAG        | dag_id (str)                  | dag_id, tasks, task_configuration_details |
| dag_code            | Get DAG source code                       | dag_id (str)                  | dag_id, file_token, source_code      |
| list_event_logs     | List event log entries with filtering     | dag_id, task_id, run_id, limit=20, offset=0 | event_logs, total_entries, limit, offset, has_more_pages, next_offset, pagination_info |
| get_event_log       | Get specific event log entry by ID        | event_log_id (int)            | event_log_id, when, event, dag_id, task_id, run_id, etc. |
| all_dag_event_summary | Get event count summary for all DAGs    | None                          | dag_summaries, total_dags, total_events (improved: uses limit=1000) |
| list_import_errors  | List import errors with filtering         | limit=20, offset=0           | import_errors, total_entries, limit, offset, has_more_pages, next_offset, pagination_info |
| get_import_error    | Get specific import error by ID           | import_error_id (int)         | import_error_id, filename, stacktrace, timestamp |
| all_dag_import_summary | Get import error summary for all DAGs | None                          | import_summaries, total_errors, affected_files |
| dag_run_duration    | Get run duration statistics               | dag_id (str), limit=50        | dag_id, runs, statistics (improved: limit 10→50) |
| dag_task_duration   | Get task duration for a run               | dag_id (str), run_id (str)    | dag_id, run_id, tasks, statistics    |
| dag_calendar        | Get calendar/schedule information         | dag_id (str), start_date, end_date, limit=20 | dag_id, schedule_interval, runs, next_runs (optimized: default 20, configurable) |

## 5. Example Queries

### Basic DAG Operations
- **list_dags**: "List all DAGs with limit 10 in a table format." → Returns up to 10 DAGs
- **list_dags**: "List all DAGs a table format." → Returns up to All DAGs (WARN: Need High Tokens)
- **list_dags**: "Show next page of DAGs." → Use offset for pagination
- **list_dags**: "List DAGs 21-40." → `list_dags(limit=20, offset=20)`
- **list_dags**: "Filter DAGs whose ID contains 'tutorial'." → `list_dags(id_contains="etl")`
- **list_dags**: "Filter DAGs whose display name contains 'tutorial'." → `list_dags(name_contains="daily")`
- **running_dags**: "Show running DAGs."
- **failed_dags**: "Show failed DAGs."
- **trigger_dag**: "Trigger DAG 'example_complex'."
- **pause_dag**: "Pause DAG 'example_complex' in a table format."
- **unpause_dag**: "Unpause DAG 'example_complex' in a table format."

### Cluster Management & Health
- **get_health**: "Check Airflow cluster health."
- **get_version**: "Get Airflow version information."

### Pool Management
- **list_pools**: "List all pools."
- **list_pools**: "Show pool usage statistics."
- **get_pool**: "Get details for pool 'default_pool'."
- **get_pool**: "Check pool utilization."

### Variable Management
- **list_variables**: "List all variables."
- **list_variables**: "Show all Airflow variables with their values."
- **get_variable**: "Get variable 'database_url'."
- **get_variable**: "Show the value of variable 'api_key'."

### Task Instance Management
- **list_task_instances_all**: "List all task instances for DAG 'example_complex'."
- **list_task_instances_all**: "Show running task instances."
- **list_task_instances_all**: "Show task instances filtered by pool 'default_pool'."
- **list_task_instances_all**: "List task instances with duration greater than 300 seconds."
- **list_task_instances_all**: "Show failed task instances from last week."
- **list_task_instances_all**: "List failed task instances from yesterday."
- **list_task_instances_all**: "Show task instances that started after 9 AM today."
- **list_task_instances_all**: "List task instances from the last 3 days with state 'failed'."
- **get_task_instance_details**: "Get details for task 'data_processing' in DAG 'example_complex' run 'scheduled__xxxxx'."
- **list_task_instances_batch**: "List failed task instances from last month."
- **list_task_instances_batch**: "Show task instances in batch for multiple DAGs from this week."
- **get_task_instance_extra_links**: "Get extra links for task 'data_processing' in latest run."
- **get_task_instance_logs**: "Retrieve logs for task 'create_entry_gcs' try number 2 of DAG 'example_complex'."

### XCom Management
- **list_xcom_entries**: "List XCom entries for task 'data_processing' in DAG 'example_complex' run 'scheduled__xxxxx'."
- **list_xcom_entries**: "Show all XCom entries for task 'data_processing' in latest run."
- **get_xcom_entry**: "Get XCom entry with key 'result' for task 'data_processing' in specific run."
- **get_xcom_entry**: "Retrieve XCom value for key 'processed_count' from task 'data_processing'."

### DAG Analysis & Monitoring
- **get_dag**: "Get details for DAG 'example_complex'."
- **dag_graph**: "Show task graph for DAG 'example_complex'."
- **list_tasks**: "List all tasks in DAG 'example_complex'."
- **dag_code**: "Get source code for DAG 'example_complex'."
- **list_event_logs**: "List event logs for DAG 'example_complex'."
- **list_event_logs**: "Show event logs with ID from yesterday for all DAGs."
- **get_event_log**: "Get event log entry with ID 12345."
- **all_dag_event_summary**: "Show event count summary for all DAGs."
- **list_import_errors**: "List import errors with ID."
- **get_import_error**: "Get import error with ID 67890."
- **all_dag_import_summary**: "Show import error summary for all DAGs."
- **dag_run_duration**: "Get run duration stats for DAG 'example_complex'."
- **dag_task_duration**: "Show latest run of DAG 'example_complex'."
- **dag_task_duration**: "Show task durations for latest run of 'manual__xxxxx'."
- **dag_calendar**: "Get calendar info for DAG 'example_complex' from last month."
- **dag_calendar**: "Show DAG schedule for 'example_complex' from this week."

## 6. Date Calculation Verification

**Before making any API calls with relative dates, verify your calculation:**

Tools automatically base relative date calculations on the server's current date/time. Examples:

| User Input | Calculation Method | Example Format |
|------------|-------------------|----------------|
| "yesterday" | current_date - 1 day | YYYY-MM-DD (1 day before current) |
| "last week" | current_date - 7 days to current_date - 1 day | YYYY-MM-DD to YYYY-MM-DD (7 days range) |
| "last 3 days" | current_date - 3 days to current_date | YYYY-MM-DD to YYYY-MM-DD (3 days range) |
| "this morning" | current_date 00:00 to 12:00 | YYYY-MM-DDTHH:mm:ssZ format |

The server always uses its current date/time for these calculations.

## 7. Formatting Rules

- Output only the requested fields.
- No extra explanation unless explicitly requested.
- Use JSON objects for tool outputs.

## 8. Logging & Environment

- Control log level via AIRFLOW_LOG_LEVEL env or --log-level CLI flag.
- Supported levels: DEBUG, INFO, WARNING, ERROR, CRITICAL.

## 9. References

- Main MCP tool file: `src/mcp_airflow_api/airflow_api.py`
- Utility functions: `src/mcp_airflow_api/functions.py`
- See README.md for full usage and configuration.
