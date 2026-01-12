"""
Normalization and validation of provider data to canonical schema
"""

from typing import Any, Dict
from datetime import datetime
from app.core.schema import Itinerary, Leg, RiskFlag


class ItineraryNormalizer:
    """
    Validates and normalizes itinerary data
    Ensures all data conforms to canonical schema
    """
    
    def normalize(self, itinerary: Itinerary) -> Itinerary:
        """
        Normalize and enrich itinerary
        - Validate schema
        - Calculate derived fields
        - Detect risk flags
        """
        # Ensure derived fields are correct
        itinerary.num_stops = len(itinerary.legs) - 1
        itinerary.is_direct = (itinerary.num_stops == 0)
        
        # Calculate total duration
        if itinerary.legs:
            first_departure = itinerary.legs[0].departure_time
            last_arrival = itinerary.legs[-1].arrival_time
            total_minutes = int((last_arrival - first_departure).total_seconds() / 60)
            itinerary.total_duration_minutes = total_minutes
        
        # Detect risk flags
        itinerary.risk_flags = self._detect_risks(itinerary)
        
        return itinerary
    
    def _detect_risks(self, itinerary: Itinerary) -> list[RiskFlag]:
        """Automatically detect risk flags"""
        risks = []
        
        # Check layovers
        for layover in itinerary.layovers:
            # Tight connection
            if layover.duration_minutes < 90:
                risks.append(RiskFlag.TIGHT_CONNECTION)
            
            # Long layover
            elif 360 <= layover.duration_minutes < 720:
                risks.append(RiskFlag.LONG_LAYOVER)
            
            # Overnight layover
            if layover.overnight or layover.duration_minutes >= 720:
                risks.append(RiskFlag.OVERNIGHT_LAYOVER)
            
            # Airport change
            if layover.airport_change:
                risks.append(RiskFlag.AIRPORT_CHANGE)
        
        # Check for red-eye flights (departures between 10 PM - 5 AM)
        for leg in itinerary.legs:
            hour = leg.departure_time.hour
            if hour >= 22 or hour < 5:
                risks.append(RiskFlag.RED_EYE)
                break
        
        # Remove duplicates
        return list(set(risks))
    
    def validate_schema(self, itinerary: Itinerary) -> bool:
        """
        Validate itinerary against schema
        Returns True if valid
        """
        try:
            # Pydantic validation happens automatically
            # Additional business logic checks
            
            # Must have at least one leg
            if not itinerary.legs:
                return False
            
            # Price must be positive
            if itinerary.price.total_usd <= 0:
                return False
            
            # Legs must be in chronological order
            for i in range(len(itinerary.legs) - 1):
                if itinerary.legs[i].arrival_time > itinerary.legs[i+1].departure_time:
                    return False
            
            # Layovers must match legs
            if len(itinerary.layovers) != len(itinerary.legs) - 1:
                return False
            
            return True
            
        except Exception:
            return False


def normalize_itinerary(itinerary: Itinerary) -> Itinerary:
    """Convenience function to normalize an itinerary"""
    normalizer = ItineraryNormalizer()
    return normalizer.normalize(itinerary)
