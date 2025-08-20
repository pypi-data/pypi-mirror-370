"""
Database Configuration Module

Uses singleton pattern to handle database configuration loading and management.
"""

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from .logger_util import logger, db_config_path


@dataclass
class RedisInstance:
    """Redis instance configuration"""
    redis_instance_id: str
    redis_type: str
    redis_host: str
    redis_port: int
    redis_database: int
    redis_password: Optional[str]
    redis_active: bool
    redis_ssl: bool = False
    redis_decode_responses: bool = True


@dataclass
class DatabaseConfig:
    """Database configuration, including connection pool settings and Redis instance list"""
    redis_encoding: str
    redis_pool_size: int
    redis_max_connections: int
    redis_connection_timeout: int
    socket_timeout: int
    retry_on_timeout: bool
    health_check_interval: int
    redis_instances_list: List[RedisInstance]


class DatabaseConfigLoader:
    """Database configuration loader, load configuration from JSON file - singleton pattern"""

    _instance = None
    _initialized = False

    def __new__(cls):
        """
        Singleton pattern implementation

        Returns:
            DatabaseConfigLoader: Singleton instance
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initialize configuration loader (only executed when creating instance for the first time)
        """
        if not self._initialized:
            self.config_json_file = db_config_path
            self._config: Optional[DatabaseConfig] = None
            self._initialized = True
            logger.debug(f"Database configuration loader initialized, configuration file: {self.config_json_file}")

    def load_config(self) -> DatabaseConfig:
        """
        Load database configuration from JSON file

        Returns:
            DatabaseConfig: Loaded configuration object

        Raises:
            FileNotFoundError: Configuration file does not exist
            json.JSONDecodeError: Invalid JSON format
            KeyError: Missing required configuration keys
        """
        if not os.path.exists(self.config_json_file):
            error_msg = f"Database configuration file not found: {self.config_json_file}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        try:
            with open(self.config_json_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            logger.debug(f"Successfully read database configuration file: {self.config_json_file}")
        except json.JSONDecodeError as e:
            error_msg = f"Database configuration file JSON format error: {e}"
            logger.error(error_msg)
            raise json.JSONDecodeError(error_msg, e.doc, e.pos)

        # Validate required keys
        required_keys = ['redisPoolSize', 'redisMaxConnections', 'redisConnectionTimeout', 'redisList']
        for key in required_keys:
            if key not in config_data:
                error_msg = f"Missing required database configuration key: {key}"
                logger.error(error_msg)
                raise KeyError(error_msg)

        # Parse Redis instances
        redis_instances = []
        for redis_data in config_data['redisList']:
            required_redis_keys = [
                'redisInstanceId', 'redisType', 'redisHost', 'redisPort',
                'redisDatabase', 'dbActive'
            ]
            for key in required_redis_keys:
                if key not in redis_data:
                    error_msg = f"Missing required Redis instance configuration key: {key}"
                    logger.error(error_msg)
                    raise KeyError(error_msg)

            redis_instance = RedisInstance(
                redis_instance_id=redis_data['redisInstanceId'],
                redis_type=redis_data['redisType'],
                redis_host=redis_data['redisHost'],
                redis_port=redis_data['redisPort'],
                redis_database=redis_data['redisDatabase'],
                redis_password=redis_data.get('redisPassword'),
                redis_active=redis_data['dbActive'],  # Use dbActive field
                redis_ssl=redis_data.get('redisSsl', False),
                redis_decode_responses=redis_data.get('redisDecodeResponses', True)
            )
            redis_instances.append(redis_instance)
            logger.debug(
                f"Parsed Redis instance: {redis_instance.redis_instance_id} ({redis_instance.redis_host}:{redis_instance.redis_port})")

        # Create configuration object
        self._config = DatabaseConfig(
            redis_encoding=config_data.get('redisEncoding', 'utf-8'),
            redis_pool_size=config_data['redisPoolSize'],
            redis_max_connections=config_data['redisMaxConnections'],
            redis_connection_timeout=config_data['redisConnectionTimeout'],
            socket_timeout=config_data.get('socketTimeout', 30),
            retry_on_timeout=config_data.get('retryOnTimeout', True),
            health_check_interval=config_data.get('healthCheckInterval', 30),
            redis_instances_list=redis_instances
        )

        logger.debug(f"Database configuration loading completed, {len(redis_instances)} Redis instances in total")
        return self._config

    def get_config(self) -> DatabaseConfig:
        """
        Get loaded configuration, automatically load if not loaded

        Returns:
            DatabaseConfig: Configuration object
        """
        if self._config is None:
            return self.load_config()
        return self._config

    def get_active_redis(self) -> Optional[RedisInstance]:
        """
        Get the first active Redis instance

        Returns:
            Optional[RedisInstance]: First active Redis instance, return None if no active instance
        """
        config = self.get_config()
        for redis in config.redis_instances_list:
            if redis.redis_active:
                logger.info(f"Found first active Redis instance: {redis.redis_instance_id}")
                return redis
        logger.warning("No active Redis instance found")
        return None


def load_db_config() -> DatabaseConfig:
    """
    Convenience function to load database configuration

    Returns:
        DatabaseConfig: Loaded configuration object
    """
    loader = DatabaseConfigLoader()
    return loader.load_config()


def load_active_redis_config() -> tuple[RedisInstance, DatabaseConfig]:
    """
    Convenience function to load database configuration and active Redis instance

    Returns:
        tuple[RedisInstance, DatabaseConfig]: Tuple of active Redis instance and configuration object
    """
    loader = DatabaseConfigLoader()
    config = loader.get_config()
    active_redis = loader.get_active_redis()
    if active_redis is None:
        raise ValueError("No active Redis instance found")
    return active_redis, config


# For backward compatibility, keep original function names
def load_redis_config() -> DatabaseConfig:
    """
    Convenience function to load Redis configuration (backward compatible)

    Returns:
        DatabaseConfig: Loaded configuration object
    """
    return load_db_config()


def load_activate_redis_config() -> tuple[RedisInstance, DatabaseConfig]:
    """
    Convenience function to load Redis configuration and active Redis instance (backward compatible)

    Returns:
        tuple[RedisInstance, DatabaseConfig]: Tuple of active Redis instance and configuration object
    """
    return load_active_redis_config()


# Example usage
if __name__ == "__main__":
    # Load configuration
    active_redis, db_config = load_active_redis_config()
    logger.info(f"Redis encoding: {db_config.redis_encoding}")
    logger.info(f"Redis connection pool size: {db_config.redis_pool_size}")
    logger.info(f"Redis max connections: {db_config.redis_max_connections}")
    logger.info(f"Redis connection timeout: {db_config.redis_connection_timeout}")
    logger.info(f"Socket timeout: {db_config.socket_timeout}")
    logger.info(f"Retry on timeout: {db_config.retry_on_timeout}")
    logger.info(f"Health check interval: {db_config.health_check_interval}")

    # Display active Redis information
    logger.info(f"\nActive Redis instance: {active_redis.redis_instance_id}")
    logger.info(f"  Host: {active_redis.redis_host}:{active_redis.redis_port}")
    logger.info(f"  Database: {active_redis.redis_database}")
    logger.info(f"  Type: {active_redis.redis_type}")
    logger.info(f"  Password: {'Set' if active_redis.redis_password else 'Not set'}")
