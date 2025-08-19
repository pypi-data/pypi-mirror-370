"""
Utility functions for Airflow MCP
"""
import os
import requests
from typing import Any, Dict, Optional, List

# Global session instance for connection pooling and performance optimization
_airflow_session = None

def get_airflow_session() -> requests.Session:
    """
    Get or create a global requests.Session for Airflow API calls.
    This enables connection pooling and Keep-Alive connections for better performance.
    """
    global _airflow_session
    if _airflow_session is None:
        _airflow_session = requests.Session()
        
        # Configure session defaults
        _airflow_session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'mcp-airflow-api/1.0'
        })
        
        # Configure connection pooling for better performance
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        # Configure adapter with connection pooling
        adapter = HTTPAdapter(
            pool_connections=5,  # Number of connection pools
            pool_maxsize=10,     # Maximum connections per pool
            max_retries=retry_strategy
        )
        
        # Mount adapter for both HTTP and HTTPS
        _airflow_session.mount("http://", adapter)
        _airflow_session.mount("https://", adapter)
    
    return _airflow_session

def airflow_request(method: str, path: str, **kwargs) -> requests.Response:
    """
    Make a Basic Auth request to Airflow REST API using a persistent session.
    This improves performance through connection pooling and Keep-Alive connections.
    
    'path' should be relative to AIRFLOW_API_URL (e.g., '/dags', '/pools').
    """
    base_url = os.getenv("AIRFLOW_API_URL", "").rstrip("/")
    if not base_url:
        raise RuntimeError("AIRFLOW_API_URL environment variable is not set")
    
    # Ensure path starts with /
    if not path.startswith("/"):
        path = "/" + path
    
    # Construct full URL
    full_url = base_url + path
    
    # Get authentication
    username = os.getenv("AIRFLOW_API_USERNAME")
    password = os.getenv("AIRFLOW_API_PASSWORD")
    if not username or not password:
        raise RuntimeError("AIRFLOW_API_USERNAME or AIRFLOW_API_PASSWORD environment variable is not set")
    
    auth = (username, password)
    headers = kwargs.pop("headers", {})
    
    # Use persistent session for better performance
    session = get_airflow_session()
    return session.request(method, full_url, headers=headers, auth=auth, **kwargs)

def close_airflow_session():
    """
    Close the global Airflow session and cleanup resources.
    This is optional and mainly useful for testing or application shutdown.
    """
    global _airflow_session
    if _airflow_session is not None:
        _airflow_session.close()
        _airflow_session = None

def read_prompt_template(path: str) -> str:
    """
    Reads the MCP prompt template file and returns its content as a string.
    """
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def parse_prompt_sections(template: str):
    """
    Parses the prompt template into section headings and sections.
    Returns (headings, sections).
    """
    lines = template.splitlines()
    sections = []
    current = []
    headings = []
    for line in lines:
        if line.startswith("## "):
            if current:
                sections.append("\n".join(current))
                current = []
            headings.append(line[3:].strip())
            current.append(line)
        else:
            current.append(line)
    if current:
        sections.append("\n".join(current))
    return headings, sections


def get_current_time_context() -> Dict[str, Any]:
    """
    Internal helper: Returns the current time context for relative date calculations.

    Returns:
        Current date and time information for reference in date calculations
    """
    from datetime import datetime, timedelta
    current_time = datetime.now()
    current_date_str = current_time.strftime('%Y-%m-%d')

    # Calculate relative dates based on actual current time
    yesterday = (current_time - timedelta(days=1)).strftime('%Y-%m-%d')
    last_week_start = (current_time - timedelta(days=7)).strftime('%Y-%m-%d')
    last_week_end = (current_time - timedelta(days=1)).strftime('%Y-%m-%d')
    last_3_days_start = (current_time - timedelta(days=3)).strftime('%Y-%m-%d')

    return {
        "current_date": current_date_str,
        "current_time": current_time.strftime('%Y-%m-%d %H:%M:%S'),
        "reference_date": f"{current_time.strftime('%B %d, %Y')} ({current_date_str})",
        "date_calculation_examples": {
            "yesterday": yesterday,
            "last_week": f"{last_week_start} to {last_week_end}",
            "last_3_days": f"{last_3_days_start} to {current_date_str}",
            "today": current_date_str
        }
    }

