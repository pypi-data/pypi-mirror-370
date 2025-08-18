from src.utils.db_config import load_activate_redis_config
from src.utils.db_operate import execute_command
from src.utils.logger_util import logger


async def get_connection_status() -> dict:
    """Test Redis connection"""
    logger.info("=== Connection Test ===")

    try:
        # Test PING command
        ping_result = await execute_command('PING')
        logger.info(f"PING test: {ping_result}")

        # Test simple SET/GET operations
        await execute_command('SET', 'test:connection', 'ok')
        get_result = await execute_command('GET', 'test:connection')
        logger.info(f"SET/GET test: {get_result}")

        # Clean up test keys
        await execute_command('DEL', 'test:connection')

        return {"ping": ping_result, "set_get": get_result}
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return {"error": str(e)}

async def generate_database_config():

    active_redis, redis_config = load_activate_redis_config()

    # Hide sensitive information
    safe_config = {
        "redisInstanceId": active_redis.redis_instance_id,
        "redisType": active_redis.redis_type,
        "host": active_redis.redis_host,
        "port": active_redis.redis_port,
        "database": active_redis.redis_database,
        "password": "***hidden***" if active_redis.redis_password else None,
        "ssl": active_redis.redis_ssl,
        "pool_size": redis_config.redis_pool_size,
        "max_connections": redis_config.redis_max_connections,
        "connection_timeout": redis_config.redis_connection_timeout,
    }
    logger.info("Successfully retrieved Redis configuration information")
    logger.info(f"Redis configuration: {safe_config}")
    return safe_config