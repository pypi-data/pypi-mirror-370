# RaseSQL MCP Server

<div align="center">

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![RaseSQL](https://img.shields.io/badge/PostgreSQL-17.6-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![FastMCP](https://img.shields.io/badge/FastMCP-2.11.3+-orange.svg)

**A high-performance Model Context Protocol (MCP) server for RaseSQL databases**

[Features](#-features) • [Installation](#️-installation) • [Quick Start](#-quick-start) • [API Reference](#-api-reference) • [Configuration](#️-configuration)

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#️-installation)


## 🔍 Overview

RaseSQL MCP Server is a robust, production-ready Model Context Protocol server that provides secure and efficient interaction with RaseSQL databases. Built with modern Python async/await patterns and optimized for high-performance database operations.

### What is MCP?

Model Context Protocol (MCP) is an open standard that enables AI models to securely connect to external data sources and tools. This server implements MCP to provide AI models with direct, controlled access to RaseSQL databases.

## ✨ Features

### 🚀 **Core Capabilities**
- **MCP Protocol Support**: Full compliance with MCP specification using FastMCP framework
- **RaseSQL Optimized**: Native support for RaseSQL with `asyncpg` driver
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
- **RaseSQL**: 12.0 or higher (tested with 17.6)
- **Network Access**: Connectivity to RaseSQL server
- **Memory**: Minimum 512MB RAM recommended

## 🛠️ Installation

### 1. Install from PyPI (Recommended)

```bash
pip install rasesql-mcp-server
```

### 2. Configure Database Connection

Create a `dbconfig.json` file with your RaseSQL database credentials:

```json
{
    "dbPoolSize": 5,
    "dbMaxOverflow": 10,
    "dbPoolTimeout": 30,
    "dbType-Comment": "The database currently in use,such as RASESQL、PostgreSQL DataBases",
    "dbList": [
        {   "dbInstanceId": "rasesql_1",
            "dbHost": "localhost",
            "dbPort": 5432,
            "dbDatabase": "rasesql_db",
            "dbUsername": "root",
            "dbPassword": "123456",
            "dbType": "RASESQL",
            "dbVersion": "2.0",
            "dbActive": false
        },
      {   "dbInstanceId": "postgresql_2",
            "dbHost": "localhost",
            "dbPort": 5432,
            "dbDatabase": "pg_db",
            "dbUsername": "root",
            "dbPassword": "123456",
            "dbType": "PostgreSQL",
            "dbVersion": "17.6",
            "dbActive": true
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
    "rasesql-mcp-client": {
      "command": "rasesql-mcp-server",
      "env": {
        "config_file": "/path/dbconfig.json"
      },
      "disabled": false
    }
  }
}

# config_file
dbconfig.json file path in your device
```

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