"""
Redis Cache Client Module

This module provides a client for interacting with Redis for caching purposes.
"""

import os

import aioredis

from services.auth_service import ICache

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")


class RedisCache(ICache):
    """
    A Redis client for caching that implements the ICache interface.

    Methods:
        get(key): Retrieves a value from the cache by its key.
        set(key, value, ttl): Stores a value in the cache with a time-to-live (TTL).
        delete(key): Deletes a value from the cache by its key.
    """

    def __init__(self):
        """
        Initializes the Redis client with configuration from environment variables.
        """
        self.redis = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

    async def get(self, key: str):
        """
        Retrieves a value from the cache by its key.

        Args:
            key (str): The key of the cached value.

        Returns:
            str: The cached value, or None if the key does not exist.
        """
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ttl: int):
        """
        Stores a value in the cache with a time-to-live (TTL).

        Args:
            key (str): The key for the cached value.
            value (str): The value to cache.
            ttl (int): The time-to-live for the cached value in seconds.

        Returns:
            None
        """
        await self.redis.setex(key, ttl, value)

    async def delete(self, key: str):
        """
        Deletes a value from the cache by its key.

        Args:
            key (str): The key of the value to delete.

        Returns:
            None
        """
        await self.redis.delete(key)
