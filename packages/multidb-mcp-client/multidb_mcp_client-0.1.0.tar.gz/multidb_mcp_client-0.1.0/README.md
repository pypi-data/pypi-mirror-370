# Multi-Database MCP Client

A Model Context Protocol (MCP) server that enables secure interaction with multiple database types including MySQL, MariaDB, TiDB, OceanBase, and AWS RDS/Aurora MySQL. This server exposes database operations as MCP tools and resources while proxying actual SQL execution to a remote HTTP service.

## 🚀 Features

- **Universal SQL Execution**: Execute any SQL statement (SELECT, INSERT, UPDATE, DELETE, DDL) through a single tool
- **Multi-Database Support**: Works with MySQL, MariaDB, TiDB, OceanBase, and compatible cloud databases
- **HTTP Proxy Architecture**: Decouples MCP interface from database connections via HTTP forwarding
- **Schema Introspection**: Get table structures and database metadata as MCP resources
- **Test Data Generation**: Built-in tool for generating development test data
- **Flexible Configuration**: Support for multiple database instances with runtime switching
- **Async I/O**: Full asynchronous operation using `aiohttp` and `asyncio`
- **Structured Logging**: Comprehensive logging with `loguru` to both stderr and rotating files

## 🏗️ Architecture

The system follows a proxy pattern where the MCP server acts as a client-side interface:

```
MCP Client → FastMCP Tools/Resources → HTTP POST → Remote DB Server → Database
```

### Key Components

- **`src/server.py`**: MCP server with FastMCP framework, tool/resource definitions
- **`src/utils/db_operate.py`**: HTTP-proxied SQL execution engine
- **`src/utils/db_config.py`**: Singleton configuration loader with multi-instance support
- **`src/resources/db_resources.py`**: Database metadata and configuration resource builders
- **`src/tools/db_tool.py`**: Test data generation utilities
- **`src/utils/http_util.py`**: Async HTTP client helpers
- **`src/utils/logger_util.py`**: Logging setup and configuration path resolution

## 📋 Requirements

- Python 3.12+
- A remote database server accessible via the configured `multiDBServer` endpoint

## 🔧 Installation

```bash
# Clone the repository
git clone https://github.com/j00131120/mcp_database_server.git
cd mcp_database_server/multidb_mcp_client

# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -U pip
pip install -e .
```

## ⚙️ Configuration

### Configuration File

The server reads configuration from `dbconfig.json` (default) or a custom path via the `config_file` environment variable:

```bash
export config_file="/absolute/path/to/your/dbconfig.json"
```

### Example Configuration

```json
{
  "dbType-Comment": "Supported types: mysql, xesql, ubisql, rasesql, oceanbase, tidb",
  "dbList": [
    {
      "dbInstanceId": "primary_oceanbase",
      "dbHost": "localhost",
      "dbPort": 2281,
      "dbDatabase": "production_db",
      "dbUsername": "app_user",
      "dbPassword": "secure_password",
      "dbType": "OceanBase",
      "dbVersion": "V4.0.0",
      "dbActive": true
    },
    {
      "dbInstanceId": "backup_mysql",
      "dbHost": "backup.example.com",
      "dbPort": 3306,
      "dbDatabase": "backup_db",
      "dbUsername": "backup_user",
      "dbPassword": "backup_password",
      "dbType": "MySQL",
      "dbVersion": "8.0",
      "dbActive": false
    }
  ],
  "multiDBServer": "http://127.0.0.1:8080/mcp/executeQuery",
  "logPath": "/var/log/mcp-client",
  "logLevel": "INFO"
}
```

### Configuration Properties

- **`dbList`**: Array of database instance configurations
  - **`dbActive`**: Exactly one instance must be `true` (the active database)
  - **`dbType`**: Supported values include MySQL, OceanBase, TiDB, etc.
- **`multiDBServer`**: HTTP endpoint that accepts SQL execution requests
- **`logPath`**: Directory for log files (auto-creates if missing)
- **`logLevel`**: One of TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL

### Remote Server Contract

The `multiDBServer` endpoint must accept POST requests with this payload:

```json
{
  "sql": "SELECT * FROM users WHERE id = ?",
  "params": [123],
  "databaseInstance": {
    "dbInstanceId": "primary_oceanbase",
    "dbHost": "localhost",
    "dbPort": 2281,
    "dbDatabase": "production_db",
    "dbUsername": "app_user",
    "dbPassword": "secure_password",
    "dbType": "OceanBase",
    "dbActive": true
  }
}
```

And return responses like:

```json
{
  "result": [
    {"id": 123, "name": "John Doe", "email": "john@example.com"}
  ]
}
```

## 🚀 Running the Server

### Command Line

After installation, use the provided CLI command:

```bash
multidb-mcp-client
```

This starts the MCP server over stdio for consumption by MCP-compatible clients.

### FastMCP CLI (Alternative)

```bash
# List available MCP servers
fastmcp servers list

# Run via entry point (defined in pyproject.toml)
fastmcp run mysql
```

### Environment Variables

- **`config_file`**: Override default config file path
- Standard logging environment variables supported by `loguru`

## 🛠️ MCP Tools

### `sql_exec(sql: str)`

Execute any SQL statement with automatic transaction handling.

**Parameters:**
- `sql` (string): SQL statement to execute

**Returns:**
```json
{
  "success": true,
  "result": [...],  // Query results or affected row count
  "message": "SQL executed successfully"
}
```

