# Redis MCP Server

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://python.org)
[![Redis Version](https://img.shields.io/badge/redis-5.0%2B-red.svg)](https://redis.io)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.11.3%2B-green.svg)](https://github.com/fastmcp/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Model Context Protocol (MCP) server that enables secure, efficient interaction with Redis databases through AI assistants and applications.

## 🚀 Features

- **🔌 MCP Protocol Support**: Built on FastMCP framework with standard MCP tools and resources
- **🗄️ Redis Compatibility**: Support for Redis single, master-slave, and cluster deployments
- **⚡ Asynchronous Architecture**: Built with `redis.asyncio` and `hiredis` for high-performance operations
- **🔗 Connection Pooling**: Efficient connection management with configurable pool settings
- **🔒 Security Features**: Password protection, SSL support, and connection validation
- **🛠️ Comprehensive Tools**: Redis command execution, monitoring, and data management
- **📊 Monitoring & Analytics**: Server info, memory usage, client connections, and key statistics
- **🔧 Flexible Configuration**: JSON-based configuration with multiple instance support
- **📝 Detailed Logging**: Structured logging with configurable levels and file rotation
- **🐳 Production Ready**: Health checks, error handling, and graceful connection management

## 📋 Prerequisites

- **Python**: >= 3.12
- **Redis**: >= 5.0.0
- **Network Access**: To Redis server instance(s)

## 🛠️ Installation

### 1. Install from PyPI (Recommended)
```bash
pip install redis-mcp-server3
```

### 2. Configure database connection

Edit `dbconfig.json` with your database credentials:

```json
{
  "redisEncoding": "utf-8",
  "redisPoolSize": 5,
  "redisMaxConnections": 10,
  "redisConnectionTimeout": 30,
  "socketTimeout": 30,
  "retryOnTimeout": true,
  "healthCheckInterval": 30,
  "redisType-Comment": "single 单机模式、masterslave 主从模式、cluster 集群模式",
  "redisList": [
    {
      "redisInstanceId": "redis-local-single",
      "redisType": "single",
      "redisHost": "localhost",
      "redisPort": 6379,
      "redisDatabase": 0,
      "redisPassword": 123456,
      "dbActive": true
    },
    {
      "redisInstanceId": "redis-ms-single",
      "redisType": "masterslave",
      "redisHost": "localhost",
      "redisPort": 6379,
      "redisDatabase": 0,
      "redisPassword": 123456,
      "dbActive": false
    },
    {
      "redisInstanceId": "redis-cluster-single",
      "redisType": "cluster",
      "redisHost": "localhost",
      "redisPort": 6379,
      "redisDatabase": 0,
      "redisPassword": 123456,
      "dbActive": false
    }
  ],
  "logPath": "/path/to/logs",
  "logLevel": "info"
}
# redisType
Redis Instance is in single、masterslave、cluster mode.
# dbActive
Only database instances with dbActive set to true in the dbList configuration list are available. 
# logPath
MCP server log is stored in /path/to/logs/mcp_server.log.
# logLevel
TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL
```

### 3. Configure MCP Client

Add to your MCP client configuration file:

```json
{
  "mcpServers": {
    "oceanbase-mcp-client": {
      "command": "redis-mcp-server3",
      "env": {
        "config_file": "/path/to/your/dbconfig.json"
      },
      "disabled": false
    }
  }
}
```

**Note**: Replace `/path/to/your/dbconfig.json` with the actual path to your configuration file.

### 4. Clone the repository (Development Mode)
```bash
git clone https://github.com/j00131120/mcp_database_server.git
cd mcp_database_server/redis_mcp_server
# Import project into your IDE
```

### 5. Configure MCP Client for Development
```json
{
  "mcpServers": {
    "redis-mcp-client": {
      "command": "/bin/uv",
      "args": ["run", "src/server.py"],
      "cwd": "/path/to/your/project",
      "env": {
        "config_file": "/path/to/your/dbconfig.json"
      },
      "disabled": false
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

## 🚀 Quick Start

### 1. Start the MCP Server

```bash
# Using installed package
redis-mcp-server3

# Using FastMCP CLI
fastmcp run src/server.py

# Direct Python execution
python src/server.py

# Using fastmcp debug
fastmcp dev src/server.py
```

### 2. Basic Usage Examples

```python
# Execute Redis commands
await redis_exec("SET", ["user:1001", "John Doe"])
await redis_exec("GET", ["user:1001"])

# Hash operations
await redis_exec("HSET", ["user:1001:profile", "name", "John", "age", "30"])
await redis_exec("HGETALL", ["user:1001:profile"])

# List operations
await redis_exec("LPUSH", ["tasks", "task1", "task2"])
await redis_exec("LRANGE", ["tasks", "0", "-1"])

# Get server information
server_info = await get_server_info()
memory_info = await get_memory_info()
```

## 📚 API Reference

### MCP Tools

#### `redis_exec(command: str, args: list = None)`
Execute any Redis command with arguments.

**Parameters:**
- `command` (str): Redis command name (e.g., 'GET', 'SET', 'HGET')
- `args` (list, optional): Command arguments

**Returns:**
- `dict`: Execution result with success status and data

**Examples:**
```python
# String operations
await redis_exec("SET", ["key1", "value1"])
await redis_exec("GET", ["key1"])
await redis_exec("SETEX", ["key2", "60", "temp_value"])

# Hash operations  
await redis_exec("HSET", ["hash1", "field1", "value1"])
await redis_exec("HGETALL", ["hash1"])

# List operations
await redis_exec("LPUSH", ["list1", "item1", "item2"])
await redis_exec("LRANGE", ["list1", "0", "-1"])

# Set operations
await redis_exec("SADD", ["set1", "member1", "member2"])
await redis_exec("SMEMBERS", ["set1"])
```

#### `gen_test_data(table: str, columns: list, num: int = 10)`
Generate test data for Redis hash structures.

**Parameters:**
- `table` (str): Table/prefix name for the keys
- `columns` (list): Field names to populate
- `num` (int): Number of test records to generate

#### `get_server_info()`
Get Redis server basic information.

**Returns:**
- Server version, mode, OS, architecture, uptime

#### `get_memory_info()`
Get Redis memory usage statistics.

**Returns:**
- Memory usage, peak usage, RSS memory, max memory settings

#### `get_clients_info()`
Get Redis client connection information.

**Returns:**
- Connected clients count, input/output buffer sizes

#### `get_stats_info()`
Get Redis operation statistics.

**Returns:**
- Total connections, commands processed, keyspace hits/misses

#### `get_db_info()`
Get Redis database information.

**Returns:**
- Database size, keyspace information

#### `get_keys_info()`
Get sample key information (first 10 keys).

**Returns:**
- Total key count, sample keys with types and TTL

#### `get_key_types()`
Get key type distribution statistics.

**Returns:**
- Distribution of different key types (string, hash, list, set, zset)

#### `get_redis_config()`
Get Redis configuration information.

**Returns:**
- Important Redis configuration parameters

#### `get_redis_overview()`
Get comprehensive Redis overview (all monitoring information).

**Returns:**
- Complete system overview including all above information

### MCP Resources

#### `database://config`
Database configuration information (sensitive data hidden).

**Returns:**
- Safe configuration details without passwords

#### `database://status`
Database connection status and health check results.

**Returns:**
- Connection status, ping results, basic operations test

## 🏗️ Architecture

### Project Structure
```
redis_mcp_server/
├── src/
│   ├── __init__.py              # Package metadata and API
│   ├── server.py                # Main MCP server entry point
│   ├── utils/                   # Utility modules
│   │   ├── __init__.py          # Utility exports
│   │   ├── db_config.py         # Configuration management
│   │   ├── db_pool.py           # Connection pool management
│   │   ├── db_operate.py        # Redis operations wrapper
│   │   └── logger_util.py       # Logging configuration
│   ├── resources/               # MCP resources
│   │   └── db_resources.py      # Database resources provider
│   └── tools/                   # MCP tools
│       └── db_tool.py           # Redis management tools
├── dbconfig.json               # Database configuration
├── pyproject.toml              # Project configuration
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

### Key Components

#### Connection Pool Manager
- **Singleton Pattern**: Single pool instance per application
- **Async Management**: Non-blocking connection handling  
- **Health Monitoring**: Automatic connection validation
- **Resource Cleanup**: Proper connection release

#### Configuration System
- **JSON-based**: Human-readable configuration
- **Environment Override**: Flexible deployment options
- **Multi-instance**: Support for multiple Redis instances
- **Validation**: Comprehensive error checking

#### Logging System
- **Structured Logging**: JSON-formatted log entries
- **File Rotation**: Automatic log file management
- **Configurable Levels**: TRACE to CRITICAL
- **Performance Optimized**: Asynchronous logging

## 🔧 Advanced Configuration

### SSL/TLS Configuration

For secure connections, configure SSL in your `dbconfig.json`:

```json
{
  "redisList": [
    {
      "redisInstanceId": "secure-redis",
      "redisHost": "secure.redis.example.com",
      "redisPort": 6380,
      "redisSsl": true,
      "redisPassword": "secure_password",
      "dbActive": true
    }
  ]
}
```

### Cluster Configuration

For Redis cluster deployments:

```json
{
  "redisList": [
    {
      "redisInstanceId": "redis-cluster",
      "redisType": "cluster",
      "redisHost": "cluster-node1.example.com",
      "redisPort": 7000,
      "redisPassword": "cluster_password",
      "dbActive": true
    }
  ]
}
```

### Performance Tuning

Optimize for high-throughput scenarios:

```json
{
  "redisPoolSize": 20,
  "redisMaxConnections": 50,
  "redisConnectionTimeout": 10,
  "socketTimeout": 5,
  "healthCheckInterval": 60
}
```

## 🧪 Testing

### Basic Connection Test

```python
# Test Redis connection
status = await get_connection_status()
print(status)  # {'ping': True, 'set_get': 'ok'}
```

### Performance Testing

```python
# Generate test data
await gen_test_data("users", ["name", "email", "age"], 1000)

# Check database size
db_info = await get_db_info()
print(f"Total keys: {db_info['dbsize']}")
```

## 📊 Monitoring

### Health Checks

The server provides built-in health monitoring:

```python
# Get comprehensive overview
overview = await get_redis_overview()

# Check specific metrics
memory = await get_memory_info()
if memory['used_memory'] > threshold:
    # Handle high memory usage
    pass
```

### Log Analysis

Monitor server logs for performance and errors:

```bash
# View real-time logs
tail -f /var/log/redis_mcp_server/logs/mcp_server.log

# Search for errors
grep "ERROR" /var/log/redis_mcp_server/logs/mcp_server.log
```

## 🚨 Troubleshooting

### Common Issues

#### Connection Errors

**Problem**: `ConnectionError: Connection refused`

**Solution**:
```bash
# Check Redis server status
redis-cli ping

# Verify Redis is running
systemctl status redis

# Check network connectivity
telnet localhost 6379
```

#### Authentication Errors

**Problem**: `AuthenticationError: Auth failed`

**Solutions**:
- Verify password in `dbconfig.json`
- Check Redis AUTH configuration
- Ensure user has proper permissions

#### Memory Issues

**Problem**: High memory usage or OOM errors

**Solutions**:
- Monitor with `get_memory_info()`
- Adjust `maxmemory` policy
- Implement key expiration
- Use Redis memory optimization techniques

#### Performance Issues

**Problem**: Slow response times

**Solutions**:
- Increase connection pool size
- Reduce connection timeout
- Monitor with `get_stats_info()`
- Check network latency

### Debug Mode

Enable debug logging:

```json
{
  "logLevel": "debug"
}
```

### Diagnostic Commands

```python
# Check server health
server_info = await get_server_info()
clients_info = await get_clients_info()
stats_info = await get_stats_info()

# Analyze key distribution
key_types = await get_key_types()
keys_sample = await get_keys_info()
```

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Development Setup

```bash
# Clone the repository
git clone https://github.com/j00131120/mcp_database_server.git
cd mcp_database_server/redis_mcp_server

# Install development dependencies
pip install -e ".[dev,test,docs]"

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
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html
```

### Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Add docstrings for public methods
- Write comprehensive tests
- Update documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Frank Jin** - *Initial work* - [j00131120@163.com](mailto:j00131120@163.com)

## 🙏 Acknowledgments

- [FastMCP](https://github.com/fastmcp/fastmcp) - MCP framework foundation
- [redis-py](https://github.com/redis/redis-py) - Python Redis client
- [Loguru](https://github.com/Delgan/loguru) - Structured logging library
- [Redis](https://redis.io/) - In-memory data structure store

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/j00131120/mcp_database_server/issues)
- **Discussions**: [GitHub Discussions](https://github.com/j00131120/mcp_database_server/discussions)
- **Email**: [j00131120@163.com](mailto:j00131120@163.com)

## 🔄 Version History

### v1.0.0
- Initial release
- Full MCP protocol support
- Redis connection pooling
- Comprehensive monitoring tools
- Security features implementation
- Production-ready deployment

---

<p align="center">
  <strong>Built with ❤️ for the Redis and MCP communities</strong>
</p>