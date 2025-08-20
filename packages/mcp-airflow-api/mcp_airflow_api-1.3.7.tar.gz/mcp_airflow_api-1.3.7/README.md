# 🚀 MCP-Airflow-API: Revolutionary Open Source Tool for Managing Apache Airflow with Natural Language

Have you ever wondered how amazing it would be if you could manage your Apache Airflow workflows using natural language instead of complex REST API calls or web interface manipulations? **MCP-Airflow-API** is the revolutionary open-source project that makes this goal a reality.

![MCP-Airflow-API Screenshot](img/screenshot-000.png)

---

## 🎯 What is MCP-Airflow-API?

MCP-Airflow-API is an MCP server that leverages the **Model Context Protocol (MCP)** to transform Apache Airflow REST API operations into natural language tools. This project hides the complexity of API structures and enables intuitive management of Airflow clusters through natural language commands.

**Traditional approach (example):**
```bash
curl -X GET "http://localhost:8080/api/v1/dags?limit=100&offset=0" \
  -H "Authorization: Basic YWlyZmxvdzphaXJmbG93"
```

**MCP-Airflow-API approach (natural language):**
> "Show me the currently running DAGs"

---

## QuickStart: Get started in 5 minutes
```bash
git clone https://github.com/call518/MCP-Airflow-API.git
cd MCP-Airflow-API
docker-compose up -d

# Access in your browser
http://localhost:3002
```

---

## 🌟 Key Features

1. **Natural Language Queries**  
   No need to learn complex API syntax. Just ask as you would naturally speak:
   - "What DAGs are currently running?"
   - "Show me the failed tasks"
   - "Find DAGs containing ETL"

2. **Comprehensive Monitoring Capabilities**  
   Real-time cluster status monitoring:
   - Cluster health monitoring
   - DAG status and performance analysis
   - Task execution log tracking
   - XCom data management

3. **43 Powerful MCP Tools**  
   Covers almost all Airflow API functionality:
   - DAG management (trigger, pause, resume)
   - Task instance monitoring
   - Pool and variable management
   - Connection configuration
   - Configuration queries
   - Event log analysis

4. **Large Environment Optimization**  
   Efficiently handles large environments with 1000+ DAGs:
   - Smart pagination support
   - Advanced filtering options
   - Batch processing capabilities

---

## 🛠️ Technical Advantages

- **Leveraging Model Context Protocol (MCP)**  
  MCP is an open standard for secure connections between AI applications and data sources, providing:
  - Standardized interface
  - Secure data access
  - Scalable architecture

- **Support for Two Connection Modes**
  - `stdio` mode: Traditional approach for local environments
  - `streamable-http` mode: Docker-based remote deployment

- **Complete Docker Support**  
  Full Docker Compose setup with 3 separate services:
  - **Open WebUI**: Web interface (port `3002`)
  - **MCP Server**: Airflow API tools (port `8080`)
  - **MCPO Proxy**: REST API endpoint provider (port `8002`)

---

## 🚀 Real Usage Examples

### DAG Management
```python
# List all currently running DAGs
list_dags(limit=50, is_active=True)

# Search for DAGs containing specific keywords
list_dags(id_contains="etl", name_contains="daily")

# Trigger DAG immediately
trigger_dag("my_etl_pipeline")
```

### Task Monitoring
```python
# Query failed task instances
list_task_instances_all(state="failed", limit=20)

# Check logs for specific task
get_task_instance_logs(
    dag_id="my_dag", 
    dag_run_id="run_123", 
    task_id="extract_data"
)
```

### Performance Analysis
```python
# DAG execution time statistics
dag_run_duration("my_etl_pipeline", limit=50)

# Task-level performance analysis
dag_task_duration("my_etl_pipeline", "latest_run")
```

---

## 📊 Real-World Use Cases

![Capacity Management for Operations Teams](img/screenshot-001.png)
---
![Capacity Management for Operations Teams](img/screenshot-002.png)
---
![Capacity Management for Operations Teams](img/screenshot-003.png)
---
![Capacity Management for Operations Teams](img/screenshot-004.png)
---
![Capacity Management for Operations Teams](img/screenshot-005.png)
---
![Capacity Management for Operations Teams](img/screenshot-006.png)
---
![Capacity Management for Operations Teams](img/screenshot-007.png)
---
![Capacity Management for Operations Teams](img/screenshot-008.png)
---
![Capacity Management for Operations Teams](img/screenshot-009.png)
---
![Capacity Management for Operations Teams](img/screenshot-010.png)
---
![Capacity Management for Operations Teams](img/screenshot-011.png)

---

## 🔧 Easy Installation and Setup

### Simple Installation via PyPI
```bash
uvx --python 3.11 mcp-airflow-api
```

### One-Click Deployment with Docker Compose (example)
```yaml
version: '3.8'
services:
  mcp-server:
    build: 
      context: .
      dockerfile: Dockerfile.MCP-Server
    environment:
      - FASTMCP_PORT=8080
      - AIRFLOW_API_URL=http://your-airflow:8080/api/v1
      - AIRFLOW_API_USERNAME=airflow
      - AIRFLOW_API_PASSWORD=your-password
```

### MCP Configuration File (example)
```json
{
  "mcpServers": {
    "airflow-api": {
      "command": "uvx",
      "args": ["--python", "3.11", "mcp-airflow-api"],
      "env": {
        "AIRFLOW_API_URL": "http://localhost:8080/api/v1",
        "AIRFLOW_API_USERNAME": "airflow",
        "AIRFLOW_API_PASSWORD": "airflow"
      }
    }
  }
}
```

---

## 🌈 Future-Ready Architecture

- Scalable design and modular structure for easy addition of new features  
- Standards-compliant protocol for integration with other tools  
- Cloud-native operations and LLM-ready interface  
- Context-aware query processing and automated workflow management capabilities

---

## 🎯 Who Is This Tool For?

- **Data Engineers** — Reduce debugging time, improve productivity, minimize learning curve  
- **DevOps Engineers** — Automate infrastructure monitoring, reduce incident response time  
- **System Administrators** — User-friendly management without complex APIs, real-time cluster status monitoring

---

## 🚀 Open Source Contribution and Community

**Repository:** https://github.com/call518/MCP-Airflow-API

**How to Contribute**
- Bug reports and feature suggestions
- Documentation improvements
- Code contributions

Please consider starring the project if you find it useful.

---

## 🔮 Conclusion

MCP-Airflow-API changes the paradigm of data engineering and workflow management:  
No need to memorize REST API calls — just ask in natural language:

> "Show me the status of currently running ETL jobs."

---

## 🏷️ Tags
`#Apache-Airflow #MCP #ModelContextProtocol #DataEngineering #DevOps #WorkflowAutomation #NaturalLanguage #OpenSource #Python #Docker #AI-Integration`

---

## License
Freely use, modify, and distribute under the **MIT License**.
