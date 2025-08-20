"""
MCP tool definitions for Airflow REST API operations.

- Airflow API Documents: https://airflow.apache.org/docs/apache-airflow/2.0.0/stable-rest-api-ref.html
"""
import argparse
import asyncio
import logging
from typing import Any, Dict, List, Optional
from fastmcp import FastMCP
import os

from mcp_airflow_api.functions import airflow_request, read_prompt_template, parse_prompt_sections, get_current_time_context, list_dags_internal, get_dag_detailed_info
# Handle both direct execution and module execution
# try:
#     from .functions import airflow_request, read_prompt_template, parse_prompt_sections, get_current_time_context
# except ImportError:
#     # Fallback for direct execution
#     from functions import airflow_request, read_prompt_template, parse_prompt_sections, get_current_time_context

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


# MCP server instance for registering tools
mcp = FastMCP("mcp-airflow-api")

PROMPT_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "prompt_template.md")



@mcp.tool()
async def get_prompt_template(section: Optional[str] = None, mode: Optional[str] = None) -> str:
    """
    Returns the MCP prompt template (full, headings, or specific section).
    Args:
        section: Section number or keyword (optional)
        mode: 'full', 'headings', or None (optional)
    """
    template = read_prompt_template(PROMPT_TEMPLATE_PATH)
    
    if mode == "headings":
        headings, _ = parse_prompt_sections(template)
        lines = ["Section Headings:"]
        for title in headings:
            lines.append(title)
        return "\n".join(lines)
    
    if section:
        headings, sections = parse_prompt_sections(template)
        # Try by number
        try:
            idx = int(section) - 1
            # Skip the first section (title section) and adjust index
            if 0 <= idx < len(headings):
                return sections[idx + 1]  # +1 to skip the title section
        except Exception:
            pass
        # Try by keyword
        section_lower = section.strip().lower()
        for i, heading in enumerate(headings):
            if section_lower in heading.lower():
                return sections[i + 1]  # +1 to skip the title section
        return f"Section '{section}' not found."
    
    return template

@mcp.tool()
async def list_dags(limit: int = 20,
              offset: int = 0,
              fetch_all: bool = False,
              id_contains: Optional[str] = None,
              name_contains: Optional[str] = None) -> Dict[str, Any]:
    """
    [Tool Role]: Lists all DAGs registered in the Airflow cluster with pagination support.
    
    Args:
        limit: Maximum number of DAGs to return (default: 20)
               - For small queries: use default 100
               - For large environments: use 500-1000 to get more DAGs at once
               - Maximum recommended: 1000 (to avoid API timeouts)
        offset: Number of DAGs to skip for pagination (default: 0)
                - Use 0 for first page
                - Use limit*page_number for subsequent pages
                - Example: offset=100 for page 2 when limit=100

    Pagination Examples:
        - First 20 DAGs: list_dags()
        - Next 20 DAGs: list_dags(limit=20, offset=20)  
        - Page 3 of 50 DAGs each: list_dags(limit=50, offset=100)
        - All DAGs at once: list_dags(limit=1000)
        
    Use total_entries from response to determine if more pages exist:
        - has_more_pages = (offset + limit) < total_entries
        - next_offset = offset + limit
        - remaining_count = total_entries - (offset + limit)

    Returns:
        Dict containing:
        - dags: List of DAG objects with comprehensive info (dag_id, dag_display_name, is_active, 
                is_paused, description, schedule_interval, max_active_runs, max_active_tasks, 
                owners, tags, next_dagrun info, last_parsed_time, has_import_errors, timetable_description)
        - total_entries: Total number of DAGs in Airflow (for pagination calculation)
        - limit: Requested limit (echoed back)
        - offset: Requested offset (echoed back)
        - returned_count: Actual number of DAGs returned in this response
        - has_more_pages: Boolean indicating if more pages are available
        - next_offset: Suggested offset for next page (if has_more_pages is True)
    """
    return await list_dags_internal(limit, offset, fetch_all, id_contains, name_contains)

@mcp.tool()
async def get_dag(dag_id: str) -> Dict[str, Any]:
    """
    [Tool Role]: Retrieves detailed information for a specific DAG.

    Args:
        dag_id: The DAG ID to get details for

    Returns:
        Comprehensive DAG details: dag_id, schedule_interval, start_date, owners, tags, description, etc.
    """
    return await get_dag_detailed_info(dag_id)

@mcp.tool()
async def get_dags_detailed_batch(
    limit: int = 100,
    offset: int = 0,
    fetch_all: bool = False,
    id_contains: Optional[str] = None,
    name_contains: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_paused: Optional[bool] = None
) -> Dict[str, Any]:
    """
    [Tool Role]: Retrieves detailed information for multiple DAGs in batch with get_dag() level detail plus latest run information.
    
    This tool combines list_dags() filtering with get_dag() detailed information retrieval,
    providing comprehensive DAG details AND latest execution information for multiple DAGs in a single response.
    Each DAG entry includes both static configuration details and dynamic runtime information.
    
    Args:
        limit: Maximum number of DAGs to process (default: 100)
               - Use higher values (500-1000) for large environments
               - Ignored when fetch_all=True
        offset: Number of DAGs to skip for pagination (default: 0)
        fetch_all: If True, fetches all DAGs regardless of limit/offset (default: False)
        id_contains: Filter DAGs by ID containing this string (optional)
        name_contains: Filter DAGs by display name containing this string (optional)
        is_active: Filter by active status - True/False (optional)
        is_paused: Filter by paused status - True/False (optional)
    
    Usage Examples:
        - All unpaused DAGs with full details and latest runs: get_dags_detailed_batch(fetch_all=True, is_paused=False)
        - Active, unpaused DAGs only: get_dags_detailed_batch(is_active=True, is_paused=False)
        - DAGs containing "example": get_dags_detailed_batch(id_contains="example", limit=50)
        - Paginated batch: get_dags_detailed_batch(limit=100, offset=200)
    
    Returns:
        Dictionary containing:
        - dags_detailed: List of detailed DAG objects with:
          * All get_dag() fields (dag_id, schedule_interval, start_date, owners, tags, etc.)
          * latest_dag_run: Most recent execution information (run_id, state, start_date, end_date, etc.)
        - total_processed: Number of DAGs successfully processed
        - total_available: Total number of DAGs matching initial filters
        - processing_stats: Success/failure counts and error details
        - applied_filters: Summary of filters applied
        - pagination_info: Current page info and remaining counts
    """
    # First get the list of DAGs with basic filtering using helper function
    dag_list_result = await list_dags_internal(
        limit=limit, 
        offset=offset, 
        fetch_all=fetch_all,
        id_contains=id_contains,
        name_contains=name_contains
    )
    
    dags_basic = dag_list_result.get("dags", [])
    detailed_dags = []
    success_count = 0
    error_count = 0
    errors = []
    skipped_count = 0
    
    for dag_basic in dags_basic:
        dag_id = dag_basic.get("dag_id")
        if not dag_id:
            skipped_count += 1
            continue
            
        # Apply additional filters that require detailed DAG info
        if is_active is not None and dag_basic.get("is_active") != is_active:
            skipped_count += 1
            continue
        if is_paused is not None and dag_basic.get("is_paused") != is_paused:
            skipped_count += 1
            continue
            
        try:
            # Get detailed information for this DAG using helper function
            detailed_dag = await get_dag_detailed_info(dag_id)
            
            # Also get the latest DAG run information for comprehensive details
            try:
                latest_run_resp = await airflow_request("GET", f"/dags/{dag_id}/dagRuns?limit=1&order_by=-execution_date")
                latest_run_resp.raise_for_status()
                latest_runs = latest_run_resp.json().get("dag_runs", [])
                
                if latest_runs:
                    latest_run = latest_runs[0]
                    detailed_dag["latest_dag_run"] = {
                        "run_id": latest_run.get("run_id"),
                        "run_type": latest_run.get("run_type"),
                        "state": latest_run.get("state"),
                        "execution_date": latest_run.get("execution_date"),
                        "start_date": latest_run.get("start_date"),
                        "end_date": latest_run.get("end_date"),
                        "data_interval_start": latest_run.get("data_interval_start"),
                        "data_interval_end": latest_run.get("data_interval_end"),
                        "external_trigger": latest_run.get("external_trigger"),
                        "conf": latest_run.get("conf"),
                        "note": latest_run.get("note")
                    }
                else:
                    detailed_dag["latest_dag_run"] = None
            except Exception:
                # If we can't get latest run info, don't fail the whole operation
                detailed_dag["latest_dag_run"] = None
                
            detailed_dags.append(detailed_dag)
            success_count += 1
        except Exception as e:
            error_count += 1
            errors.append({
                "dag_id": dag_id,
                "error": str(e)
            })
    
    return {
        "dags_detailed": detailed_dags,
        "total_processed": success_count,
        "total_available": dag_list_result.get("total_entries", 0),
        "returned_count": len(detailed_dags),
        "processing_stats": {
            "success_count": success_count,
            "error_count": error_count,
            "skipped_count": skipped_count,
            "errors": errors
        },
        "applied_filters": {
            "id_contains": id_contains,
            "name_contains": name_contains,
            "is_active": is_active,
            "is_paused": is_paused,
            "limit": limit,
            "offset": offset,
            "fetch_all": fetch_all
        },
        "pagination_info": dag_list_result.get("pagination_info", {}),
        "has_more_pages": dag_list_result.get("has_more_pages", False),
        "next_offset": dag_list_result.get("next_offset")
    }

