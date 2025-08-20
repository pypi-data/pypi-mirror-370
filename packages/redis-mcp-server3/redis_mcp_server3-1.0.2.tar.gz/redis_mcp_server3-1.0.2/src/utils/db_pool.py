"""
Database Connection Pool Management Module
Provides asynchronous MySQL connection pool functionality
"""
import asyncio

import redis.asyncio as redis
from src.utils.logger_util import logger
from src.utils.db_config import load_activate_redis_config


class RedisPool:
    """Redis connection pool management class"""

    _instance = None
    _pool = None
    _redis = None
    _config = None

    @classmethod
    async def get_instance(cls):
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = RedisPool()
            await cls._instance._initialize()
        return cls._instance

    async def _initialize(self):
        """Initialize connection pool"""
        if self._pool is not None:
            return

        # Get active Redis instance and configuration
        redis_instance, redis_config = load_activate_redis_config()
        self._config = redis_config

        try:
            # Prepare connection pool parameters
            pool_kwargs = {
                'host': redis_instance.redis_host,
                'port': redis_instance.redis_port,
                'db': redis_instance.redis_database,
                'max_connections': redis_config.redis_max_connections,
                'socket_connect_timeout': redis_config.redis_connection_timeout,
                'socket_timeout': redis_config.socket_timeout,
                'decode_responses': redis_instance.redis_decode_responses,
                'health_check_interval': redis_config.health_check_interval,
                'retry_on_timeout': redis_config.retry_on_timeout
            }

            # Only add password parameter when password exists
            if redis_instance.redis_password:
                pool_kwargs['password'] = redis_instance.redis_password

            # Only add SSL parameters when SSL is enabled
            if redis_instance.redis_ssl:
                pool_kwargs['ssl'] = True
                pool_kwargs['ssl_check_hostname'] = False
                pool_kwargs['ssl_cert_reqs'] = None

            # Create connection pool
            self._pool = redis.ConnectionPool(**pool_kwargs)

            # Create Redis client
            self._redis = redis.Redis(connection_pool=self._pool)

            # Test connection
            await self._redis.ping()

            logger.info(f"Redis connection pool initialized successfully")
            logger.info(f"  Instance: {redis_instance.redis_instance_id}")
            logger.info(f"  Address: {redis_instance.redis_host}:{redis_instance.redis_port}")
            logger.info(f"  Database: {redis_instance.redis_database}")
            logger.info(f"  Max connections: {redis_config.redis_max_connections}")

        except Exception as e:
            logger.error(f"Redis connection pool initialization failed: {str(e)}")
            raise

    async def get_redis(self) -> redis.Redis:
        """
        Get Redis client instance

        Returns:
            redis.Redis: Redis client instance
        """
        if self._redis is None:
            await self._initialize()
        return self._redis

    async def health_check(self) -> bool:
        """
        Perform health check

        Returns:
            bool: Whether the connection is healthy
        """
        try:
            if self._redis is None:
                return False

            # Execute ping command to check connection
            result = await self._redis.ping()
            if result:
                logger.debug("Redis health check passed")
                return True
            else:
                logger.warning("Redis health check failed: ping returned False")
                return False

        except Exception as e:
            logger.error(f"Redis health check failed: {str(e)}")
            return False

    async def close_pool(self):
        """Close connection pool"""
        if self._pool is None:
            logger.warning("Redis connection pool does not exist, no need to close")
            return

        try:
            # Close Redis client
            if self._redis:
                await self._redis.aclose()
                self._redis = None

            # Disconnect connection pool
            await self._pool.aclose()
            self._pool = None

            logger.info("Redis connection pool closed")

        except Exception as e:
            logger.error(f"Failed to close Redis connection pool: {str(e)}")


# Export connection pool retrieval function
async def get_redis_pool():
    """Get Redis connection pool instance"""
    return await RedisPool.get_instance()


if __name__ == "__main__":
    # Test connection pool
    async def test_pool():
        redis_pool = await get_redis_pool()
        redis_client = await redis_pool.get_redis()

        # Test basic operations
        await redis_client.set("test_key", "test_value")
        value = await redis_client.get("test_key")
        logger.info(f"Test result: {value}")

        # Clean up test data
        await redis_client.delete("test_key")

        # Close connection pool
        await redis_pool.close_pool()


    asyncio.run(test_pool())