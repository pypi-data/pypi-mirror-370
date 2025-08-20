"""
Database Operations Module

Provides database operation functions with HTTP proxy support.
"""

from src.utils.db_pool import get_redis_pool
from src.utils.logger_util import logger
from typing import Any, Dict, List, Optional, Union, Tuple

async def get_redis_connection():
    """Get connection from Redis connection pool"""
    try:
        pool = await get_redis_pool()
        redis_client = await pool.get_redis()
        return redis_client
    except Exception as e:
        logger.error(f"Failed to get connection from Redis connection pool: {e}")
        raise


async def get_redis_status():
    """Get connection from Redis connection pool"""
    try:
        pool = await get_redis_pool()
        return pool.health_check()
    except Exception as e:
        logger.error(f"Failed to get connection from Redis connection pool: {e}")
        raise


async def execute_command(command: str, *args, **kwargs) -> Any:
    """
    Execute any Redis command (async version, using connection pool)

    Args:
        command: Redis command name (such as 'SET', 'GET', 'HSET', etc.)
        *args: Command arguments
        **kwargs: Command keyword arguments

    Returns:
        Any: Redis command execution result

    Examples:
        # String operations
        await execute_command('SET', 'key1', 'value1')
        await execute_command('GET', 'key1')
        await execute_command('SETEX', 'key2', 60, 'value2')

        # Hash operations
        await execute_command('HSET', 'hash1', 'field1', 'value1')
        await execute_command('HGET', 'hash1', 'field1')
        await execute_command('HGETALL', 'hash1')

        # List operations
        await execute_command('LPUSH', 'list1', 'item1', 'item2')
        await execute_command('LRANGE', 'list1', 0, -1)

        # Set operations
        await execute_command('SADD', 'set1', 'member1', 'member2')
        await execute_command('SMEMBERS', 'set1')

        # Sorted set operations
        await execute_command('ZADD', 'zset1', {'member1': 1.0, 'member2': 2.0})
        await execute_command('ZRANGE', 'zset1', 0, -1, withscores=True)

        # General operations
        await execute_command('KEYS', '*')
        await execute_command('EXISTS', 'key1')
        await execute_command('DEL', 'key1', 'key2')
        await execute_command('EXPIRE', 'key1', 60)
        await execute_command('TTL', 'key1')

        # Transaction operations
        await execute_command('MULTI')
        await execute_command('EXEC')

        # Pub/Sub
        await execute_command('PUBLISH', 'channel1', 'message')

        # Server information
        await execute_command('INFO')
        await execute_command('PING')
    """
    logger.debug(f"Preparing to execute Redis command: {command} {args} {kwargs}")

    try:
        redis_client = await get_redis_connection()

        # Convert command name to lowercase
        command_lower = command.lower()

        # Check if Redis client has this command method
        if hasattr(redis_client, command_lower):
            cmd_method = getattr(redis_client, command_lower)

            # Execute command
            if kwargs:
                # If there are keyword arguments, pass both positional and keyword arguments
                result = await cmd_method(*args, **kwargs)
            else:
                # Only positional arguments
                result = await cmd_method(*args)

            logger.debug(f"Redis command executed successfully, return type: {type(result)}")

            # Log successfully executed command (truncate long parameters to avoid overly long logs)
            args_str = str(args)[:200] + ('...' if len(str(args)) > 200 else '')
            kwargs_str = str(kwargs)[:200] + ('...' if len(str(kwargs)) > 200 else '')
            logger.info(f"Redis command executed successfully: {command} {args_str} {kwargs_str}")

            return result

        else:
            # If no corresponding method found, try using execute_command method
            try:
                # Use Redis native execute_command method
                result = await redis_client.execute_command(command.upper(), *args)
                logger.info(f"Redis command executed successfully via execute_command: {command} {args}")
                return result
            except Exception as e:
                logger.error(f"Unsupported Redis command: {command}, error: {e}")
                raise AttributeError(f"Unsupported Redis command: {command}")

    except Exception as e:
        logger.error(f"Redis command execution failed: {command} {args} {kwargs}, error: {e}")
        raise


async def execute_raw_command(command_string: str) -> Any:
    """
    Execute raw Redis command string

    Args:
        command_string: Complete Redis command string, such as "SET key1 value1"

    Returns:
        Any: Redis command execution result

    Examples:
        await execute_raw_command("SET key1 value1")
        await execute_raw_command("GET key1")
        await execute_raw_command("HSET hash1 field1 value1")
        await execute_raw_command("KEYS *")
    """
    logger.debug(f"Preparing to execute raw Redis command: {command_string}")

    try:
        # Simple command string parsing (handle quotes)
        import shlex
        parts = shlex.split(command_string.strip())
        if not parts:
            raise ValueError("Command string cannot be empty")

        command = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        # Execute command
        return await execute_command(command, *args)

    except Exception as e:
        logger.error(f"Raw Redis command execution failed: {command_string}, error: {e}")
        raise


async def execute_pipeline_commands(commands: List[Tuple[str, tuple, dict]]) -> List[Any]:
    """
    Use pipeline to batch execute Redis commands

    Args:
        commands: Command list, each element is a (command, args, kwargs) tuple

    Returns:
        List[Any]: Execution result list of all commands

    Examples:
        commands = [
            ('SET', ('key1', 'value1'), {}),
            ('SET', ('key2', 'value2'), {}),
            ('GET', ('key1',), {}),
            ('GET', ('key2',), {})
        ]
        results = await execute_pipeline_commands(commands)
    """
    logger.debug(f"Preparing to execute pipeline commands, {len(commands)} commands in total")

    try:
        redis_client = await get_redis_connection()

        # Create pipeline
        pipe = redis_client.pipeline()

        # Add commands to pipeline
        for command, args, kwargs in commands:
            command_lower = command.lower()
            if hasattr(pipe, command_lower):
                cmd_method = getattr(pipe, command_lower)
                if kwargs:
                    cmd_method(*args, **kwargs)
                else:
                    cmd_method(*args)
            else:
                # Use native command
                pipe.execute_command(command.upper(), *args)

        # Execute pipeline
        results = await pipe.execute()

        logger.info(f"Pipeline commands executed successfully, {len(commands)} commands in total")
        return results

    except Exception as e:
        logger.error(f"Pipeline command execution failed: {e}")
        raise


# Add simple wrappers for common Redis operations
async def redis_set(key, value):
    return await execute_command('SET', key, value)


async def redis_get(key):
    return await execute_command('GET', key)


async def redis_hset(name, key, value):
    return await execute_command('HSET', name, key, value)


async def redis_hgetall(name):
    result = await execute_command('HGETALL', name)
    # redis.asyncio returns dict, some drivers may return list/str, need compatibility
    if isinstance(result, dict):
        return result
    elif isinstance(result, list):
        # Convert to dict
        return dict(zip(result[::2], result[1::2]))
    elif isinstance(result, str):
        # Empty hash may return empty string
        return {}
    else:
        raise TypeError(f"Unexpected HGETALL result type: {type(result)}")


if __name__ == "__main__":
    import asyncio


    async def main():
        """Main test function"""


    # Run test
    asyncio.run(main())