@mcp.tool()
async def running_dags() -> Dict[str, Any]:
    """
    [Tool Role]: Lists all currently running DAG runs in the Airflow cluster.

    Returns:
        List of running DAG runs with comprehensive info: dag_id, run_id, state, execution_date, 
        start_date, end_date, data_interval_start, data_interval_end, run_type, conf, 
        external_trigger, dag_display_name
    """
    # Use the global endpoint to get all DAG runs filtered by running state
    # This is much more efficient than querying each DAG individually
    resp = await airflow_request("GET", "/dags/~/dagRuns?state=running&limit=1000&order_by=-start_date")
    resp.raise_for_status()
    data = resp.json()
    
    running_runs = []
    for run in data.get("dag_runs", []):
        # Get additional DAG info if needed
        run_info = {
            "dag_id": run.get("dag_id"),
            "dag_display_name": run.get("dag_display_name"),
            "run_id": run.get("run_id"),
            "run_type": run.get("run_type"),  # manual, scheduled, dataset_triggered, etc.
            "state": run.get("state"),
            "execution_date": run.get("execution_date"),
            "start_date": run.get("start_date"),
            "end_date": run.get("end_date"),
            "data_interval_start": run.get("data_interval_start"),
            "data_interval_end": run.get("data_interval_end"),
            "external_trigger": run.get("external_trigger"),
            "conf": run.get("conf"),  # Configuration passed to the DAG run
            "note": run.get("note")
        }
        running_runs.append(run_info)
    
    return {
        "dag_runs": running_runs,
        "total_running": len(running_runs),
        "query_info": {
            "state_filter": "running",
            "limit": 1000,
            "order_by": "start_date (descending)"
        }
    }

@mcp.tool()
async def failed_dags() -> Dict[str, Any]:
    """
    [Tool Role]: Lists all recently failed DAG runs in the Airflow cluster.

    Returns:
        List of failed DAG runs with comprehensive info: dag_id, run_id, state, execution_date, 
        start_date, end_date, data_interval_start, data_interval_end, run_type, conf, 
        external_trigger, dag_display_name
    """
    # Use the global endpoint to get all DAG runs filtered by failed state
    # This is much more efficient than querying each DAG individually
    resp = await airflow_request("GET", "/dags/~/dagRuns?state=failed&limit=1000&order_by=-start_date")
    resp.raise_for_status()
    data = resp.json()
    
    failed_runs = []
    for run in data.get("dag_runs", []):
        run_info = {
            "dag_id": run.get("dag_id"),
            "dag_display_name": run.get("dag_display_name"),
            "run_id": run.get("run_id"),
            "run_type": run.get("run_type"),  # manual, scheduled, dataset_triggered, etc.
            "state": run.get("state"),
            "execution_date": run.get("execution_date"),
            "start_date": run.get("start_date"),
            "end_date": run.get("end_date"),
            "data_interval_start": run.get("data_interval_start"),
            "data_interval_end": run.get("data_interval_end"),
            "external_trigger": run.get("external_trigger"),
            "conf": run.get("conf"),  # Configuration passed to the DAG run
            "note": run.get("note")
        }
        failed_runs.append(run_info)
    
    return {
        "dag_runs": failed_runs,
        "total_failed": len(failed_runs),
        "query_info": {
            "state_filter": "failed",
            "limit": 1000,
            "order_by": "start_date (descending)"
        }
    }

@mcp.tool()
async def trigger_dag(dag_id: str) -> Dict[str, Any]:
    """
    [Tool Role]: Triggers a new DAG run for a specified Airflow DAG.

    Args:
        dag_id: The DAG ID to trigger

    Returns:
        Minimal info about triggered DAG run: dag_id, run_id, state, execution_date, start_date, end_date
    """
    if not dag_id:
        raise ValueError("dag_id must not be empty")
    resp = await airflow_request("POST", f"/dags/{dag_id}/dagRuns", json={"conf": {}})
    resp.raise_for_status()
    run = resp.json()
    return {
        "dag_id": dag_id,
        "run_id": run.get("run_id"),
        "state": run.get("state"),
        "execution_date": run.get("execution_date"),
        "start_date": run.get("start_date"),
        "end_date": run.get("end_date")
    }

@mcp.tool()
async def pause_dag(dag_id: str) -> Dict[str, Any]:
    """
    [Tool Role]: Pauses the specified Airflow DAG (prevents scheduling new runs).

    Args:
        dag_id: The DAG ID to pause

    Returns:
        Minimal info about the paused DAG: dag_id, is_paused
    """
    if not dag_id:
        raise ValueError("dag_id must not be empty")
    resp = await airflow_request("PATCH", f"/dags/{dag_id}", json={"is_paused": True})
    resp.raise_for_status()
    dag = resp.json()
    return {"dag_id": dag.get("dag_id", dag_id), "is_paused": dag.get("is_paused", True)}

@mcp.tool()
async def unpause_dag(dag_id: str) -> Dict[str, Any]:
    """
    [Tool Role]: Unpauses the specified Airflow DAG (allows scheduling new runs).

    Args:
        dag_id: The DAG ID to unpause

    Returns:
        Minimal info about the unpaused DAG: dag_id, is_paused
    """
    if not dag_id:
        raise ValueError("dag_id must not be empty")
    resp = await airflow_request("PATCH", f"/dags/{dag_id}", json={"is_paused": False})
    resp.raise_for_status()
    dag = resp.json()
    return {"dag_id": dag.get("dag_id", dag_id), "is_paused": dag.get("is_paused", False)}

@mcp.tool()
async def dag_graph(dag_id: str) -> Dict[str, Any]:
    """
    [Tool Role]: Retrieves the task dependency graph structure for a specific DAG.

    Args:
        dag_id: The DAG ID to get graph structure for

    Returns:
        DAG graph with tasks and dependencies: dag_id, tasks, dependencies
    """
    if not dag_id:
        raise ValueError("dag_id must not be empty")
    resp = await airflow_request("GET", f"/dags/{dag_id}/tasks")
    resp.raise_for_status()
    tasks = resp.json().get("tasks", [])
    
    graph_data = {"dag_id": dag_id, "tasks": [], "total_tasks": len(tasks)}
    for task in tasks:
        task_info = {
            "task_id": task.get("task_id"),
            "task_display_name": task.get("task_display_name"),
            "operator_name": task.get("class_ref", {}).get("class_name"),
            "downstream_task_ids": task.get("downstream_task_ids", []),
            "upstream_task_ids": task.get("upstream_task_ids", []),
            "start_date": task.get("start_date"),
            "end_date": task.get("end_date"),
            "depends_on_past": task.get("depends_on_past"),
            "wait_for_downstream": task.get("wait_for_downstream"),
            "retries": task.get("retries"),
            "pool": task.get("pool")
        }
        graph_data["tasks"].append(task_info)
    
    return graph_data

@mcp.tool()
async def list_tasks(dag_id: str) -> Dict[str, Any]:
    """
    [Tool Role]: Lists all tasks for a specific DAG.

    Args:
        dag_id: The DAG ID to get tasks for

    Returns:
        List of tasks with detailed task information: dag_id, tasks, total_tasks
    """
    if not dag_id:
        raise ValueError("dag_id must not be empty")
    resp = await airflow_request("GET", f"/dags/{dag_id}/tasks")
    resp.raise_for_status()
    tasks = resp.json().get("tasks", [])
    
    task_list = []
    for task in tasks:
        task_info = {
            "task_id": task.get("task_id"),
            "task_display_name": task.get("task_display_name"),
            "operator_name": task.get("class_ref", {}).get("class_name"),
            "operator_module": task.get("class_ref", {}).get("module_path"),
            "start_date": task.get("start_date"),
            "end_date": task.get("end_date"),
            "depends_on_past": task.get("depends_on_past"),
            "wait_for_downstream": task.get("wait_for_downstream"),
            "retries": task.get("retries"),
            "retry_delay": task.get("retry_delay"),
            "max_retry_delay": task.get("max_retry_delay"),
            "pool": task.get("pool"),
            "pool_slots": task.get("pool_slots"),
            "execution_timeout": task.get("execution_timeout"),
            "email_on_retry": task.get("email_on_retry"),
            "email_on_failure": task.get("email_on_failure"),
            "trigger_rule": task.get("trigger_rule"),
            "weight_rule": task.get("weight_rule"),
            "priority_weight": task.get("priority_weight")
        }
        task_list.append(task_info)
    
    return {
        "dag_id": dag_id,
        "tasks": task_list,
        "total_tasks": len(tasks)
    }

@mcp.tool()
async def dag_code(dag_id: str) -> Dict[str, Any]:
    """
    [Tool Role]: Retrieves the source code for a specific DAG.

    Args:
        dag_id: The DAG ID to get source code for

    Returns:
        DAG source code: dag_id, file_token, source_code
    """
    if not dag_id:
        raise ValueError("dag_id must not be empty")
    
    # First get DAG details to obtain file_token
    dag_resp = await airflow_request("GET", f"/dags/{dag_id}")
    dag_resp.raise_for_status()
    dag_data = dag_resp.json()
    
    file_token = dag_data.get("file_token")
    if not file_token:
        return {"dag_id": dag_id, "error": "File token not available for this DAG"}
    
    # Now get the source code using the file_token
    # Note: This endpoint returns plain text, not JSON
    source_resp = await airflow_request("GET", f"/dagSources/{file_token}")
    source_resp.raise_for_status()
    
    # Get the plain text content directly
    source_code = source_resp.text
    
    return {
        "dag_id": dag_id,
        "file_token": file_token,
        "source_code": source_code if source_code else "Source code not available"
    }

