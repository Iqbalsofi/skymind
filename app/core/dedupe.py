"""
Deduplication logic for merging identical itineraries from different providers
"""

from typing import List, Dict, Tuple
from collections import defaultdict
from datetime import datetime
from app.core.schema import Itinerary, Leg


class ItineraryDeduplicator:
    """
    Intelligently deduplicate itineraries from multiple providers
    Merges "same flight from different sources" and keeps the best price
    """
    
    def deduplicate(self, itineraries: List[Itinerary]) -> List[Itinerary]:
        """
        Deduplicate itineraries
        Returns list with duplicates merged
        """
        if len(itineraries) <= 1:
            return itineraries
        
        # Group by signature
        groups = self._group_by_signature(itineraries)
        
        # For each group, keep the best one
        deduplicated = []
        for signature, itins in groups.items():
            if len(itins) == 1:
                deduplicated.append(itins[0])
            else:
                # Merge duplicates
                best = self._select_best(itins)
                deduplicated.append(best)
        
        return deduplicated
    
    def _group_by_signature(self, itineraries: List[Itinerary]) -> Dict[str, List[Itinerary]]:
        """Group itineraries by their flight signature"""
        groups = defaultdict(list)
        
        for itin in itineraries:
            sig = self._compute_signature(itin)
            groups[sig].append(itin)
        
        return groups
    
    def _compute_signature(self, itin: Itinerary) -> str:
        """
        Compute unique signature for an itinerary
        Same flights should have same signature regardless of provider
        """
        leg_sigs = []
        for leg in itin.legs:
            # Signature: airline_code + flight_number + date + origin + destination
            dep_date = leg.departure_time.strftime("%Y%m%d")
            leg_sig = f"{leg.airline_code}{leg.flight_number}_{dep_date}_{leg.origin.code}_{leg.destination.code}"
            leg_sigs.append(leg_sig)
        
        return "|".join(leg_sigs)
    
    def _select_best(self, duplicates: List[Itinerary]) -> Itinerary:
        """
        Select the best itinerary from duplicates
        Criteria: lowest price, highest provider trust
        """
        # Sort by price (ascending), then by provider trust (descending)
        sorted_itins = sorted(
            duplicates,
            key=lambda x: (x.price.total_usd, -x.provider.trust_score)
        )
        
        best = sorted_itins[0]
        
        # Add note about cheaper provider
        if len(duplicates) > 1:
            other_providers = [d.provider.provider_name for d in duplicates if d.itinerary_id != best.itinerary_id]
            if other_providers:
                note = f"Also available via: {', '.join(other_providers)}"
                if note not in best.provider.notes:
                    best.provider.notes.append(note)
        
        return best
    
    def find_price_differences(self, itineraries: List[Itinerary]) -> List[Dict]:
        """
        Find same itineraries with different prices
        Useful for debugging provider discrepancies
        """
        groups = self._group_by_signature(itineraries)
        
        differences = []
        for signature, itins in groups.items():
            if len(itins) > 1:
                prices = [(i.provider.provider_name, i.price.total_usd) for i in itins]
                min_price = min(p[1] for p in prices)
                max_price = max(p[1] for p in prices)
                
                if max_price - min_price > 5:  # More than $5 difference
                    differences.append({
                        "signature": signature,
                        "price_range": (min_price, max_price),
                        "difference": max_price - min_price,
                        "providers": prices,
                        "legs": [f"{leg.airline_code}{leg.flight_number}" for leg in itins[0].legs]
                    })
        
        return differences


def merge_itineraries(itineraries: List[Itinerary]) -> List[Itinerary]:
    """
    Convenience function to deduplicate itineraries
    """
    deduper = ItineraryDeduplicator()
    return deduper.deduplicate(itineraries)
