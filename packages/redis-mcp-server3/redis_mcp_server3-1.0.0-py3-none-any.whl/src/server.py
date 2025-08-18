
"""
MCP NoSQL Server

Main entry point for Redis MCP Client server.
"""
import os
import sys
from fastmcp import FastMCP
from src.resources.db_resources import generate_database_config, get_connection_status
from src.tools.db_tool import generate_test_data, get_redis_server_info, get_redis_memory_info, get_redis_clients_info, \
    get_redis_stats_info, get_database_info, get_keys_sample, get_key_types_distribution, get_config_info
from src.utils.db_operate import execute_command

project_path=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# Add current directory to Python module search path
sys.path.insert(0,project_path)
from src.utils.logger_util import logger, db_config_path
from src.utils import load_activate_redis_config
# Create global MCP server instance
mcp = FastMCP("Redis MCP Client Server")


@mcp.tool()
async def redis_exec(command: str, args: list = None):
    """
    Execute Redis commands

    Args:
        command: Redis command name, such as 'GET', 'SET', 'HGET', etc.
        args: Command argument list, such as ['key'] or ['key', 'value']

    Examples:
        redis_exec('GET', ['mykey'])
        redis_exec('SET', ['mykey', 'myvalue'])
        redis_exec('HGET', ['myhash', 'field'])

    Returns:
        dict: Dictionary containing execution results
    """
    if args is None:
        args = []

    logger.info(f"Executing Redis command: {command} {args}")
    try:
        result = await execute_command(command, *args)
        logger.info(f"Redis command executed successfully")
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Redis command execution failed: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
async def gen_test_data(table: str, columns: list, num: int = 10):
    """
    Automatically generate test data

    Args:
        table: Table name
        columns: Column name list
        num: Number of records to generate, default 10

    Returns:
        dict: Dictionary containing success status and message
    """
    logger.info(f"Generating {num} test data records for table {table}, fields: {columns}")

    try:
        await generate_test_data(table, columns, num)
        logger.info(f"Successfully generated {num} data records for {table}")
        return {"success": True, "msg": f"Generated {num} rows for {table}"}
    except Exception as e:
        logger.error(f"Failed to generate test data: {e}")
        return {"success": False, "error": str(e)}


# ==================== Redis Resource Information ====================

@mcp.resource("database://config")
async def get_database_config_resource():
    """
    Get database configuration information (hide sensitive information)
    """
    logger.info("Getting database configuration information")

    try:
        safe_config = await generate_database_config()
        return {
            "uri": "database://config",
            "mimeType": "application/json",
            "text": str(safe_config)
        }
    except Exception as e:
        logger.error(f"Failed to get database configuration: {e}")
        return {
            "uri": "database://config",
            "mimeType": "application/json",
            "text": f'{{"error": "{str(e)}"}}'
        }


@mcp.resource("database://status")
async def get_database_status_resource():
    """
    Get database connection status
    """
    logger.info("Getting database status")

    try:
        connection_status = get_connection_status()
        return {
            "uri": "database://status",
            "mimeType": "application/json",
            "text": str(connection_status)
        }
    except Exception as e:
        logger.error(f"Failed to get database status: {e}")
        return {
            "uri": "database://status",
            "mimeType": "application/json",
            "text": f'{{"error": "{str(e)}"}}'
        }


# ==================== Redis Information Retrieval Tools ====================

@mcp.tool()
async def get_server_info():
    """
    Get Redis server basic information

    Returns:
        dict: Dictionary containing Redis server information
    """
    logger.info("Getting Redis server information")

    try:
        info = await get_redis_server_info()
        return {"success": True, "data": info}
    except Exception as e:
        logger.error(f"Failed to get server information: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
async def get_memory_info():
    """
    Get Redis memory usage information

    Returns:
        dict: Dictionary containing Redis memory usage information
    """
    logger.info("Getting Redis memory information")

    try:
        info = await get_redis_memory_info()
        return {"success": True, "data": info}
    except Exception as e:
        logger.error(f"Failed to get memory information: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
async def get_clients_info():
    """
    Get Redis client connection information

    Returns:
        dict: Dictionary containing Redis client connection information
    """
    logger.info("Getting Redis client information")

    try:
        info = await get_redis_clients_info()
        return {"success": True, "data": info}
    except Exception as e:
        logger.error(f"Failed to get client information: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
async def get_stats_info():
    """
    Get Redis statistics information

    Returns:
        dict: Dictionary containing Redis statistics information
    """
    logger.info("Getting Redis statistics information")

    try:
        info = await get_redis_stats_info()
        return {"success": True, "data": info}
    except Exception as e:
        logger.error(f"Failed to get statistics information: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
async def get_db_info():
    """
    Get Redis database information

    Returns:
        dict: Dictionary containing Redis database information
    """
    logger.info("Getting Redis database information")

    try:
        info = await get_database_info()
        return {"success": True, "data": info}
    except Exception as e:
        logger.error(f"Failed to get database information: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
async def get_keys_info():
    """
    Get Redis key sample information

    Returns:
        dict: Dictionary containing Redis key sample information
    """
    logger.info("Getting Redis key sample information")

    try:
        info = await get_keys_sample()
        return {"success": True, "data": info}
    except Exception as e:
        logger.error(f"Failed to get key information: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
async def get_key_types():
    """
    Get Redis key type distribution statistics

    Returns:
        dict: Dictionary containing Redis key type distribution
    """
    logger.info("Getting Redis key type distribution")

    try:
        info = await get_key_types_distribution()
        return {"success": True, "data": info}
    except Exception as e:
        logger.error(f"Failed to get key type distribution: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
async def get_redis_config():
    """
    Get Redis configuration information

    Returns:
        dict: Dictionary containing Redis configuration information
    """
    logger.info("Getting Redis configuration information")

    try:
        info = await get_config_info()
        return {"success": True, "data": info}
    except Exception as e:
        logger.error(f"Failed to get configuration information: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
async def get_redis_overview():
    """
    Get Redis complete overview information (including all monitoring information)

    Returns:
        dict: Dictionary containing Redis complete overview information
    """
    logger.info("Getting Redis complete overview information")

    try:
        overview = {}

        # Get all information
        overview['server'] = await get_redis_server_info()
        overview['memory'] = await get_redis_memory_info()
        overview['clients'] = await get_redis_clients_info()
        overview['stats'] = await get_redis_stats_info()
        overview['database'] = await get_database_info()
        overview['keys_sample'] = await get_keys_sample()
        overview['key_types'] = await get_key_types_distribution()
        overview['config'] = await get_config_info()

        return {"success": True, "data": overview}
    except Exception as e:
        logger.error(f"Failed to get Redis overview information: {e}")
        return {"success": False, "error": str(e)}

# ==================== Server Startup Related ====================

# When using fastmcp run, FastMCP CLI automatically handles server startup
# No need to manually call mcp.run() or handle stdio

def main():
    """Main function: Start MCP server"""
    logger.info(f"Database configuration file path:{db_config_path}")
    logger.info(f"Current project path:{project_path}")
    logger.info("Redis DataSource MCP Client server is ready to accept connections")

    active_db, _ = load_activate_redis_config()
    logger.info(f"Current database instance configuration: {active_db}")
    # When using fastmcp run, just call mcp.run() directly
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