# DAG-related helper functions
def list_dags_internal(limit: int = 20,
                      offset: int = 0,
                      fetch_all: bool = False,
                      id_contains: Optional[str] = None,
                      name_contains: Optional[str] = None) -> Dict[str, Any]:
    """
    Internal helper function to list DAGs.
    This function contains the actual implementation logic that can be reused.
    """
    # Helper: server-side filtering by ID and display name
    def _filter_dags(dag_list):
        results = dag_list
        if id_contains:
            key = id_contains.lower()
            results = [d for d in results if key in d.get("dag_id", "").lower()]
        if name_contains:
            key = name_contains.lower()
            results = [d for d in results if key in (d.get("dag_display_name") or "").lower()]
        return results

    # If fetch_all=True, loop through pages to collect all DAGs
    if fetch_all:
        all_dags = []
        current_offset = offset
        total_entries = None
        pages_fetched = 0
        while True:
            # recursive call without fetch_all to fetch one page
            result = list_dags_internal(limit=limit, offset=current_offset)
            page_dags = result.get("dags", [])
            all_dags.extend(page_dags)
            pages_fetched += 1
            total_entries = result.get("total_entries", 0)
            if not result.get("has_more_pages", False) or not page_dags:
                break
            current_offset = result.get("next_offset", current_offset + limit)
        # apply filters
        filtered = _filter_dags(all_dags)
        return {
            "dags": filtered,
            "total_entries": len(filtered),
            "pages_fetched": pages_fetched,
            "limit": limit,
            "offset": offset
        }
    # Default: paginated fetch
    params = []
    params.append(f"limit={limit}")
    if offset > 0:
        params.append(f"offset={offset}")
    
    query_string = "&".join(params) if params else ""
    endpoint = f"/dags?{query_string}" if query_string else "/dags"
    
    resp = airflow_request("GET", endpoint)
    resp.raise_for_status()
    response_data = resp.json()
    dags = response_data.get("dags", [])
    dag_list = []
    for dag in dags:
        # Extract schedule interval info
        schedule_info = dag.get("schedule_interval")
        if isinstance(schedule_info, dict) and schedule_info.get("__type") == "CronExpression":
            schedule_display = schedule_info.get("value", "Unknown")
        elif schedule_info:
            schedule_display = str(schedule_info)
        else:
            schedule_display = None
        
        dag_info = {
            "dag_id": dag.get("dag_id"),
            "dag_display_name": dag.get("dag_display_name"),
            "description": dag.get("description"),
            "is_active": dag.get("is_active"),
            "is_paused": dag.get("is_paused"),
            "schedule_interval": schedule_display,
            "max_active_runs": dag.get("max_active_runs"),
            "max_active_tasks": dag.get("max_active_tasks"),
            "owners": dag.get("owners"),
            "tags": [t.get("name") for t in dag.get("tags", [])],
            "next_dagrun": dag.get("next_dagrun"),
            "next_dagrun_data_interval_start": dag.get("next_dagrun_data_interval_start"),
            "next_dagrun_data_interval_end": dag.get("next_dagrun_data_interval_end"),
            "last_parsed_time": dag.get("last_parsed_time"),
            "has_import_errors": dag.get("has_import_errors"),
            "has_task_concurrency_limits": dag.get("has_task_concurrency_limits"),
            "timetable_description": dag.get("timetable_description"),
            "fileloc": dag.get("fileloc"),
            "file_token": dag.get("file_token")
        }
        dag_list.append(dag_info)
    
    # Calculate pagination info and apply filters
    total_entries = response_data.get("total_entries", len(dag_list))
    has_more_pages = (offset + limit) < total_entries
    next_offset = offset + limit if has_more_pages else None
    filtered = _filter_dags(dag_list)
    returned_count = len(filtered)
    
    return {
        "dags": filtered,
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

def get_dag_detailed_info(dag_id: str) -> Dict[str, Any]:
    """
    Internal helper function to get detailed DAG information.
    This function contains the actual implementation logic that can be reused.
    """
    if not dag_id:
        raise ValueError("dag_id must not be empty")
    resp = airflow_request("GET", f"/dags/{dag_id}")
    resp.raise_for_status()
    dag = resp.json()
    return {
        "dag_id": dag.get("dag_id"),
        "dag_display_name": dag.get("dag_display_name"),
        "description": dag.get("description"),
        "schedule_interval": dag.get("schedule_interval"),
        "start_date": dag.get("start_date"),
        "end_date": dag.get("end_date"),
        "is_active": dag.get("is_active"),
        "is_paused": dag.get("is_paused"),
        "owners": dag.get("owners"),
        "tags": [t.get("name") for t in dag.get("tags", [])],
        "catchup": dag.get("catchup"),
        "max_active_runs": dag.get("max_active_runs"),
        "max_active_tasks": dag.get("max_active_tasks"),
        "has_task_concurrency_limits": dag.get("has_task_concurrency_limits"),
        "has_import_errors": dag.get("has_import_errors"),
        "next_dagrun": dag.get("next_dagrun"),
        "next_dagrun_data_interval_start": dag.get("next_dagrun_data_interval_start"),
        "next_dagrun_data_interval_end": dag.get("next_dagrun_data_interval_end")
    }