**Usage Examples:**
```python
# Query data
await sql_exec("SELECT * FROM users WHERE age > 18")

# Insert data
await sql_exec("INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com')")

# Update records
await sql_exec("UPDATE users SET email = 'newemail@example.com' WHERE id = 1")

# DDL operations
await sql_exec("CREATE TABLE products (id INT PRIMARY KEY, name VARCHAR(100))")
```

### `describe_table(table_name: str)`

Get detailed table structure information.

**Parameters:**
- `table_name` (string): Name of the table (supports `database.table` format)

**Returns:**
Same format as `sql_exec`, with `result` containing column metadata.

**Usage Examples:**
```python
await describe_table("users")
await describe_table("inventory.products")
```

### `generate_demo_data(table_name: str, columns_name: List[str], num: int)`

Generate test data for development and testing.

**Parameters:**
- `table_name` (string): Target table name
- `columns_name` (array): List of column names to populate
- `num` (integer): Number of test records to generate

**Usage Examples:**
```python
# Generate 100 test users
await generate_demo_data("users", ["name", "email", "phone"], 100)

# Generate 50 test products
await generate_demo_data("products", ["product_name", "category", "description"], 50)
```

## 📊 MCP Resources

### `database://tables`

Provides comprehensive metadata for all database tables.

**Returns:**
```json
{
  "uri": "database://tables",
  "mimeType": "application/json",
  "text": "[{\"name\": \"users\", \"columns\": [...], \"record_count\": 1250}, ...]"
}
```

**Use Cases:**
- Schema exploration and documentation
- Database monitoring and statistics
- Query planning and optimization

### `database://config`

Provides current database configuration (with sensitive data masked).

**Returns:**
```json
{
  "uri": "database://config", 
  "mimeType": "application/json",
  "text": "{\"dbInstanceId\": \"primary_oceanbase\", \"dbHost\": \"localhost\", \"dbPassword\": \"***hidden***\", ...}"
}
```

## 📝 Logging

The system provides comprehensive logging:

- **Console Output**: Logs to stderr for MCP client visibility
- **File Logging**: Rotating log files (10MB max, 7-day retention)
- **Structured Format**: Timestamp, level, function, line number, and message
- **Configurable Levels**: TRACE through CRITICAL

Log files are stored in:
- Configured `logPath` directory
- Default: `<project_root>/logs/mcp_server.log`

## 🔒 Security Considerations

### Current Security Features

- **Password Masking**: Sensitive data hidden in resource responses
- **HTTP Client**: Supports custom headers for authentication
- **Configuration Isolation**: Only active database config exposed

### Security Recommendations

1. **Credential Management**: Store database passwords in environment variables or secure vaults
2. **Network Security**: Use HTTPS for `multiDBServer` endpoint with proper authentication
3. **Access Control**: Restrict `sql_exec` tool usage to trusted environments
4. **File Permissions**: Secure `dbconfig.json` with appropriate file system permissions
5. **Network Isolation**: Deploy `multiDBServer` in a secured network segment

### Production Deployment

```bash
# Use environment variables for sensitive data
export DB_PASSWORD="your_secure_password"
export MULTIDB_SERVER_URL="https://secure-db-proxy.internal.com/api/v1/execute"

# Restrict config file permissions
chmod 600 dbconfig.json

# Run with non-root user
useradd -r mcp-client
sudo -u mcp-client multidb-mcp-client
```

## 🧪 Development

### Project Structure

```
multidb_mcp_client/
├── src/
│   ├── server.py              # MCP server and tool definitions
│   ├── resources/
│   │   └── db_resources.py    # Resource data builders
│   ├── tools/
│   │   └── db_tool.py         # Tool implementations
│   └── utils/
│       ├── db_config.py       # Configuration management
│       ├── db_operate.py      # SQL execution via HTTP
│       ├── http_util.py       # HTTP client utilities
│       └── logger_util.py     # Logging configuration
├── dbconfig.json              # Database configuration
├── pyproject.toml             # Project metadata and dependencies
└── logs/                      # Log output directory
```

### Code Style

- **Explicit naming**: Clear, descriptive function and variable names
- **Early returns**: Reduce nesting with guard clauses
- **Type annotations**: Public APIs include type hints
- **Error handling**: Comprehensive exception handling with logging
- **Async/await**: Proper async patterns throughout

### Key Dependencies

- **`fastmcp`**: MCP framework and protocol implementation
- **`aiohttp`**: Async HTTP client for database proxy calls
- **`loguru`**: Structured logging with rotation and formatting
- **`mcp[cli]`**: MCP command-line tools

## 📄 License

MIT License - see the LICENSE file for details.

## 🔗 Links

- **Homepage**: https://github.com/j00131120/mcp_database_server/tree/main/multidb_mcp_client
- **Documentation**: https://github.com/j00131120/mcp_database_server/blob/main/multidb_mcp_client/README.md
- **Source Code**: https://github.com/j00131120/mcp_database_server.git
- **Issue Tracker**: https://github.com/j00131120/mcp_database_server/issues
- **Changelog**: https://github.com/j00131120/mcp_database_server/blob/main/multidb_mcp_client/CHANGELOG.md

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📞 Support

For questions, issues, or contributions:

- **Author**: Frank Jin (j00131120@163.com)
- **GitHub Issues**: Use the issue tracker for bug reports and feature requests
- **Documentation**: Check the repository wiki for additional documentation

---

**Note**: This MCP server requires a compatible remote database service running at the configured `multiDBServer` endpoint. Ensure your remote service implements the expected HTTP API contract before running the client.
