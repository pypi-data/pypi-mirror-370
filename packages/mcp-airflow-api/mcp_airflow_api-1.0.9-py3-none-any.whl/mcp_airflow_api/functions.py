"""
Utility functions for Airflow MCP
"""
import os
import requests
from typing import Any, Dict, Optional

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
