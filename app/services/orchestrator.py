"""
Search Orchestrator
Coordinates the entire search pipeline: cache → fetch → normalize → dedupe → rank
Now with intelligent caching for 10-20x performance boost
"""

import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from app.core.schema import SearchIntent, Itinerary
from app.core.normalize import ItineraryNormalizer
from app.core.dedupe import ItineraryDeduplicator
from app.core.scoring import ItineraryRanker, get_category_winners
from app.core.cache import cache_manager


class SearchOrchestrator:
    """
    Main orchestrator for flight search
    Pipeline: Cache Check → Provider Calls → Normalization → Deduplication → Ranking → Cache Store
    """
    
    def __init__(self):
        self.normalizer = ItineraryNormalizer()
        self.deduplicator = ItineraryDeduplicator()
        self.sample_data_path = Path(__file__).parent.parent.parent / "data" / "sample_itineraries.json"
    
    async def search(self, intent: SearchIntent) -> tuple[List[Itinerary], bool]:
        """
        Execute full search pipeline with caching
        Returns: (itineraries, cache_hit)
        """
        # Step 1: Check cache first (10-20x faster)
        cached_results = await cache_manager.get_search_results(intent)
        if cached_results:
            return cached_results, True
        
        # Step 2: Cache miss - fetch fresh results
        raw_itineraries = await self._fetch_results(intent)
        
        # Step 3: Normalize
        normalized = [self.normalizer.normalize(itin) for itin in raw_itineraries]
        
        # Step 4: Deduplicate
        deduplicated = self.deduplicator.deduplicate(normalized)
        
        # Step 5: Rank
        ranker = ItineraryRanker(intent)
        ranked = ranker.rank_itineraries(deduplicated)
        
        # Step 6: Cache the results (5 minute TTL)
        await cache_manager.set_search_results(intent, ranked, ttl_seconds=300)
        
        return ranked, False
    
    async def _fetch_results(self, intent: SearchIntent) -> List[Itinerary]:
        """
        Fetch flight results
        Phase 1: Load from sample data
        Phase 2+: Call real provider APIs
        """
        # Load sample data
        if not self.sample_data_path.exists():
            return []
        
        with open(self.sample_data_path, 'r') as f:
            data = json.load(f)
        
        # Parse into Itinerary objects
        itineraries = [Itinerary(**itin_data) for itin_data in data]
        
        # Filter by intent (basic filtering for Phase 1)
        filtered = self._filter_by_intent(itineraries, intent)
        
        return filtered
    
    def _filter_by_intent(self, itineraries: List[Itinerary], intent: SearchIntent) -> List[Itinerary]:
        """Filter itineraries based on search intent"""
        filtered = []
        
        for itin in itineraries:
            # Check origin/destination match
            origin_match = itin.legs[0].origin.code in intent.origins
            destination_match = itin.legs[-1].destination.code in intent.destinations
            
            if not (origin_match and destination_match):
                continue
            
            # Check max stops
            if intent.nonstop_only and not itin.is_direct:
                continue
            
            if intent.max_stops is not None and itin.num_stops > intent.max_stops:
                continue
            
            # Check max price
            if intent.max_price_usd and itin.price.total_usd > intent.max_price_usd:
                continue
            
            # Check max duration
            if intent.max_duration_hours:
                max_minutes = intent.max_duration_hours * 60
                if itin.total_duration_minutes > max_minutes:
                    continue
            
            # Check no red-eyes
            if intent.no_red_eyes:
                has_red_eye = any(
                    leg.departure_time.hour >= 22 or leg.departure_time.hour < 5
                    for leg in itin.legs
                )
                if has_red_eye:
                    continue
            
            # Check no overnight layovers
            if intent.no_overnight_layovers:
                has_overnight = any(layover.overnight for layover in itin.layovers)
                if has_overnight:
                    continue
            
            filtered.append(itin)
        
        return filtered
    
    def get_categories(self, itineraries: List[Itinerary]) -> Dict[str, Itinerary]:
        """Get category winners (cheapest, fastest, etc.)"""
        return get_category_winners(itineraries)
