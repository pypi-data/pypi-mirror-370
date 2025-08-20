"""
Database Utility Functions

Provides database utility functions related to SQL execution.
"""
from src.utils.db_operate import execute_command
from src.utils.logger_util import logger
import random, string


async def generate_test_data(table, columns, num):
    """Generate Redis test data"""
    logger.info(f"Starting to generate {num} test records for Redis table '{table}'")
    logger.debug(f"Target {table} columns: {columns}")

    for i in range(num):
        # Generate record ID
        record_id = str(i + 1)
        key = f"table:{table}:{record_id}"

        # Generate field data
        record_data = {}
        for col in columns:
            # Simple example: all use 8-character random strings
            random_value = ''.join(random.choices(string.ascii_letters, k=8))
            record_data[col] = random_value

        # Use Redis HSET command to store records
        await execute_command("HSET", key, mapping=record_data)

        logger.debug(f"Inserting row {i + 1}/{num}: {record_data}")

    logger.info(f"Successfully generated {num} test records for Redis table '{table}'")


async def get_redis_server_info():
    """Get Redis server basic information"""
    logger.info("=== Redis Server Information ===")

    try:
        # Get server information
        info = await execute_command('INFO', 'server')
        logger.info("Server information:")
        for key, value in info.items():
            if key in ['redis_version', 'redis_mode', 'os', 'arch_bits', 'uptime_in_seconds', 'uptime_in_days']:
                logger.info(f"  {key}: {value}")

        return info
    except Exception as e:
        logger.error(f"Failed to get server information: {e}")
        return {}


async def get_redis_memory_info():
    """Get Redis memory usage information"""
    logger.info("=== Redis Memory Information ===")

    try:
        info = await execute_command('INFO', 'memory')
        logger.info("Memory usage:")
        for key, value in info.items():
            if key in ['used_memory_human', 'used_memory_peak_human', 'used_memory_rss_human', 'maxmemory_human']:
                logger.info(f"  {key}: {value}")

        return info
    except Exception as e:
        logger.error(f"Failed to get memory information: {e}")
        return {}


async def get_redis_clients_info():
    """Get Redis client connection information"""
    logger.info("=== Redis Client Information ===")

    try:
        info = await execute_command('INFO', 'clients')
        logger.info("Client connections:")
        for key, value in info.items():
            if key in ['connected_clients', 'client_recent_max_input_buffer', 'client_recent_max_output_buffer']:
                logger.info(f"  {key}: {value}")

        return info
    except Exception as e:
        logger.error(f"Failed to get client information: {e}")
        return {}


async def get_redis_stats_info():
    """Get Redis statistics information"""
    logger.info("=== Redis Statistics Information ===")

    try:
        info = await execute_command('INFO', 'stats')
        logger.info("Operation statistics:")
        for key, value in info.items():
            if key in ['total_connections_received', 'total_commands_processed', 'instantaneous_ops_per_sec',
                       'keyspace_hits', 'keyspace_misses']:
                logger.info(f"  {key}: {value}")

        return info
    except Exception as e:
        logger.error(f"Failed to get statistics information: {e}")
        return {}


async def get_database_info():
    """Get database information"""
    logger.info("=== Database Information ===")

    try:
        # Get current database size
        dbsize = await execute_command('DBSIZE')
        logger.info(f"Current database key count: {dbsize}")

        # Get database keyspace information
        info = await execute_command('INFO', 'keyspace')
        logger.info("Keyspace information:")
        for key, value in info.items():
            if key.startswith('db'):
                logger.info(f"  {key}: {value}")

        return {"dbsize": dbsize, "keyspace": info}
    except Exception as e:
        logger.error(f"Failed to get database information: {e}")
        return {}


async def get_keys_sample():
    """Get key sample information"""
    logger.info("=== Key Sample Information ===")

    try:
        # Get all keys (Note: use KEYS * carefully in production environment)
        all_keys = await execute_command('KEYS', '*')
        total_keys = len(all_keys)
        logger.info(f"Total keys: {total_keys}")

        if total_keys > 0:
            # Display first 10 keys as sample
            sample_keys = all_keys[:10]
            logger.info("Key samples (first 10):")
            for i, key in enumerate(sample_keys, 1):
                key_type = await execute_command('TYPE', key)
                ttl = await execute_command('TTL', key)
                ttl_info = f"TTL: {ttl}s" if ttl > 0 else "No expiration" if ttl == -1 else "Expired"
                logger.info(f"  {i}. {key} (Type: {key_type}, {ttl_info})")

        return {"total_keys": total_keys, "sample_keys": all_keys[:10]}
    except Exception as e:
        logger.error(f"Failed to get key information: {e}")
        return {}


async def get_key_types_distribution():
    """Get key type distribution"""
    logger.info("=== Key Type Distribution ===")

    try:
        all_keys = await execute_command('KEYS', '*')
        type_count = {}

        for key in all_keys:
            key_type = await execute_command('TYPE', key)
            type_count[key_type] = type_count.get(key_type, 0) + 1

        logger.info("Key type distribution:")
        for key_type, count in type_count.items():
            logger.info(f"  {key_type}: {count}")

        return type_count
    except Exception as e:
        logger.error(f"Failed to get key type distribution: {e}")
        return {}


async def get_config_info():
    """Get Redis configuration information"""
    logger.info("=== Redis Configuration Information ===")

    try:
        # Get some important configuration items
        important_configs = [
            'maxmemory', 'maxmemory-policy', 'timeout', 'databases',
            'save', 'appendonly', 'appendfsync'
        ]

        config_info = {}
        for config_key in important_configs:
            try:
                config_value = await execute_command('CONFIG', 'GET', config_key)
                if config_value and len(config_value) >= 2:
                    config_info[config_key] = config_value[1]
                    logger.info(f"  {config_key}: {config_value[1]}")
            except Exception as e:
                logger.debug(f"Failed to get configuration {config_key}: {e}")

        return config_info
    except Exception as e:
        logger.error(f"Failed to get configuration information: {e}")
        return {}