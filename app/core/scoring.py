"""
Multi-objective scoring and ranking logic
This is the "moat" - the secret sauce that makes decisions better than competitors
"""

from typing import List, Dict, Optional
from app.core.schema import (
    Itinerary, ScoreBreakdown, SearchIntent, RiskFlag
)


class ItineraryRanker:
    """
    Ranks itineraries using multi-objective optimization
    Generates scores and human-readable explanations
    """
    
    # Default preference weights
    DEFAULT_WEIGHTS = {
        "cheap": {"price": 0.50, "duration": 0.15, "stops": 0.10, "layover": 0.05, "baggage": 0.05, "risk": 0.10, "reliability": 0.05},
        "fast": {"price": 0.15, "duration": 0.45, "stops": 0.20, "layover": 0.10, "baggage": 0.02, "risk": 0.05, "reliability": 0.03},
        "comfort": {"price": 0.20, "duration": 0.20, "stops": 0.15, "layover": 0.15, "baggage": 0.10, "risk": 0.15, "reliability": 0.05},
        "balanced": {"price": 0.25, "duration": 0.20, "stops": 0.15, "layover": 0.10, "baggage": 0.10, "risk": 0.15, "reliability": 0.05}
    }
    
    def __init__(self, search_intent: Optional[SearchIntent] = None):
        """Initialize ranker with search intent for context"""
        self.search_intent = search_intent
        self.weights = self._get_weights()
    
    def _get_weights(self) -> Dict[str, float]:
        """Get scoring weights based on user priority"""
        if not self.search_intent:
            return self.DEFAULT_WEIGHTS["balanced"]
        
        priority = self.search_intent.priority.lower()
        return self.DEFAULT_WEIGHTS.get(priority, self.DEFAULT_WEIGHTS["balanced"])
    
    def rank_itineraries(self, itineraries: List[Itinerary]) -> List[Itinerary]:
        """
        Rank itineraries and populate scores
        Returns sorted list (highest score first)
        """
        if not itineraries:
            return []
        
        # Calculate scores for all itineraries
        for itin in itineraries:
            self._calculate_score(itin, itineraries)
        
        # Sort by score (descending)
        ranked = sorted(itineraries, key=lambda x: x.score or 0, reverse=True)
        
        # Generate explanations
        for itin in ranked:
            itin.explanation = self._generate_explanation(itin, ranked)
        
        return ranked
    
    def _calculate_score(self, itinerary: Itinerary, all_itineraries: List[Itinerary]):
        """Calculate overall score and breakdown"""
        
        # Individual component scores
        price_score = self._score_price(itinerary, all_itineraries)
        duration_score = self._score_duration(itinerary, all_itineraries)
        stops_score = self._score_stops(itinerary)
        layover_score = self._score_layovers(itinerary)
        baggage_score = self._score_baggage(itinerary)
        risk_score = self._score_risk(itinerary)
        reliability_score = self._score_reliability(itinerary)
        
        # Create breakdown
        breakdown = ScoreBreakdown(
            price_score=price_score,
            duration_score=duration_score,
            stops_score=stops_score,
            layover_score=layover_score,
            baggage_score=baggage_score,
            risk_score=risk_score,
            reliability_score=reliability_score,
            weights=self.weights
        )
        
        # Calculate weighted total
        total_score = (
            self.weights["price"] * price_score +
            self.weights["duration"] * duration_score +
            self.weights["stops"] * stops_score +
            self.weights["layover"] * layover_score +
            self.weights["baggage"] * baggage_score +
            self.weights["risk"] * risk_score +
            self.weights["reliability"] * reliability_score
        )
        
        # Assign to itinerary
        itinerary.score = round(total_score, 2)
        itinerary.score_breakdown = breakdown
    
    def _score_price(self, itinerary: Itinerary, all_itineraries: List[Itinerary]) -> float:
        """Score based on price (lower is better)"""
        prices = [itin.price.total_usd for itin in all_itineraries]
        min_price = min(prices)
        max_price = max(prices)
        
        if max_price == min_price:
            return 100.0
        
        # Normalize: cheapest = 100, most expensive = 0
        normalized = 100 * (1 - (itinerary.price.total_usd - min_price) / (max_price - min_price))
        return round(normalized, 2)
    
    def _score_duration(self, itinerary: Itinerary, all_itineraries: List[Itinerary]) -> float:
        """Score based on total duration (shorter is better)"""
        durations = [itin.total_duration_minutes for itin in all_itineraries]
        min_dur = min(durations)
        max_dur = max(durations)
        
        if max_dur == min_dur:
            return 100.0
        
        # Normalize: shortest = 100, longest = 0
        normalized = 100 * (1 - (itinerary.total_duration_minutes - min_dur) / (max_dur - min_dur))
        return round(normalized, 2)
    
    def _score_stops(self, itinerary: Itinerary) -> float:
        """Score based on number of stops"""
        # Direct flight = 100
        # 1 stop = 70
        # 2 stops = 40
        # 3+ stops = 10
        stop_penalties = {0: 100, 1: 70, 2: 40}
        return stop_penalties.get(itinerary.num_stops, 10)
    
    def _score_layovers(self, itinerary: Itinerary) -> float:
        """Score layover quality"""
        if not itinerary.layovers:
            return 100.0  # Direct flight
        
        scores = []
        for layover in itinerary.layovers:
            dur_min = layover.duration_minutes
            
            # Ideal layover: 90-180 min
            if 90 <= dur_min <= 180:
                scores.append(100)
            # Short but acceptable: 60-90 min
            elif 60 <= dur_min < 90:
                scores.append(80)
            # Tight connection: < 60 min
            elif dur_min < 60:
                scores.append(30)
            # Long layover: 180-360 min
            elif 180 < dur_min <= 360:
                scores.append(70)
            # Very long: 360+ min
            else:
                scores.append(40)
            
            # Penalties
            if layover.overnight:
                scores[-1] *= 0.5  # 50% penalty for overnight
            if layover.airport_change:
                scores[-1] *= 0.6  # 40% penalty for airport change
        
        return round(sum(scores) / len(scores), 2)
    
    def _score_baggage(self, itinerary: Itinerary) -> float:
        """Score baggage allowance"""
        score = 50  # Base score
        
        for bag in itinerary.baggage:
            if bag.included and bag.type.value == "carry_on":
                score += 25
            if bag.included and bag.type.value == "checked":
                score += 25
        
        return min(score, 100)
    
    def _score_risk(self, itinerary: Itinerary) -> float:
        """Score based on risk flags (fewer/less severe = better)"""
        base_score = 100
        
        # Risk penalties
        risk_penalties = {
            RiskFlag.SELF_TRANSFER: 40,
            RiskFlag.TIGHT_CONNECTION: 15,
            RiskFlag.OVERNIGHT_LAYOVER: 10,
            RiskFlag.SEPARATE_TICKETS: 35,
            RiskFlag.AIRPORT_CHANGE: 20,
            RiskFlag.LONG_LAYOVER: 5,
            RiskFlag.RED_EYE: 8
        }
        
        for risk in itinerary.risk_flags:
            base_score -= risk_penalties.get(risk, 5)
        
        return max(base_score, 0)
    
    def _score_reliability(self, itinerary: Itinerary) -> float:
        """Score based on provider trust and on-time performance"""
        score = 50  # Base
        
        # Provider trust
        score += itinerary.provider.trust_score * 25
        
        # On-time performance
        if itinerary.signals.on_time_proxy:
            score += itinerary.signals.on_time_proxy * 25
        
        return round(min(score, 100), 2)
    
    def _generate_explanation(self, itinerary: Itinerary, all_ranked: List[Itinerary]) -> str:
        """Generate human-readable explanation"""
        if not itinerary.score_breakdown:
            return "No scoring data available"
        
        parts = []
        breakdown = itinerary.score_breakdown
        
        # Price analysis
        cheapest = min(all_ranked, key=lambda x: x.price.total_usd)
        if itinerary.itinerary_id == cheapest.itinerary_id:
            parts.append("Cheapest option")
        else:
            diff = itinerary.price.total_usd - cheapest.price.total_usd
            parts.append(f"${diff:.0f} more than cheapest")
        
        # Duration
        if itinerary.is_direct:
            parts.append("direct flight")
        else:
            parts.append(f"{itinerary.num_stops} stop(s)")
        
        # Layover quality
        if itinerary.layovers:
            for layover in itinerary.layovers:
                dur_hrs = layover.duration_minutes / 60
                if 1.5 <= dur_hrs <= 3:
                    parts.append(f"{dur_hrs:.1f}h layover (comfortable)")
                elif dur_hrs < 1.5:
                    parts.append(f"{dur_hrs:.1f}h layover (tight)")
                else:
                    parts.append(f"{dur_hrs:.1f}h layover (long)")
        
        # Baggage
        carry_on = any(b.included and b.type.value == "carry_on" for b in itinerary.baggage)
        checked = any(b.included and b.type.value == "checked" for b in itinerary.baggage)
        
        if carry_on and checked:
            parts.append("bags included")
        elif carry_on:
            parts.append("carry-on included")
        
        # Risks
        if itinerary.risk_flags:
            critical_risks = [r for r in itinerary.risk_flags 
                            if r in [RiskFlag.SELF_TRANSFER, RiskFlag.SEPARATE_TICKETS]]
            if critical_risks:
                parts.append(f"⚠️ {critical_risks[0].value.replace('_', ' ')}")
        
        return ". ".join(parts).capitalize() + "."


def get_category_winners(itineraries: List[Itinerary]) -> Dict[str, Itinerary]:
    """Get the winner in each category"""
    if not itineraries:
        return {}
    
    return {
        "cheapest": min(itineraries, key=lambda x: x.price.total_usd),
        "fastest": min(itineraries, key=lambda x: x.total_duration_minutes),
        "best_overall": max(itineraries, key=lambda x: x.score or 0),
        "most_direct": min(itineraries, key=lambda x: x.num_stops),
    }