@mcp.tool()
async def list_event_logs(dag_id: str = None, task_id: str = None, run_id: str = None, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    """
    [Tool Role]: Lists event log entries with optional filtering.

    Args:
        dag_id: Filter by DAG ID (optional)
        task_id: Filter by task ID (optional)
        run_id: Filter by run ID (optional)
        limit: Maximum number of log entries to return (default: 20, increased from 20 for better coverage)
        offset: Number of entries to skip (default: 0)

    Returns:
        List of event logs: event_logs, total_entries, limit, offset, pagination metadata
    """
    # Build query parameters
    params = []
    if dag_id:
        params.append(f"dag_id={dag_id}")
    if task_id:
        params.append(f"task_id={task_id}")
    if run_id:
        params.append(f"run_id={run_id}")
    params.append(f"limit={limit}")
    params.append(f"offset={offset}")
    
    query_string = "&".join(params)
    resp = await airflow_request("GET", f"/eventLogs?{query_string}")
    resp.raise_for_status()
    logs = resp.json()
    
    events = []
    for log in logs.get("event_logs", []):
        event_info = {
            "event_log_id": log.get("event_log_id"),
            "when": log.get("when"),
            "event": log.get("event"),
            "dag_id": log.get("dag_id"),
            "task_id": log.get("task_id"),
            "run_id": log.get("run_id"),
            "map_index": log.get("map_index"),
            "try_number": log.get("try_number"),
            "owner": log.get("owner"),
            "extra": log.get("extra")
        }
        events.append(event_info)
    
    # Calculate pagination info
    total_entries = logs.get("total_entries", len(events))
    returned_count = len(events)
    has_more_pages = (offset + limit) < total_entries
    next_offset = offset + limit if has_more_pages else None
    
    return {
        "event_logs": events,
        "total_entries": total_entries,
        "limit": limit,
        "offset": offset,
        "returned_count": returned_count,
        "has_more_pages": has_more_pages,
        "next_offset": next_offset,
        "pagination_info": {
            "current_page": (offset // limit) + 1 if limit > 0 else 1,
            "total_pages": ((total_entries - 1) // limit) + 1 if limit > 0 and total_entries > 0 else 1,
            "remaining_count": max(0, total_entries - (offset + returned_count))
        }
    }

@mcp.tool()
async def get_event_log(event_log_id: int) -> Dict[str, Any]:
    """
    [Tool Role]: Retrieves a specific event log entry by ID.

    Args:
        event_log_id: The event log ID to retrieve

    Returns:
        Single event log entry: event_log_id, when, event, dag_id, task_id, run_id, etc.
    """
    if not event_log_id:
        raise ValueError("event_log_id must not be empty")
    
    resp = await airflow_request("GET", f"/eventLogs/{event_log_id}")
    resp.raise_for_status()
    log = resp.json()
    
    return {
        "event_log_id": log.get("event_log_id"),
        "when": log.get("when"),
        "event": log.get("event"),
        "dag_id": log.get("dag_id"),
        "task_id": log.get("task_id"),
        "run_id": log.get("run_id"),
        "map_index": log.get("map_index"),
        "try_number": log.get("try_number"),
        "owner": log.get("owner"),
        "extra": log.get("extra")
    }

@mcp.tool()
async def all_dag_event_summary() -> Dict[str, Any]:
    """
    [Tool Role]: Retrieves event count summary for all DAGs.

    Returns:
        Summary of event counts by DAG: dag_summaries, total_dags, total_events
    """
    # First get all DAGs with increased limit to avoid missing DAGs in large environments
    dags_resp = await airflow_request("GET", "/dags?limit=1000")
    dags_resp.raise_for_status()
    dags = dags_resp.json().get("dags", [])
    
    dag_summaries = []
    total_events = 0
    
    for dag in dags:
        dag_id = dag.get("dag_id")
        if not dag_id:
            continue
            
        # Get event count for this DAG (using limit=1 and checking total_entries)
        try:
            events_resp = await airflow_request("GET", f"/eventLogs?dag_id={dag_id}&limit=1")
            events_resp.raise_for_status()
            events_data = events_resp.json()
            event_count = events_data.get("total_entries", 0)
        except Exception:
            # If error occurs, set count to 0
            event_count = 0
        
        dag_summary = {
            "dag_id": dag_id,
            "dag_display_name": dag.get("dag_display_name"),
            "is_active": dag.get("is_active"),
            "is_paused": dag.get("is_paused"),
            "event_count": event_count
        }
        dag_summaries.append(dag_summary)
        total_events += event_count
    
    # Sort by event count (descending)
    dag_summaries.sort(key=lambda x: x["event_count"], reverse=True)
    
    return {
        "dag_summaries": dag_summaries,
        "total_dags": len(dag_summaries),
        "total_events": total_events
    }

@mcp.tool()
async def list_import_errors(limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    """
    [Tool Role]: Lists import errors with optional filtering.

    Args:
        limit: Maximum number of import errors to return (default: 20, increased from 20 for better coverage)
        offset: Number of entries to skip (default: 0)

    Returns:
        List of import errors: import_errors, total_entries, limit, offset, pagination metadata
    """
    # Build query parameters
    params = [f"limit={limit}", f"offset={offset}"]
    query_string = "&".join(params)
    
    resp = await airflow_request("GET", f"/importErrors?{query_string}")
    resp.raise_for_status()
    errors = resp.json()
    
    import_errors = []
    for error in errors.get("import_errors", []):
        error_info = {
            "import_error_id": error.get("import_error_id"),
            "filename": error.get("filename"),
            "stacktrace": error.get("stacktrace"),
            "timestamp": error.get("timestamp")
        }
        import_errors.append(error_info)
    
    # Calculate pagination info
    total_entries = errors.get("total_entries", len(import_errors))
    returned_count = len(import_errors)
    has_more_pages = (offset + limit) < total_entries
    next_offset = offset + limit if has_more_pages else None
    
    return {
        "import_errors": import_errors,
        "total_entries": total_entries,
        "limit": limit,
        "offset": offset,
        "returned_count": returned_count,
        "has_more_pages": has_more_pages,
        "next_offset": next_offset,
        "pagination_info": {
            "current_page": (offset // limit) + 1 if limit > 0 else 1,
            "total_pages": ((total_entries - 1) // limit) + 1 if limit > 0 and total_entries > 0 else 1,
            "remaining_count": max(0, total_entries - (offset + returned_count))
        }
    }

@mcp.tool()
async def get_import_error(import_error_id: int) -> Dict[str, Any]:
    """
    [Tool Role]: Retrieves a specific import error by ID.

    Args:
        import_error_id: The import error ID to retrieve

    Returns:
        Single import error: import_error_id, filename, stacktrace, timestamp
    """
    if not import_error_id:
        raise ValueError("import_error_id must not be empty")
    
    resp = await airflow_request("GET", f"/importErrors/{import_error_id}")
    resp.raise_for_status()
    error = resp.json()
    
    return {
        "import_error_id": error.get("import_error_id"),
        "filename": error.get("filename"),
        "stacktrace": error.get("stacktrace"),
        "timestamp": error.get("timestamp")
    }

@mcp.tool()
async def all_dag_import_summary() -> Dict[str, Any]:
    """
    [Tool Role]: Retrieves import error summary for all DAGs.

    Returns:
        Summary of import errors by filename: import_summaries, total_errors, affected_files
    """
    # Get all import errors (using a large limit to get all)
    try:
        errors_resp = await airflow_request("GET", "/importErrors?limit=1000")
        errors_resp.raise_for_status()
        errors_data = errors_resp.json()
        errors = errors_data.get("import_errors", [])
    except Exception:
        # If error occurs, return empty summary
        return {
            "import_summaries": [],
            "total_errors": 0,
            "affected_files": 0
        }
    
    # Group errors by filename
    filename_errors = {}
    for error in errors:
        filename = error.get("filename", "unknown")
        if filename not in filename_errors:
            filename_errors[filename] = {
                "filename": filename,
                "error_count": 0,
                "latest_timestamp": None,
                "error_ids": []
            }
        
        filename_errors[filename]["error_count"] += 1
        filename_errors[filename]["error_ids"].append(error.get("import_error_id"))
        
        # Track latest timestamp
        timestamp = error.get("timestamp")
        if timestamp:
            if not filename_errors[filename]["latest_timestamp"] or timestamp > filename_errors[filename]["latest_timestamp"]:
                filename_errors[filename]["latest_timestamp"] = timestamp
    
    # Convert to list and sort by error count
    import_summaries = list(filename_errors.values())
    import_summaries.sort(key=lambda x: x["error_count"], reverse=True)
    
    return {
        "import_summaries": import_summaries,
        "total_errors": len(errors),
        "affected_files": len(import_summaries)
    }

@mcp.tool()
async def dag_run_duration(dag_id: str, limit: int = 50) -> Dict[str, Any]:
    """
    [Tool Role]: Retrieves run duration statistics for a specific DAG.

    Args:
        dag_id: The DAG ID to get run durations for
        limit: Maximum number of recent runs to analyze (default: 50, increased from 10 for better statistics)

    Returns:
        DAG run duration data: dag_id, runs, statistics
    """
    if not dag_id:
        raise ValueError("dag_id must not be empty")
    resp = await airflow_request("GET", f"/dags/{dag_id}/dagRuns?limit={limit}&order_by=-execution_date")
    resp.raise_for_status()
    runs = resp.json().get("dag_runs", [])
    
    run_durations = []
    durations = []
    
    for run in runs:
        start_date = run.get("start_date")
        end_date = run.get("end_date")
        
        duration = None
        if start_date and end_date:
            # Calculate duration in seconds (simplified)
            duration = "calculated_duration_placeholder"
        
        run_info = {
            "run_id": run.get("run_id"),
            "execution_date": run.get("execution_date"),
            "start_date": start_date,
            "end_date": end_date,
            "state": run.get("state"),
            "duration": duration
        }
        run_durations.append(run_info)
        
        if duration:
            durations.append(duration)
    
    return {
        "dag_id": dag_id,
        "runs": run_durations,
        "total_runs_analyzed": len(runs),
        "completed_runs": len([r for r in runs if r.get("state") == "success"]),
        "failed_runs": len([r for r in runs if r.get("state") == "failed"])
    }

@mcp.tool()
async def dag_task_duration(dag_id: str, run_id: str = None) -> Dict[str, Any]:
    """
    [Tool Role]: Retrieves task duration information for a specific DAG run.

    Args:
        dag_id: The DAG ID to get task durations for
        run_id: Specific run ID (if not provided, uses latest run)

    Returns:
        Task duration data: dag_id, run_id, tasks, statistics
    """
    if not dag_id:
        raise ValueError("dag_id must not be empty")
    
    # If no run_id provided, get the latest run
    if not run_id:
        runs_resp = await airflow_request("GET", f"/dags/{dag_id}/dagRuns?limit=1&order_by=-execution_date")
        runs_resp.raise_for_status()
        runs = runs_resp.json().get("dag_runs", [])
        if not runs:
            return {"dag_id": dag_id, "error": "No runs found"}
        run_id = runs[0].get("run_id")
    
    # Get task instances for the run
    resp = await airflow_request("GET", f"/dags/{dag_id}/dagRuns/{run_id}/taskInstances")
    resp.raise_for_status()
    tasks = resp.json().get("task_instances", [])
    
    task_durations = []
    for task in tasks:
        start_date = task.get("start_date")
        end_date = task.get("end_date")
        
        duration = None
        if start_date and end_date:
            duration = "calculated_duration_placeholder"
        
        task_info = {
            "task_id": task.get("task_id"),
            "task_display_name": task.get("task_display_name"),
            "start_date": start_date,
            "end_date": end_date,
            "duration": duration,
            "state": task.get("state"),
            "try_number": task.get("try_number"),
            "max_tries": task.get("max_tries")
        }
        task_durations.append(task_info)
    
    return {
        "dag_id": dag_id,
        "run_id": run_id,
        "tasks": task_durations,
        "total_tasks": len(tasks),
        "completed_tasks": len([t for t in tasks if t.get("state") == "success"]),
        "failed_tasks": len([t for t in tasks if t.get("state") == "failed"])
    }

@mcp.tool()
async def dag_calendar(dag_id: str, start_date: str = None, end_date: str = None, limit: int = 20) -> Dict[str, Any]:
    """
    [Tool Role]: Retrieves calendar/schedule information for a specific DAG.

    Args:
        dag_id: The DAG ID to get calendar info for
        start_date: Start date for calendar range (YYYY-MM-DD format, optional)
        end_date: End date for calendar range (YYYY-MM-DD format, optional)
        limit: Maximum number of DAG runs to return (default: 20, was hardcoded at 50)

    Returns:
        DAG calendar data: dag_id, schedule_interval, runs, next_runs
    """
    if not dag_id:
        raise ValueError("dag_id must not be empty")
    
    # Get DAG details for schedule info
    dag_resp = await airflow_request("GET", f"/dags/{dag_id}")
    dag_resp.raise_for_status()
    dag = dag_resp.json()
    
    # Build query parameters for date range
    query_params = f"?limit={limit}&order_by=-execution_date"
    if start_date:
        query_params += f"&start_date_gte={start_date}T00:00:00Z"
    if end_date:
        query_params += f"&start_date_lte={end_date}T23:59:59Z"
    
    # Get DAG runs within date range
    runs_resp = await airflow_request("GET", f"/dags/{dag_id}/dagRuns{query_params}")
    runs_resp.raise_for_status()
    runs = runs_resp.json().get("dag_runs", [])
    
    calendar_runs = []
    for run in runs:
        run_info = {
            "run_id": run.get("run_id"),
            "execution_date": run.get("execution_date"),
            "start_date": run.get("start_date"),
            "end_date": run.get("end_date"),
            "state": run.get("state"),
            "run_type": run.get("run_type")
        }
        calendar_runs.append(run_info)
    
    return {
        "dag_id": dag_id,
        "schedule_interval": dag.get("schedule_interval"),
        "start_date": dag.get("start_date"),
        "next_dagrun": dag.get("next_dagrun"),
        "next_dagrun_data_interval_start": dag.get("next_dagrun_data_interval_start"),
        "next_dagrun_data_interval_end": dag.get("next_dagrun_data_interval_end"),
        "runs": calendar_runs,
        "total_runs_in_range": len(runs),
        "query_range": {
            "start_date": start_date,
            "end_date": end_date
        }
    }

@mcp.tool()
async def get_health() -> Dict[str, Any]:
    """
    [Tool Role]: Get the health status of the Airflow webserver instance.
    
    Returns:
        Health status information including metadatabase and scheduler status
    """
    resp = await airflow_request("GET", "/health")
    resp.raise_for_status()
    health_data = resp.json()
    
    return {
        "metadatabase": health_data.get("metadatabase", {}),
        "scheduler": health_data.get("scheduler", {}),
        "status": "healthy" if all([
            health_data.get("metadatabase", {}).get("status") == "healthy",
            health_data.get("scheduler", {}).get("status") == "healthy"
        ]) else "unhealthy"
    }

@mcp.tool()
async def get_version() -> Dict[str, Any]:
    """
    [Tool Role]: Get version information of the Airflow instance.
    
    Returns:
        Version information including Airflow version, Git version, and build info
    """
    resp = await airflow_request("GET", "/version")
    resp.raise_for_status()
    version_data = resp.json()
    
    return {
        "version": version_data.get("version"),
        "git_version": version_data.get("git_version"),
        "build_date": version_data.get("build_date"),
        "api_version": version_data.get("api_version", "2.0.0")
    }

@mcp.tool()
async def list_pools(limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    """
    [Tool Role]: List all pools in the Airflow instance.
    
    Args:
        limit: Maximum number of pools to return (default: 20)
        offset: Number of pools to skip for pagination (default: 0)
    
    Returns:
        List of pools with their configuration and usage information
    """
    query_params = f"?limit={limit}&offset={offset}"
    resp = await airflow_request("GET", f"/pools{query_params}")
    resp.raise_for_status()
    pools_data = resp.json()
    
    pools = []
    for pool in pools_data.get("pools", []):
        pool_info = {
            "name": pool.get("name"),
            "slots": pool.get("slots"),
            "occupied_slots": pool.get("occupied_slots"),
            "running_slots": pool.get("running_slots"),
            "queued_slots": pool.get("queued_slots"),
            "open_slots": pool.get("open_slots"),
            "description": pool.get("description")
        }
        pools.append(pool_info)
    
    return {
        "pools": pools,
        "total_entries": pools_data.get("total_entries", len(pools)),
        "limit": limit,
        "offset": offset
    }

@mcp.tool()
async def get_pool(pool_name: str) -> Dict[str, Any]:
    """
    [Tool Role]: Get detailed information about a specific pool.
    
    Args:
        pool_name: The name of the pool to retrieve
    
    Returns:
        Detailed pool information including slots usage and description
    """
    if not pool_name:
        raise ValueError("pool_name must not be empty")
    
    resp = await airflow_request("GET", f"/pools/{pool_name}")
    resp.raise_for_status()
    pool_data = resp.json()
    
    return {
        "name": pool_data.get("name"),
        "slots": pool_data.get("slots"),
        "occupied_slots": pool_data.get("occupied_slots"),
        "running_slots": pool_data.get("running_slots"),
        "queued_slots": pool_data.get("queued_slots"),
        "open_slots": pool_data.get("open_slots"),
        "description": pool_data.get("description"),
        "utilization_percentage": round(
            (pool_data.get("occupied_slots", 0) / pool_data.get("slots", 1)) * 100, 2
        ) if pool_data.get("slots", 0) > 0 else 0
    }

#========================================================================================
# Task Instance Management Functions
#========================================================================================

# Note: get_current_time_context is now an internal helper in functions.py, not exposed as an MCP tool.

@mcp.tool()
async def list_task_instances_all(dag_id: str = None, dag_run_id: str = None, execution_date_gte: str = None, execution_date_lte: str = None, start_date_gte: str = None, start_date_lte: str = None, end_date_gte: str = None, end_date_lte: str = None, duration_gte: float = None, duration_lte: float = None, state: str = None, pool: str = None, queue: str = None, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    """
    [Tool Role]: Lists task instances across all DAGs or filtered by specific DAG with comprehensive filtering options.
    
    IMPORTANT: When users provide natural language dates, calculate relative dates using the current server time context
    (internally via get_current_time_context):
    - "yesterday" = current_date - 1 day
    - "last week" = current_date - 7 days to current_date - 1 day  
    - "last 3 days" = current_date - 3 days to current_date
    - "today" = current_date

    Args:
        dag_id: Filter by DAG ID (optional)
        dag_run_id: Filter by DAG run ID (optional)
        execution_date_gte: Filter by execution date greater than or equal to (ISO 8601 format with timezone, e.g., '2024-01-01T00:00:00Z', optional)
        execution_date_lte: Filter by execution date less than or equal to (ISO 8601 format with timezone, e.g., '2024-01-01T23:59:59Z', optional)
        start_date_gte: Filter by start date greater than or equal to (ISO 8601 format with timezone, optional)
        start_date_lte: Filter by start date less than or equal to (ISO 8601 format with timezone, optional)
        end_date_gte: Filter by end date greater than or equal to (ISO 8601 format with timezone, optional)
        end_date_lte: Filter by end date less than or equal to (ISO 8601 format with timezone, optional)
        duration_gte: Filter by duration greater than or equal to (seconds, optional)
        duration_lte: Filter by duration less than or equal to (seconds, optional)
        state: Filter by task state (queued, running, success, failed, up_for_retry, up_for_reschedule, upstream_failed, skipped, deferred, scheduled, removed, restarting, optional)
        pool: Filter by pool name (optional)
        queue: Filter by queue name (optional)
        limit: Maximum number of task instances to return (default: 20)
        offset: Number of task instances to skip for pagination (default: 0)

    Returns:
        List of task instances with comprehensive information: task_instances, total_entries, limit, offset
    """
    # Log current time for verification (via internal helper)
    ctx = get_current_time_context()
    current_date_str = ctx["current_date"]
    logger.info(f"CURRENT TIME CONTEXT - Function execution time: {ctx['current_time']} | Reference date for calculations: {current_date_str}")
    
    # Auto-correct date formats to include timezone if missing
    def ensure_timezone(date_str):
        if not date_str:
            return date_str
        # If no timezone info, add 'Z' for UTC
        if 'T' in date_str and not (date_str.endswith('Z') or '+' in date_str[-6:] or '-' in date_str[-6:]):
            return date_str + 'Z'
        return date_str
    
    # Apply timezone correction to all date parameters
    execution_date_gte = ensure_timezone(execution_date_gte)
    execution_date_lte = ensure_timezone(execution_date_lte)
    start_date_gte = ensure_timezone(start_date_gte)
    start_date_lte = ensure_timezone(start_date_lte)
    end_date_gte = ensure_timezone(end_date_gte)
    end_date_lte = ensure_timezone(end_date_lte)
    
    # Build query parameters
    params = [f"limit={limit}", f"offset={offset}"]
    
    # Add optional filters (exclude dag_id when using specific DAG endpoint)
    filter_params = {
        'dag_run_id': dag_run_id,
        'execution_date_gte': execution_date_gte,
        'execution_date_lte': execution_date_lte,
        'start_date_gte': start_date_gte,
        'start_date_lte': start_date_lte,
        'end_date_gte': end_date_gte,
        'end_date_lte': end_date_lte,
        'duration_gte': duration_gte,
        'duration_lte': duration_lte,
        'state': state,
        'pool': pool,
        'queue': queue
    }
    
    for key, value in filter_params.items():
        if value is not None:
            params.append(f"{key}={value}")
    
    query_string = "&".join(params)
    
    # Choose appropriate endpoint based on whether dag_id is specified
    if dag_id:
        # Use specific DAG endpoint when dag_id is provided
        endpoint = f"/dags/{dag_id}/dagRuns/~/taskInstances?{query_string}"
    else:
        # Use global endpoint when no specific dag_id
        endpoint = f"/dags/~/dagRuns/~/taskInstances?{query_string}"
    
    resp = await airflow_request("GET", endpoint)
    resp.raise_for_status()
    data = resp.json()
    
    task_instances = []
    for task in data.get("task_instances", []):
        task_info = {
            "task_id": task.get("task_id"),
            "task_display_name": task.get("task_display_name"),
            "dag_id": task.get("dag_id"),
            "dag_run_id": task.get("dag_run_id"),
            "execution_date": task.get("execution_date"),
            "start_date": task.get("start_date"),
            "end_date": task.get("end_date"),
            "duration": task.get("duration"),
            "state": task.get("state"),
            "try_number": task.get("try_number"),
            "max_tries": task.get("max_tries"),
            "hostname": task.get("hostname"),
            "unixname": task.get("unixname"),
            "pool": task.get("pool"),
            "pool_slots": task.get("pool_slots"),
            "queue": task.get("queue"),
            "priority_weight": task.get("priority_weight"),
            "operator": task.get("operator"),
            "queued_dttm": task.get("queued_dttm"),
            "pid": task.get("pid"),
            "executor_config": task.get("executor_config"),
            "sla_miss": task.get("sla_miss"),
            "rendered_fields": task.get("rendered_fields"),
            "trigger": task.get("trigger"),
            "triggerer_job": task.get("triggerer_job"),
            "note": task.get("note")
        }
        task_instances.append(task_info)
    
    return {
        "task_instances": task_instances,
        "total_entries": data.get("total_entries", len(task_instances)),
        "limit": limit,
        "offset": offset,
        "applied_filters": {k: v for k, v in filter_params.items() if v is not None}
    }

@mcp.tool()
async def get_task_instance_details(dag_id: str, dag_run_id: str, task_id: str) -> Dict[str, Any]:
    """
    [Tool Role]: Retrieves detailed information about a specific task instance.

    Args:
        dag_id: The DAG ID containing the task
        dag_run_id: The DAG run ID containing the task instance
        task_id: The task ID to retrieve details for

    Returns:
        Detailed task instance information including execution details, state, timing, and configuration
    """
    if not dag_id or not dag_run_id or not task_id:
        raise ValueError("dag_id, dag_run_id, and task_id must not be empty")
    
    resp = await airflow_request("GET", f"/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}")
    resp.raise_for_status()
    task = resp.json()
    
    return {
        "task_id": task.get("task_id"),
        "task_display_name": task.get("task_display_name"),
        "dag_id": task.get("dag_id"),
        "dag_run_id": task.get("dag_run_id"),
        "execution_date": task.get("execution_date"),
        "start_date": task.get("start_date"),
        "end_date": task.get("end_date"),
        "duration": task.get("duration"),
        "state": task.get("state"),
        "try_number": task.get("try_number"),
        "max_tries": task.get("max_tries"),
        "hostname": task.get("hostname"),
        "unixname": task.get("unixname"),
        "pool": task.get("pool"),
        "pool_slots": task.get("pool_slots"),
        "queue": task.get("queue"),
        "priority_weight": task.get("priority_weight"),
        "operator": task.get("operator"),
        "queued_dttm": task.get("queued_dttm"),
        "pid": task.get("pid"),
        "executor_config": task.get("executor_config"),
        "sla_miss": task.get("sla_miss"),
        "rendered_fields": task.get("rendered_fields"),
        "trigger": task.get("trigger"),
        "triggerer_job": task.get("triggerer_job"),
        "note": task.get("note"),
        "map_index": task.get("map_index"),
        "rendered_map_index": task.get("rendered_map_index")
    }

@mcp.tool()
async def list_task_instances_batch(dag_ids: List[str] = None, dag_run_ids: List[str] = None, task_ids: List[str] = None, execution_date_gte: str = None, execution_date_lte: str = None, start_date_gte: str = None, start_date_lte: str = None, end_date_gte: str = None, end_date_lte: str = None, duration_gte: float = None, duration_lte: float = None, state: List[str] = None, pool: List[str] = None, queue: List[str] = None) -> Dict[str, Any]:
    """
    [Tool Role]: Lists task instances in batch with multiple filtering criteria for bulk operations.
    
    Relative date filters (if provided) are resolved against the server's current time.

    Args:
        dag_ids: List of DAG IDs to filter by (optional)
        dag_run_ids: List of DAG run IDs to filter by (optional)
        task_ids: List of task IDs to filter by (optional)
        execution_date_gte: Filter by execution date greater than or equal to (ISO format, optional)
        execution_date_lte: Filter by execution date less than or equal to (ISO format, optional)
        start_date_gte: Filter by start date greater than or equal to (ISO format, optional)
        start_date_lte: Filter by start date less than or equal to (ISO format, optional)
        end_date_gte: Filter by end date greater than or equal to (ISO format, optional)
        end_date_lte: Filter by end date less than or equal to (ISO format, optional)
        duration_gte: Filter by duration greater than or equal to (seconds, optional)
        duration_lte: Filter by duration less than or equal to (seconds, optional)
        state: List of task states to filter by (optional)
        pool: List of pool names to filter by (optional)
        queue: List of queue names to filter by (optional)

    Returns:
        Batch list of task instances with filtering results: task_instances, total_entries, applied_filters
    """
    # Prepare request body for POST batch request
    request_body = {}
    
    # Add list filters
    list_filters = {
        'dag_ids': dag_ids,
        'dag_run_ids': dag_run_ids,
        'task_ids': task_ids,
        'state': state,
        'pool': pool,
        'queue': queue
    }
    
    for key, value in list_filters.items():
        if value is not None:
            request_body[key] = value if isinstance(value, list) else [value]
    
    # Add date/duration filters
    scalar_filters = {
        'execution_date_gte': execution_date_gte,
        'execution_date_lte': execution_date_lte,
        'start_date_gte': start_date_gte,
        'start_date_lte': start_date_lte,
        'end_date_gte': end_date_gte,
        'end_date_lte': end_date_lte,
        'duration_gte': duration_gte,
        'duration_lte': duration_lte
    }
    
    for key, value in scalar_filters.items():
        if value is not None:
            request_body[key] = value
    
    # Make POST request for batch operation
    resp = await airflow_request("POST", "/dags/~/dagRuns/~/taskInstances/list", json=request_body)
    resp.raise_for_status()
    data = resp.json()
    
    task_instances = []
    for task in data.get("task_instances", []):
        task_info = {
            "task_id": task.get("task_id"),
            "task_display_name": task.get("task_display_name"),
            "dag_id": task.get("dag_id"),
            "dag_run_id": task.get("dag_run_id"),
            "execution_date": task.get("execution_date"),
            "start_date": task.get("start_date"),
            "end_date": task.get("end_date"),
            "duration": task.get("duration"),
            "state": task.get("state"),
            "try_number": task.get("try_number"),
            "max_tries": task.get("max_tries"),
            "hostname": task.get("hostname"),
            "pool": task.get("pool"),
            "queue": task.get("queue"),
            "priority_weight": task.get("priority_weight"),
            "operator": task.get("operator"),
            "note": task.get("note")
        }
        task_instances.append(task_info)
    
    return {
        "task_instances": task_instances,
        "total_entries": data.get("total_entries", len(task_instances)),
        "applied_filters": {k: v for k, v in {**list_filters, **scalar_filters}.items() if v is not None}
    }

@mcp.tool()
async def get_task_instance_extra_links(dag_id: str, dag_run_id: str, task_id: str) -> Dict[str, Any]:
    """
    [Tool Role]: Lists extra links for a specific task instance (e.g., monitoring dashboards, logs, external resources).

    Args:
        dag_id: The DAG ID containing the task
        dag_run_id: The DAG run ID containing the task instance
        task_id: The task ID to get extra links for

    Returns:
        List of extra links with their URLs and descriptions: task_id, dag_id, dag_run_id, extra_links
    """
    if not dag_id or not dag_run_id or not task_id:
        raise ValueError("dag_id, dag_run_id, and task_id must not be empty")
    
    resp = await airflow_request("GET", f"/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}/links")
    resp.raise_for_status()
    links_data = resp.json()
    
    # The response typically contains a dictionary of link names to URLs
    extra_links = []
    for link_name, link_url in links_data.items():
        if link_name != "total_entries":  # Skip metadata
            link_info = {
                "link_name": link_name,
                "link_url": link_url,
                "description": f"Extra link for {task_id}: {link_name}"
            }
            extra_links.append(link_info)
    
    return {
        "task_id": task_id,
        "dag_id": dag_id,
        "dag_run_id": dag_run_id,
        "extra_links": extra_links,
        "total_links": len(extra_links)
    }

@mcp.tool()
async def get_task_instance_logs(dag_id: str, dag_run_id: str, task_id: str, try_number: int = 1, full_content: bool = False, token: str = None) -> Dict[str, Any]:
    """
    [Tool Role]: Retrieves logs for a specific task instance and its try number with content and metadata.

    Args:
        dag_id: The DAG ID containing the task
        dag_run_id: The DAG run ID containing the task instance
        task_id: The task ID to get logs for
        try_number: The try number for the task instance (default: 1)
        full_content: Whether to return full log content or just metadata (default: False)
        token: Pagination token for large logs (optional)

    Returns:
        Task instance logs with content and metadata: task_id, dag_id, dag_run_id, try_number, content, metadata
    """
    if not dag_id or not dag_run_id or not task_id:
        raise ValueError("dag_id, dag_run_id, and task_id must not be empty")
    
    # Build query parameters
    params = [f"full_content={str(full_content).lower()}"]
    if token:
        params.append(f"token={token}")
    
    query_string = "&".join(params)
    resp = await airflow_request("GET", f"/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}/logs/{try_number}?{query_string}")
    resp.raise_for_status()
    
    # The response might be plain text for logs or JSON with metadata
    content_type = resp.headers.get('content-type', '')
    
    if 'application/json' in content_type:
        log_data = resp.json()
        return {
            "task_id": task_id,
            "dag_id": dag_id,
            "dag_run_id": dag_run_id,
            "try_number": try_number,
            "content": log_data.get("content", ""),
            "continuation_token": log_data.get("continuation_token"),
            "metadata": {
                "full_content_requested": full_content,
                "has_more": bool(log_data.get("continuation_token")),
                "content_length": len(log_data.get("content", "")),
                "content_type": "json_wrapped"
            }
        }
    else:
        # Plain text response
        log_content = resp.text
        return {
            "task_id": task_id,
            "dag_id": dag_id,
            "dag_run_id": dag_run_id,
            "try_number": try_number,
            "content": log_content,
            "continuation_token": None,
            "metadata": {
                "full_content_requested": full_content,
                "has_more": False,
                "content_length": len(log_content),
                "content_type": "plain_text"
            }
        }

#========================================================================================

@mcp.tool()
async def list_variables(limit: int = 20, offset: int = 0, order_by: str = "key") -> Dict[str, Any]:
    """
    [Tool Role]: Lists all variables stored in Airflow.

    Args:
        limit: Maximum number of variables to return (default: 20)
        offset: Number of variables to skip for pagination (default: 0)
        order_by: Order variables by field (key, description) (default: key)

    Returns:
        List of variables with their keys, values, and descriptions
    """
    params = [f"limit={limit}", f"offset={offset}", f"order_by={order_by}"]
    query_string = "&".join(params)
    
    resp = await airflow_request("GET", f"/variables?{query_string}")
    resp.raise_for_status()
    data = resp.json()
    
    variables = []
    for var in data.get("variables", []):
        var_info = {
            "key": var.get("key"),
            "value": var.get("value"),
            "description": var.get("description"),
            "is_encrypted": var.get("is_encrypted", False)
        }
        variables.append(var_info)
    
    return {
        "variables": variables,
        "total_entries": data.get("total_entries", len(variables)),
        "limit": limit,
        "offset": offset
    }

@mcp.tool()
async def get_variable(variable_key: str) -> Dict[str, Any]:
    """
    [Tool Role]: Retrieves a specific variable by its key from Airflow.

    Args:
        variable_key: The key of the variable to retrieve

    Returns:
        Variable information including key, value, and description
    """
    if not variable_key:
        raise ValueError("variable_key must not be empty")
    
    resp = await airflow_request("GET", f"/variables/{variable_key}")
    resp.raise_for_status()
    var = resp.json()
    
    return {
        "key": var.get("key"),
        "value": var.get("value"),
        "description": var.get("description"),
        "is_encrypted": var.get("is_encrypted", False)
    }

#========================================================================================

#========================================================================================
# XCom Management
#========================================================================================

@mcp.tool()
async def list_xcom_entries(
    dag_id: str,
    dag_run_id: str,
    task_id: str,
    limit: int = 20,
    offset: int = 0
) -> Dict[str, Any]:
    """
    [Tool Role]: Lists XCom entries for a specific task instance.

    Args:
        dag_id: The DAG ID
        dag_run_id: The DAG run ID  
        task_id: The task ID
        limit: Maximum number of entries to return (default: 20)
        offset: Number of entries to skip (default: 0)

    Returns:
        Dictionary containing XCom entries with key, value, timestamp, and other metadata
    """
    path = f"/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}/xcomEntries"
    params = {
        "limit": limit,
        "offset": offset
    }
    
    resp = await airflow_request("GET", path, params=params)
    resp.raise_for_status()
    data = resp.json()
    
    xcom_entries = data.get("xcom_entries", [])
    processed_entries = []
    
    for entry in xcom_entries:
        entry_info = {
            "key": entry.get("key"),
            "timestamp": entry.get("timestamp"),
            "execution_date": entry.get("execution_date"),
            "task_id": entry.get("task_id"),
            "dag_id": entry.get("dag_id"),
            "run_id": entry.get("run_id"),
            "value": entry.get("value"),  # Note: may be truncated in list view
            "map_index": entry.get("map_index", -1)
        }
        processed_entries.append(entry_info)
    
    return {
        "dag_id": dag_id,
        "dag_run_id": dag_run_id, 
        "task_id": task_id,
        "xcom_entries": processed_entries,
        "total_entries": data.get("total_entries", len(processed_entries)),
        "limit": limit,
        "offset": offset
    }

@mcp.tool()
async def get_xcom_entry(
    dag_id: str,
    dag_run_id: str,
    task_id: str,
    xcom_key: str,
    map_index: int = -1
) -> Dict[str, Any]:
    """
    [Tool Role]: Retrieves a specific XCom entry for a task instance.

    Args:
        dag_id: The DAG ID
        dag_run_id: The DAG run ID
        task_id: The task ID  
        xcom_key: The XCom key to retrieve
        map_index: Map index for mapped tasks (default: -1 for non-mapped)

    Returns:
        Dictionary containing the specific XCom entry with full value and metadata
    """
    path = f"/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}/xcomEntries/{xcom_key}"
    params = {}
    if map_index != -1:
        params["map_index"] = map_index
        
    resp = await airflow_request("GET", path, params=params)
    resp.raise_for_status()
    entry = resp.json()
    
    return {
        "dag_id": dag_id,
        "dag_run_id": dag_run_id,
        "task_id": task_id,
        "xcom_key": xcom_key,
        "map_index": map_index,
        "key": entry.get("key"),
        "value": entry.get("value"),
        "timestamp": entry.get("timestamp"),
        "execution_date": entry.get("execution_date"),
        "run_id": entry.get("run_id")
    }

#========================================================================================

#========================================================================================
# MCP Prompts (for prompts/list exposure)
#========================================================================================

@mcp.prompt("prompt_template_full")
def prompt_template_full_prompt() -> str:
    """Return the full canonical prompt template."""
    return read_prompt_template(PROMPT_TEMPLATE_PATH)

@mcp.prompt("prompt_template_headings")
def prompt_template_headings_prompt() -> str:
    """Return compact list of section headings."""
    template = read_prompt_template(PROMPT_TEMPLATE_PATH)
    headings, _ = parse_prompt_sections(template)
    lines = ["Section Headings:"]
    for idx, title in enumerate(headings, 1):
        lines.append(f"{idx}. {title}")
    return "\n".join(lines)

@mcp.prompt("prompt_template_section")
def prompt_template_section_prompt(section: Optional[str] = None) -> str:
    """Return a specific prompt template section by number or keyword."""
    if not section:
        headings_result = prompt_template_headings_prompt()
        return "\n".join([
            "[HELP] Missing 'section' argument.",
            "Specify a section number or keyword.",
            "Examples: 1 | overview | tool map | usage",
            headings_result.strip()
        ])
    return get_prompt_template(section=section)

#========================================================================================
# Connection Management Functions
#========================================================================================

@mcp.tool()
async def list_connections(limit: int = 20, 
                    offset: int = 0, 
                    fetch_all: bool = False,
                    order_by: str = "connection_id",
                    id_contains: Optional[str] = None,
                    conn_type_contains: Optional[str] = None,
                    description_contains: Optional[str] = None) -> Dict[str, Any]:
    """
    [Tool Role]: List all connections in the Airflow instance with pagination and advanced filtering support.
    
    Args:
        limit: Maximum number of connections to return (default: 20)
               - For small queries: use default 20
               - For large environments: use 100-500 to get more connections at once
               - Maximum recommended: 1000 (to avoid API timeouts)
        offset: Number of connections to skip for pagination (default: 0)
        fetch_all: If True, fetches ALL connections regardless of limit (default: False)
                  - Use with caution in large environments
                  - Automatically handles pagination internally
        order_by: Field to order by (default: "connection_id")
                 Valid values: connection_id, conn_type, host, schema, login
        id_contains: Filter connections whose connection_id contains this string (case-insensitive)
                    - Example: "postgres" → only connections with "postgres" in their ID
        conn_type_contains: Filter connections whose conn_type contains this string (case-insensitive)
                           - Example: "http" → only HTTP-based connections
        description_contains: Filter connections whose description contains this string (case-insensitive)
                             - Example: "prod" → only connections with "prod" in description
    
    Returns:
        List of connections with their configuration: connections, total_entries, limit, offset, applied_filters
    """
    if fetch_all:
        # Fetch all connections with automatic pagination
        all_connections = []
        current_offset = 0
        batch_limit = 100  # Use reasonable batch size
        
        while True:
            params = [f"limit={batch_limit}", f"offset={current_offset}"]
            if order_by:
                params.append(f"order_by={order_by}")
            
            query_string = "&".join(params)
            resp = await airflow_request("GET", f"/connections?{query_string}")
            resp.raise_for_status()
            batch_data = resp.json()
            
            batch_connections = batch_data.get("connections", [])
            if not batch_connections:
                break
                
            all_connections.extend(batch_connections)
            current_offset += batch_limit
            
            # Check if we've gotten all connections
            if len(batch_connections) < batch_limit:
                break
        
        raw_connections = all_connections
        total_from_api = len(all_connections)
    else:
        # Regular paginated fetch
        params = [f"limit={limit}", f"offset={offset}"]
        if order_by:
            params.append(f"order_by={order_by}")
        
        query_string = "&".join(params)
        resp = await airflow_request("GET", f"/connections?{query_string}")
        resp.raise_for_status()
        data = resp.json()
        
        raw_connections = data.get("connections", [])
        total_from_api = data.get("total_entries", len(raw_connections))
    
    # Apply client-side filtering (since Airflow API doesn't support these filters)
    filtered_connections = []
    applied_filters = []
    
    for conn in raw_connections:
        # Check id_contains filter
        if id_contains:
            conn_id = conn.get("connection_id", "").lower()
            if id_contains.lower() not in conn_id:
                continue
        
        # Check conn_type_contains filter  
        if conn_type_contains:
            conn_type = conn.get("conn_type", "").lower()
            if conn_type_contains.lower() not in conn_type:
                continue
        
        # Check description_contains filter
        if description_contains:
            description = conn.get("description", "").lower()
            if description_contains.lower() not in description:
                continue
        
        # Only return safe connection info (exclude sensitive data like passwords)
        conn_info = {
            "connection_id": conn.get("connection_id"),
            "conn_type": conn.get("conn_type"),
            "description": conn.get("description"),
            "host": conn.get("host"),
            "schema": conn.get("schema"),
            "login": conn.get("login"),
            "port": conn.get("port"),
            "is_encrypted": conn.get("is_encrypted"),
            "is_extra_encrypted": conn.get("is_extra_encrypted"),
            "extra": conn.get("extra")  # Note: may contain sensitive data
        }
        filtered_connections.append(conn_info)
    
    # Record applied filters
    if id_contains:
        applied_filters.append(f"id_contains='{id_contains}'")
    if conn_type_contains:
        applied_filters.append(f"conn_type_contains='{conn_type_contains}'")
    if description_contains:
        applied_filters.append(f"description_contains='{description_contains}'")
    if order_by:
        applied_filters.append(f"order_by='{order_by}'")
    
    # Calculate pagination info for filtered results
    total_entries = len(filtered_connections)
    returned_count = len(filtered_connections)
    
    if not fetch_all:
        # Apply pagination to filtered results
        start_idx = 0  # We already applied offset in API call
        end_idx = len(filtered_connections)
        paginated_connections = filtered_connections[start_idx:end_idx]
        
        has_more_pages = (offset + limit) < total_from_api
        next_offset = offset + limit if has_more_pages else None
    else:
        paginated_connections = filtered_connections
        has_more_pages = False
        next_offset = None
    
    return {
        "connections": paginated_connections,
        "total_entries": total_entries,
        "total_from_api": total_from_api,
        "limit": limit if not fetch_all else len(filtered_connections),
        "offset": offset if not fetch_all else 0,
        "returned_count": len(paginated_connections),
        "has_more_pages": has_more_pages,
        "next_offset": next_offset,
        "applied_filters": applied_filters,
        "pagination_info": {
            "current_page": (offset // limit) + 1 if limit > 0 and not fetch_all else 1,
            "total_pages": ((total_entries - 1) // limit) + 1 if limit > 0 and total_entries > 0 and not fetch_all else 1,
            "remaining_count": max(0, total_entries - (offset + returned_count)) if not fetch_all else 0
        }
    }

@mcp.tool()
async def get_connection(connection_id: str) -> Dict[str, Any]:
    """
    [Tool Role]: Get detailed information about a specific connection.
    
    Args:
        connection_id: The connection ID to retrieve
    
    Returns:
        Detailed connection information (excluding sensitive password data)
    """
    if not connection_id:
        raise ValueError("connection_id must not be empty")
    
    resp = await airflow_request("GET", f"/connections/{connection_id}")
    resp.raise_for_status()
    conn = resp.json()
    
    # Return connection info but mask sensitive data
    return {
        "connection_id": conn.get("connection_id"),
        "conn_type": conn.get("conn_type"),
        "description": conn.get("description"),
        "host": conn.get("host"),
        "schema": conn.get("schema"),
        "login": conn.get("login"),
        "port": conn.get("port"),
        "is_encrypted": conn.get("is_encrypted"),
        "is_extra_encrypted": conn.get("is_extra_encrypted"),
        "extra": conn.get("extra"),  # Note: may contain sensitive data
        "password": "[MASKED]" if conn.get("password") else None
    }

@mcp.tool()
async def create_connection(
    connection_id: str,
    conn_type: str,
    description: Optional[str] = None,
    host: Optional[str] = None,
    login: Optional[str] = None,
    password: Optional[str] = None,
    db_schema: Optional[str] = None,
    port: Optional[int] = None,
    extra: Optional[str] = None
) -> Dict[str, Any]:
    """
    [Tool Role]: Create a new connection in Airflow.
    
    Args:
        connection_id: Unique identifier for the connection
        conn_type: Type of connection (e.g., 'postgres', 'mysql', 'http', 's3', etc.)
        description: Optional description of the connection
        host: Host address for the connection
        login: Login/username for authentication
        password: Password for authentication (will be encrypted)
        db_schema: Database schema or namespace
        port: Port number for the connection
        extra: Additional connection parameters as JSON string
    
    Returns:
        Created connection information (excluding sensitive data)
    """
    if not connection_id or not conn_type:
        raise ValueError("connection_id and conn_type are required")
    
    # Build request body
    conn_data = {
        "connection_id": connection_id,
        "conn_type": conn_type
    }
    
    # Add optional fields
    optional_fields = {
        "description": description,
        "host": host,
        "login": login,
        "password": password,
        "schema": db_schema,
        "port": port,
        "extra": extra
    }
    
    for key, value in optional_fields.items():
        if value is not None:
            conn_data[key] = value
    
    resp = await airflow_request("POST", "/connections", json=conn_data)
    resp.raise_for_status()
    conn = resp.json()
    
    return {
        "connection_id": conn.get("connection_id"),
        "conn_type": conn.get("conn_type"),
        "description": conn.get("description"),
        "host": conn.get("host"),
        "login": conn.get("login"),
        "schema": conn.get("schema"),
        "port": conn.get("port"),
        "is_encrypted": conn.get("is_encrypted"),
        "is_extra_encrypted": conn.get("is_extra_encrypted"),
        "extra": conn.get("extra"),
        "password": "[MASKED]" if conn.get("password") else None,
        "status": "created"
    }

@mcp.tool()
async def update_connection(
    connection_id: str,
    conn_type: Optional[str] = None,
    description: Optional[str] = None,
    host: Optional[str] = None,
    login: Optional[str] = None,
    password: Optional[str] = None,
    db_schema: Optional[str] = None,
    port: Optional[int] = None,
    extra: Optional[str] = None
) -> Dict[str, Any]:
    """
    [Tool Role]: Update an existing connection in Airflow.
    
    Args:
        connection_id: The connection ID to update
        conn_type: Type of connection (optional for updates)
        description: Optional description of the connection
        host: Host address for the connection
        login: Login/username for authentication
        password: Password for authentication (will be encrypted)
        db_schema: Database schema or namespace
        port: Port number for the connection
        extra: Additional connection parameters as JSON string
    
    Returns:
        Updated connection information (excluding sensitive data)
    """
    if not connection_id:
        raise ValueError("connection_id must not be empty")
    
    # Build request body with only provided fields
    conn_data = {}
    
    update_fields = {
        "conn_type": conn_type,
        "description": description,
        "host": host,
        "login": login,
        "password": password,
        "schema": db_schema,
        "port": port,
        "extra": extra
    }
    
    for key, value in update_fields.items():
        if value is not None:
            conn_data[key] = value
    
    if not conn_data:
        raise ValueError("At least one field must be provided for update")
    
    resp = await airflow_request("PATCH", f"/connections/{connection_id}", json=conn_data)
    resp.raise_for_status()
    conn = resp.json()
    
    return {
        "connection_id": conn.get("connection_id"),
        "conn_type": conn.get("conn_type"),
        "description": conn.get("description"),
        "host": conn.get("host"),
        "login": conn.get("login"),
        "schema": conn.get("schema"),
        "port": conn.get("port"),
        "is_encrypted": conn.get("is_encrypted"),
        "is_extra_encrypted": conn.get("is_extra_encrypted"),
        "extra": conn.get("extra"),
        "password": "[MASKED]" if conn.get("password") else None,
        "status": "updated"
    }

@mcp.tool()
async def delete_connection(connection_id: str) -> Dict[str, Any]:
    """
    [Tool Role]: Delete a connection from Airflow.
    
    Args:
        connection_id: The connection ID to delete
    
    Returns:
        Confirmation of deletion: connection_id, status
    """
    if not connection_id:
        raise ValueError("connection_id must not be empty")
    
    resp = await airflow_request("DELETE", f"/connections/{connection_id}")
    resp.raise_for_status()
    
    return {
        "connection_id": connection_id,
        "status": "deleted",
        "message": f"Connection '{connection_id}' has been successfully deleted"
    }

#========================================================================================
# Configuration Management Functions
#========================================================================================

@mcp.tool()
async def get_config() -> Dict[str, Any]:
    """
    [Tool Role]: Get all configuration sections and options from the Airflow instance.
    
    Note: This endpoint is controlled by the 'expose_config' setting in airflow.cfg.
    Even admin users will get 403 FORBIDDEN if expose_config = False.
    
    Returns:
        Complete Airflow configuration: sections with their options and values
    """
    try:
        resp = await airflow_request("GET", "/config")
        resp.raise_for_status()
        config_data = resp.json()
        
        # Process config data according to Airflow 2.0.0 API structure
        sections_processed = {}
        total_sections = 0
        total_options = 0
        
        for section in config_data.get("sections", []):
            section_name = section.get("name", "")
            section_options = {}
            
            for option in section.get("options", []):
                option_key = option.get("key", "")
                option_value = option.get("value", "")
                
                # Basic security: mask values that look like passwords or secrets
                if any(keyword in option_key.lower() for keyword in ['password', 'secret', 'key', 'token']):
                    if option_value:
                        option_value = "[SENSITIVE_VALUE_MASKED]"
                
                section_options[option_key] = {
                    "value": option_value,
                    "key": option_key
                }
                total_options += 1
            
            sections_processed[section_name] = {
                "options": section_options,
                "option_count": len(section_options)
            }
            total_sections += 1
        
        return {
            "sections": sections_processed,
            "total_sections": total_sections,
            "total_options": total_options,
            "raw_sections": config_data.get("sections", []),  # Include raw data for reference
            "note": "Configuration access requires appropriate permissions in Airflow"
        }
        
    except Exception as e:
        if "403" in str(e) or "FORBIDDEN" in str(e):
            return {
                "error": "Configuration access blocked by Airflow settings",
                "message": "The configuration endpoint is disabled in Airflow.",
                "airflow_setting": "expose_config = False in airflow.cfg",
                "solution_steps": [
                    "1. Edit /opt/airflow/airflow.cfg (or your Airflow config file)",
                    "2. Find [webserver] section",
                    "3. Change 'expose_config = False' to 'expose_config = True'",
                    "4. Or set 'expose_config = non-sensitive-only' for partial access",
                    "5. Restart Airflow webserver service",
                    "6. Alternative: Set environment variable AIRFLOW__WEBSERVER__EXPOSE_CONFIG=True"
                ],
                "security_note": "expose_config = True shows all configuration values including sensitive data",
                "status": "403_FORBIDDEN_BY_CONFIG",
                "admin_note": "Even admin users cannot access config when expose_config = False"
            }
        else:
            return {
                "error": "Configuration retrieval failed",
                "message": str(e),
                "suggestion": "Check Airflow connection and server status"
            }

@mcp.tool()
async def list_config_sections() -> Dict[str, Any]:
    """
    [Tool Role]: List all available configuration sections with summary information.
    
    Note: This is a convenience tool that processes the /config endpoint to show section summaries.
    
    Returns:
        List of configuration sections with option counts and section names
    """
    try:
        config_result = get_config()
        
        # Check if we got an error response
        if "error" in config_result:
            return config_result  # Return the error as-is
        
        sections_summary = []
        for section_name, section_data in config_result.get("sections", {}).items():
            section_summary = {
                "section_name": section_name,
                "option_count": section_data.get("option_count", 0),
                "sample_options": list(section_data.get("options", {}).keys())[:5]  # First 5 options
            }
            sections_summary.append(section_summary)
        
        return {
            "sections": sections_summary,
            "total_sections": config_result.get("total_sections", 0),
            "total_options": config_result.get("total_options", 0),
            "common_sections_info": {
                "note": "Common sections typically include core, webserver, scheduler, database, logging",
                "access_requirement": "Configuration access requires appropriate Airflow permissions"
            }
        }
        
    except Exception as e:
        return {
            "error": "Failed to retrieve configuration sections",
            "message": str(e),
            "suggestion": "Check Airflow connection and permissions"
        }

@mcp.tool()
async def get_config_section(section: str) -> Dict[str, Any]:
    """
    [Tool Role]: Get all configuration options for a specific section.
    
    Note: This tool filters the /config endpoint results by section name,
    as Airflow 2.0.0 API doesn't support /config/{section} endpoint.
    
    Args:
        section: The configuration section name (e.g., 'core', 'webserver', 'scheduler')
    
    Returns:
        Section configuration options with values (if accessible)
    """
    if not section:
        return {"error": "Section name must not be empty"}
    
    try:
        config_result = get_config()
        
        # Check if we got an error response
        if "error" in config_result:
            return config_result  # Return the error as-is
        
        sections = config_result.get("sections", {})
        
        if section not in sections:
            available_sections = list(sections.keys())
            return {
                "error": f"Section '{section}' not found",
                "available_sections": available_sections,
                "suggestion": f"Use one of the available sections: {', '.join(available_sections)}"
            }
        
        section_data = sections[section]
        options = section_data.get("options", {})
        
        return {
            "section": section,
            "options": options,
            "total_options": len(options),
            "option_names": list(options.keys())
        }
        
    except Exception as e:
        return {
            "error": f"Failed to retrieve section '{section}'",
            "message": str(e)
        }

@mcp.tool()
async def search_config_options(search_term: str) -> Dict[str, Any]:
    """
    [Tool Role]: Search for configuration options by key name.
    
    Note: Searches within the /config endpoint results for matching option keys.
    
    Args:
        search_term: Text to search for in option keys (case-insensitive)
    
    Returns:
        Matching configuration options across all sections
    """
    if not search_term:
        return {"error": "Search term must not be empty"}
    
    try:
        config_result = get_config()
        
        # Check if we got an error response
        if "error" in config_result:
            return config_result  # Return the error as-is
        
        matches = []
        search_lower = search_term.lower()
        
        for section_name, section_data in config_result.get("sections", {}).items():
            for option_key, option_data in section_data.get("options", {}).items():
                if search_lower in option_key.lower():
                    match = {
                        "section": section_name,
                        "option_key": option_key,
                        "value": option_data.get("value", ""),
                        "match_type": "key_name"
                    }
                    matches.append(match)
        
        return {
            "search_term": search_term,
            "matches": matches,
            "total_matches": len(matches),
            "sections_searched": list(config_result.get("sections", {}).keys())
        }
        
    except Exception as e:
        return {
            "error": f"Failed to search configuration options",
            "message": str(e)
        }

#========================================================================================

def main(argv: Optional[List[str]] = None):
    """Entrypoint for MCP Airflow API server.

    Supports optional CLI arguments (e.g. --log-level DEBUG) while remaining
    backward-compatible with stdio launcher expectations.
    """
    parser = argparse.ArgumentParser(prog="mcp-airflow-api", description="MCP Airflow API Server")
    parser.add_argument(
        "--log-level",
        dest="log_level",
        help="Logging level override (DEBUG, INFO, WARNING, ERROR, CRITICAL). Overrides AIRFLOW_LOG_LEVEL env if provided.",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    parser.add_argument(
        "--type",
        dest="transport_type",
        help="Transport type (stdio or streamable-http). Default: stdio",
        choices=["stdio", "streamable-http"],
    )
    parser.add_argument(
        "--host",
        dest="host",
        help="Host address for streamable-http transport. Default: 127.0.0.1",
    )
    parser.add_argument(
        "--port",
        dest="port",
        type=int,
        help="Port number for streamable-http transport. Default: 8080",
    )
    # Allow future extension without breaking unknown args usage
    args = parser.parse_args(argv)

    # Determine log level: CLI arg > environment variable > default
    log_level = args.log_level or os.getenv("AIRFLOW_LOG_LEVEL", "INFO")
    
    # Set logging level
    logging.getLogger().setLevel(log_level)
    logger.setLevel(log_level)
    logging.getLogger("aiohttp.client").setLevel("WARNING")  # reduce noise at DEBUG
    
    if args.log_level:
        logger.info("Log level set via CLI to %s", args.log_level)
    elif os.getenv("AIRFLOW_LOG_LEVEL"):
        logger.info("Log level set via environment variable to %s", log_level)
    else:
        logger.info("Using default log level: %s", log_level)

    # 우선순위: 실행옵션 > 환경변수 > 기본값
    # Transport type 결정
    transport_type = args.transport_type or os.getenv("FASTMCP_TYPE", "stdio")
    
    # Host 결정
    host = args.host or os.getenv("FASTMCP_HOST", "127.0.0.1")
    
    # Port 결정 (간결하게)
    port = args.port or int(os.getenv("FASTMCP_PORT", 8080))
    
    # Transport 모드에 따른 실행
    if transport_type == "streamable-http":
        logger.info(f"Starting streamable-http server on {host}:{port}")
        mcp.run(transport="streamable-http", host=host, port=port)
    else:
        logger.info("Starting stdio transport for local usage")
        mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
