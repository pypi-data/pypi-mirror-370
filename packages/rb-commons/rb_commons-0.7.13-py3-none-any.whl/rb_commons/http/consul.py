import aiocache
import consul
from fastapi import HTTPException, Request
from rb_commons.configs.config import configs


class ServiceDiscovery:
    def __init__(self, host: str, port: int) -> None:
        self.consul_client = consul.Consul(host=host, port=port)
        self.cache = aiocache.Cache(aiocache.SimpleMemoryCache)

    async def _get_service_instances(self, service_name: str) -> dict:
        """Get a healthy service instance from Consul"""
        index, services = self.consul_client.health.service(service_name, passing=True)

        if not services:
            raise HTTPException(status_code=503,
                                detail="Service not available")
        return services

    def _select_instance(self, instances: list, host: str) -> dict:
        """Select instance using consistent hashing"""
        if not instances:
            raise HTTPException(status_code=503, detail="No healthy instances")

        key = host
        hash_value = hash(key)
        return instances[hash_value % len(instances)]

    async def _get_cached_service_instances(self, service_name: str) -> list:
        """Get service instances with caching"""
        cache_key = f"service:{service_name}"
        instances = await self.cache.get(cache_key)
        if not instances:
            instances = await self._get_service_instances(service_name)
            if instances:
                await self.cache.set(cache_key, instances, ttl=30)  # Cache for 30 seconds
        return instances

    def _build_instance_url(self, instance: dict) -> str:
        """Build target URL with proper path handling"""
        service_address = instance['Service']['Address'] or instance['Node']['Address']
        service_port = instance['Service']['Port']
        return f"http://{service_address}:{service_port}"