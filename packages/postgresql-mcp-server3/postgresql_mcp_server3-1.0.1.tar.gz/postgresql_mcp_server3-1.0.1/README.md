# PostgreSQL MCP Server

<div align="center">

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17.6-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![FastMCP](https://img.shields.io/badge/FastMCP-2.11.3+-orange.svg)

**A high-performance Model Context Protocol (MCP) server for PostgreSQL databases**

[Features](#-features) • [Installation](#️-installation) • [Quick Start](#-quick-start) • [API Reference](#-api-reference) • [Configuration](#️-configuration)

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#️-installation)
- [Quick Start](#-quick-start)
- [API Reference](#-api-reference)
- [Configuration](#️-configuration)
- [Architecture](#️-architecture)
- [Security](#-security)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## 🔍 Overview

PostgreSQL MCP Server is a robust, production-ready Model Context Protocol server that provides secure and efficient interaction with PostgreSQL databases. Built with modern Python async/await patterns and optimized for high-performance database operations.

### What is MCP?

Model Context Protocol (MCP) is an open standard that enables AI models to securely connect to external data sources and tools. This server implements MCP to provide AI models with direct, controlled access to PostgreSQL databases.

## ✨ Features

### 🚀 **Core Capabilities**
- **MCP Protocol Support**: Full compliance with MCP specification using FastMCP framework
- **PostgreSQL Optimized**: Native support for PostgreSQL with `asyncpg` driver
- **Asynchronous Architecture**: High-performance async/await implementation
- **Connection Pooling**: Intelligent connection management with configurable pool settings

### 🔧 **Database Operations**
- **Universal SQL Execution**: Support for SELECT, INSERT, UPDATE, DELETE, DDL operations
- **Table Structure Queries**: Detailed schema information retrieval
- **Test Data Generation**: Built-in tools for generating sample data
- **Parameterized Queries**: Safe parameter binding to prevent SQL injection

### 🛡️ **Security & Safety**
- **Query Type Restrictions**: Configurable query execution controls
- **Parameter Validation**: Comprehensive input validation
- **Password Protection**: Secure credential handling
- **Connection Isolation**: Instance-based access control

### 📊 **Monitoring & Logging**
- **Structured Logging**: Detailed operation logs with configurable levels
- **Connection Pool Monitoring**: Real-time pool status tracking
- **Error Handling**: Comprehensive error reporting and recovery

## 📋 Prerequisites

- **Python**: 3.12 or higher
- **PostgreSQL**: 12.0 or higher (tested with 17.6)
- **Network Access**: Connectivity to PostgreSQL server
- **Memory**: Minimum 512MB RAM recommended

## 🛠️ Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install postgresql-mcp-server3
```

### Option 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/j00131120/mcp_database_server.git
cd mcp_database_server/postgresql_mcp_server

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Option 3: Using UV (Fast Python Package Manager)

```bash
uv add postgresql-mcp-server3
```

## 🚀 Quick Start

### 1. Configure Database Connection

Create a `dbconfig.json` file with your PostgreSQL database credentials:

```json
{
    "dbPoolSize": 5,
    "dbMaxOverflow": 10,
    "dbPoolTimeout": 30,
    "dbList": [
        {
            "dbInstanceId": "postgresql_main",
            "dbHost": "localhost",
            "dbPort": 5432,
            "dbDatabase": "pg_db",
            "dbUsername": "root",
            "dbPassword": "123456",
            "dbType": "PostgreSQL",
            "dbVersion": "17.6",
            "dbActive": true
        },
        {   "dbInstanceId": "rasesql_2",
            "dbHost": "localhost",
            "dbPort": 5432,
            "dbDatabase": "rasesql_db",
            "dbUsername": "root",
            "dbPassword": "123456",
            "dbType": "RaseSQL",
            "dbVersion": "2.0",
            "dbActive": false
        }
    ],
    "logPath": "/path/to/logs",
    "logLevel": "info"
}
# dbActive
Only database instances with dbActive set to true in the dbList configuration list are available. 
# logPath
Mcp server log is stored in /path/to/logs/mcp_server.log.
# logLevel
TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL
# dbActive
Only database instances with dbActive set to true in the dbList configuration list are available. 
# logPath
Mcp server log is stored in /Volumes/store/mysql_mcp_server/logs/mcp_server.log.
# logLevel
TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL
```

### 3. Configure mcp json

```bash
{
  "mcpServers": {
    "postgresql-mcp-client": {
      "command": "postgresql-mcp-server3",
      "env": {
        "config_file": "/Users/frank/store/dbconfig.json"
      },
      "disabled": false
    }
  }
}

# config_file
dbconfig.json file path in your device
```

### 4. Clone the repository
```bash
git clone <repository-url>
cd mysql_mcp_server
import current project into your IDE Tool

```

### 5. Configure mcp json By IDE Tool
```bash
{
  "mcpServers": {
    "postgresql-mcp-client": {
      "command": "/bin/uv",
      "args": ["run", "src/server.py"],
      "cwd": "/path/to/your/project",
      "env": {
        "config_file": "/path/to/your/dbconfig.json"
      },
      "disabled": false,
      "autoApprove": ["describe_table", "sql_exec", "generate_demo_data"]
    }
  }
}

# command
uv absolute path
# cwd
project absolute path
# config_file
dbconfig.json file path
```

### 3. Start the Server

#### Using Installed Package
```bash
postgresql-mcp-server3
```

#### Using FastMCP CLI
```bash
fastmcp run src/server.py
```

#### Direct Python Execution
```bash
python src/server.py
```

#### Development Mode with UV
```bash
uv run src/server.py
```

#### Using fastmcp debug
```bash
fastmcp dev src/server.py
```
### 4. Verify Installation

```bash
# Test connection
python -c "
import asyncio
from src.utils.db_config import load_activate_db_config
try:
    active_db, config = load_activate_db_config()
    print('✅ Configuration loaded successfully')
    print(f'Database: {active_db.db_type} {active_db.db_version}')
except Exception as e:
    print(f'❌ Configuration error: {e}')
"
```

## 📚 API Reference

### MCP Tools

#### `sql_exec(sql: str)`

Execute any SQL statement with automatic result formatting.

**Parameters:**
- `sql` (str): SQL statement to execute

**Returns:**
```json
{
    "success": true,
    "result": [...],  // Query results or affected row count
    "message": "SQL executed successfully"
}
```

**Examples:**
```sql
-- Query data
SELECT * FROM users WHERE age > 18 LIMIT 10;

-- Insert data
INSERT INTO users (name, email) VALUES ('John Doe', 'john@example.com');

-- Update data
UPDATE users SET last_login = NOW() WHERE id = 1;

-- DDL operations
CREATE TABLE products (id SERIAL PRIMARY KEY, name VARCHAR(255));
```

#### `describe_table(table_name: str)`

Get detailed table structure information.

**Parameters:**
- `table_name` (str): Table name (supports `schema.table` format)

**Returns:**
- Detailed column information including types, constraints, and defaults

**Examples:**
```python
# Describe table in public schema
describe_table("users")

# Describe table in specific schema
describe_table("inventory.products")
```

#### `generate_demo_data(table_name: str, columns_name: List[str], num: int)`

Generate test data for development and testing.

**Parameters:**
- `table_name` (str): Target table name
- `columns_name` (List[str]): Column names to populate
- `num` (int): Number of test records to generate

**Example:**
```python
generate_demo_data("users", ["name", "email", "phone"], 100)
```

### MCP Resources

#### `database://tables`

Provides metadata for all database tables including:
- Table names and schemas
- Column definitions and types
- Primary keys and constraints
- Row counts

#### `database://config`

Returns current database configuration (sensitive data masked):
- Connection parameters
- Pool settings
- Database version information

## ⚙️ Configuration

### Database Configuration (`dbconfig.json`)

```json
{
    "dbPoolSize": 5,              // Minimum connection pool size
    "dbMaxOverflow": 10,          // Maximum additional connections
    "dbPoolTimeout": 30,          // Connection timeout in seconds
    "dbList": [
        {
            "dbInstanceId": "unique_identifier",
            "dbHost": "localhost",
            "dbPort": 5432,
            "dbDatabase": "database_name",
            "dbUsername": "username",
            "dbPassword": "password",
            "dbType": "PostgreSQL",
            "dbVersion": "17.6",
            "dbActive": true          // Only one instance should be active
        }
    ],
    "logPath": "/path/to/logs",   // Log file directory
    "logLevel": "info"            // TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL
}
```

### Environment Variables

- `config_file`: Override default configuration file path
- `LOG_LEVEL`: Override log level from configuration

### MCP Client Configuration Examples

#### Claude Desktop
```json
{
  "mcpServers": {
    "postgresql": {
      "command": "postgresql-mcp-server3",
      "env": {
        "config_file": "/Users/yourusername/dbconfig.json"
      }
    }
  }
}
```

#### Development with UV
```json
{
  "mcpServers": {
    "postgresql-dev": {
      "command": "uv",
      "args": ["run", "src/server.py"],
      "cwd": "/path/to/postgresql_mcp_server",
      "env": {
        "config_file": "/path/to/dbconfig.json"
      }
    }
  }
}
```

## 🏗️ Architecture

### Project Structure
```
postgresql_mcp_server/
├── src/
│   ├── server.py              # MCP server entry point
│   ├── utils/                 # Core utilities
│   │   ├── db_config.py      # Configuration management
│   │   ├── db_pool.py        # Connection pool
│   │   ├── db_operate.py     # Database operations
│   │   ├── logger_util.py    # Logging utilities
│   │   └── __init__.py       # Module exports
│   ├── resources/            # MCP resources
│   │   └── db_resources.py   # Database metadata resources
│   └── tools/                # MCP tools
│       └── db_tool.py        # Database operation tools
├── dbconfig.json             # Database configuration
├── pyproject.toml           # Package configuration
├── requirements.txt         # Dependencies
└── README.md               # Documentation
```

### Key Components

#### 🔗 **Connection Pool Management**
- **Singleton Pattern**: Single pool instance per application
- **Async Operations**: Non-blocking connection handling
- **Health Monitoring**: Automatic connection validation
- **Resource Cleanup**: Proper connection lifecycle management

#### ⚙️ **Configuration System**
- **JSON-based**: Human-readable configuration
- **Environment Override**: Flexible deployment options
- **Validation**: Comprehensive configuration validation
- **Hot Reload**: Configuration updates without restart

#### 📝 **Logging Framework**
- **Structured Logging**: JSON-formatted log entries
- **Multiple Outputs**: Console and file logging
- **Log Rotation**: Automatic log file management
- **Debug Support**: Detailed operation tracing

## 🛡️ Security

### Connection Security
- **Parameterized Queries**: Automatic SQL injection prevention
- **Connection Encryption**: SSL/TLS support for database connections
- **Credential Protection**: Secure password handling and masking
- **Access Control**: Instance-based permission management

### Query Safety
- **SQL Validation**: Query type verification
- **Result Limiting**: Automatic row count restrictions
- **Parameter Sanitization**: Input validation and cleaning
- **Error Handling**: Secure error message formatting

### Configuration Security
- **Environment Variables**: Secure credential management
- **File Permissions**: Proper configuration file protection
- **Network Security**: Firewall and access control recommendations

## 🧪 Testing

### Connection Testing
```bash
# Test database connectivity
python -c "
import asyncio
from src.utils.db_pool import get_db_pool

async def test():
    pool = await get_db_pool()
    conn = await pool.get_connection()
    result = await conn.fetchval('SELECT version()')
    print(f'Connected to: {result[:50]}...')
    await pool.release_connection(conn)

asyncio.run(test())
"
```

### SQL Execution Testing
```python
# Test SQL execution
from src.tools.db_tool import sql_exec

result = await sql_exec("SELECT current_timestamp as now")
print(result)
```

### Load Testing
```python
# Test concurrent connections
import asyncio
from src.utils.db_operate import execute_sql

async def load_test():
    tasks = []
    for i in range(10):
        task = execute_sql(f"SELECT {i} as test_id, pg_sleep(0.1)")
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    print(f"Completed {len(results)} concurrent queries")

asyncio.run(load_test())
```

## 🚨 Troubleshooting

### Common Issues

#### Connection Errors
```bash
# Check PostgreSQL connectivity
psql -h localhost -p 5432 -U username -d database_name

# Test configuration
python -c "
from src.utils.db_config import load_activate_db_config
try:
    db, config = load_activate_db_config()
    print('✅ Configuration valid')
except Exception as e:
    print(f'❌ Configuration error: {e}')
"
```

#### Permission Issues
- Ensure PostgreSQL user has necessary privileges:
  ```sql
  GRANT CONNECT ON DATABASE your_db TO your_user;
  GRANT USAGE ON SCHEMA public TO your_user;
  GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO your_user;
  ```
- Check firewall settings and network connectivity
- Verify PostgreSQL server is running and accepting connections

#### Configuration Problems
- Validate JSON syntax in `dbconfig.json`
- Check file permissions and paths
- Verify environment variables
- Review log files for detailed error messages

### Debug Mode

Enable detailed logging:
```json
{
    "logLevel": "debug"
}
```

Or set environment variable:
```bash
export LOG_LEVEL=debug
python src/server.py
```

### Log Analysis
```bash
# View recent logs
tail -f /path/to/logs/mcp_server.log

# Search for errors
grep -i error /path/to/logs/mcp_server.log

# Monitor connection pool
grep -i "connection pool" /path/to/logs/mcp_server.log
```

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Getting Started
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

### Development Setup
```bash
# Clone and setup
git clone https://github.com/j00131120/mcp_database_server.git
cd mcp_database_server/postgresql_mcp_server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev,test]"

# Install pre-commit hooks
pre-commit install
```

### Code Quality
```bash
# Format code
black src/
isort src/

# Lint code
flake8 src/
mypy src/

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest --cov=src --cov-report=html
```

### Pull Request Guidelines
- Write clear, descriptive commit messages
- Include tests for new features
- Update documentation as needed
- Ensure all tests pass
- Follow existing code style and conventions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors & Contributors

- **Frank Jin** - *Initial development* - [j00131120@163.com](mailto:j00131120@163.com)

## 🙏 Acknowledgments

- [FastMCP](https://github.com/fastmcp/fastmcp) - MCP framework foundation
- [asyncpg](https://github.com/MagicStack/asyncpg) - High-performance PostgreSQL driver
- [loguru](https://github.com/Delgan/loguru) - Modern logging library
- [PostgreSQL](https://www.postgresql.org/) - World's most advanced open source database

## 📞 Support

### Getting Help
- 📖 **Documentation**: Check this README and inline code documentation
- 🐛 **Bug Reports**: [Create an issue](https://github.com/j00131120/mcp_database_server/issues)
- 💬 **Questions**: Contact [j00131120@163.com](mailto:j00131120@163.com)
- 💡 **Feature Requests**: [Submit an enhancement request](https://github.com/j00131120/mcp_database_server/issues)

### Community
- Star ⭐ this repository if you find it useful
- Share with colleagues working with PostgreSQL and AI
- Contribute improvements and bug fixes

---

<div align="center">

**Made with ❤️ for the PostgreSQL and AI community**

[⬆ Back to Top](#postgresql-mcp-server)

</div>