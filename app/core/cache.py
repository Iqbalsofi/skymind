"""
Redis caching layer for high-performance search
Multi-tier caching strategy
"""

import json
import hashlib
from typing import Optional, List, Any
from datetime import datetime, timedelta
import os

from app.core.schema import Itinerary, SearchIntent

# Try to import Redis - if not available, caching will be disabled
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️  Redis library not installed - caching disabled")


class CacheManager:
    """
    Manages multi-tier caching for SkyMind
    
    Tier 1: Redis (5 minutes) - Search results
    Tier 2: Redis (1 hour) - Provider responses
    Tier 3: Redis (24 hours) - Static data (airports, etc.)
    """
    
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis_client: Optional[Any] = None
        self.redis_url = redis_url
        cache_enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"
        self.enabled = cache_enabled and REDIS_AVAILABLE
    
    async def connect(self):
        """Connect to Redis"""
        if not self.enabled:
            return
        
        try:
            self.redis_client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
            )
            await self.redis_client.ping()
            print("✅ Redis connected successfully")
        except Exception as e:
            print(f"⚠️  Redis connection failed: {e}. Caching disabled.")
            self.redis_client = None
            self.enabled = False
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
    
    def _generate_cache_key(self, intent: SearchIntent) -> str:
        """
        Generate unique cache key from search intent
        Format: search:{origin}:{dest}:{date}:{cabin}:{stops}:{priority}
        """
        date_str = intent.departure_date.strftime("%Y-%m-%d")
        key_parts = [
            "search",
            "-".join(sorted(intent.origins)),
            "-".join(sorted(intent.destinations)),
            date_str,
            intent.cabin_class.value,
            str(intent.max_stops or "any"),
            intent.priority,
        ]
        
        # Add optional filters if present
        if intent.nonstop_only:
            key_parts.append("nonstop")
        if intent.max_price_usd:
            key_parts.append(f"maxprice{int(intent.max_price_usd)}")
        
        return ":".join(key_parts)
    
    async def get_search_results(
        self,
        intent: SearchIntent
    ) -> Optional[List[Itinerary]]:
        """Get cached search results"""
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            cache_key = self._generate_cache_key(intent)
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                # Deserialize from JSON
                data_list = json.loads(cached_data)
                itineraries = [Itinerary(**item) for item in data_list]
                print(f"✅ Cache HIT for {cache_key}")
                return itineraries
            
            print(f"❌ Cache MISS for {cache_key}")
            return None
            
        except Exception as e:
            print(f"⚠️  Cache get error: {e}")
            return None
    
    async def set_search_results(
        self,
        intent: SearchIntent,
        itineraries: List[Itinerary],
        ttl_seconds: int = 300  # 5 minutes default
    ):
        """Cache search results"""
        if not self.enabled or not self.redis_client:
            return
        
        try:
            cache_key = self._generate_cache_key(intent)
            
            # Serialize to JSON
            data_list = [itin.model_dump(mode='json') for itin in itineraries]
            cached_data = json.dumps(data_list)
            
            # Store with TTL
            await self.redis_client.setex(
                cache_key,
                ttl_seconds,
                cached_data
            )
            print(f"✅ Cached {len(itineraries)} results for {cache_key} (TTL: {ttl_seconds}s)")
            
        except Exception as e:
            print(f"⚠️  Cache set error: {e}")
    
    async def get_provider_response(
        self,
        provider_name: str,
        search_hash: str
    ) -> Optional[dict]:
        """Get cached provider response"""
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            cache_key = f"provider:{provider_name}:{search_hash}"
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            
            return None
            
        except Exception as e:
            print(f"⚠️  Cache get error: {e}")
            return None
    
    async def set_provider_response(
        self,
        provider_name: str,
        search_hash: str,
        response: dict,
        ttl_seconds: int = 300  # 5 minutes
    ):
        """Cache provider API response"""
        if not self.enabled or not self.redis_client:
            return
        
        try:
            cache_key = f"provider:{provider_name}:{search_hash}"
            cached_data = json.dumps(response)
            
            await self.redis_client.setex(
                cache_key,
                ttl_seconds,
                cached_data
            )
            
        except Exception as e:
            print(f"⚠️  Cache set error: {e}")
    
    async def invalidate_search(self, intent: SearchIntent):
        """Invalidate cached search results"""
        if not self.enabled or not self.redis_client:
            return
        
        try:
            cache_key = self._generate_cache_key(intent)
            await self.redis_client.delete(cache_key)
            print(f"🗑️  Invalidated cache for {cache_key}")
        except Exception as e:
            print(f"⚠️  Cache invalidation error: {e}")
    
    async def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.enabled or not self.redis_client:
            return {"enabled": False}
        
        try:
            info = await self.redis_client.info("stats")
            return {
                "enabled": True,
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                )
            }
        except Exception as e:
            return {"enabled": True, "error": str(e)}
    
    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage"""
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)


# Global cache manager instance
cache_manager = CacheManager()
