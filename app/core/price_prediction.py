from datetime import datetime, timedelta
from typing import List
from app.core.schema import Itinerary, PriceReasoning, SearchIntent

class PricePredictor:
    """
    Heuristic-based price prediction engine.
    Analyzes booking window, seasonality, and historical patterns (simulated)
    to advise users on "Buy Now" vs "Wait".
    """
    
    def predict(self, itinerary: Itinerary, intent: SearchIntent) -> Itinerary:
        """
        Enrich itinerary with price prediction analysis
        """
        analysis = self._analyze(itinerary, intent)
        itinerary.price_analysis = analysis
        return itinerary

    def _analyze(self, itinerary: Itinerary, intent: SearchIntent) -> PriceReasoning:
        days_to_departure = (intent.departure_date - datetime.now()).days
        day_of_week = intent.departure_date.weekday() # 0=Mon, 6=Sun
        month = intent.departure_date.month
        
        advice = "monitor"
        confidence = 0.5
        predicted_change = 0.0
        factors = []
        
        # 1. Advance Purchase Logic
        if days_to_departure < 14:
            advice = "buy_now"
            confidence = 0.9
            factors.append("Last minute booking - prices rising daily")
            predicted_change = 50.0  # Likely to rise
            
        elif 14 <= days_to_departure <= 21:
            advice = "buy_now"
            confidence = 0.8
            factors.append("Entering high-price window (< 21 days)")
            predicted_change = 20.0
            
        elif 21 < days_to_departure <= 60:
            advice = "monitor" # Sweet spot logic varies
            confidence = 0.6
            factors.append("Standard booking window")
            
        elif days_to_departure > 90:
            advice = "wait"
            confidence = 0.75
            factors.append("Booking too early - airlines drop prices ~60 days out")
            predicted_change = -30.0 # Likely to drop
            
        # 2. Day of Week Logic
        if day_of_week in [4, 6]: # Fri, Sun
            factors.append("Weekend departure premium applied")
            if advice == "monitor":
                advice = "wait" # Suggest checking Tue/Wed
                predicted_change -= 15.0
                factors.append("Flying Tue/Wed could save ~10%")
                
        if day_of_week in [1, 2]: # Tue, Wed
            factors.append("Mid-week savings detected")
            if advice == "monitor":
                advice = "buy_now" # Good time
                
        # 3. Seasonality (Northern Hemisphere)
        if month in [6, 7, 8, 12]: # Summer/Xmas
            factors.append("High season demand")
            if advice == "wait":
                advice = "monitor" # Don't wait too long in high season
                predicted_change += 10.0
                
        return PriceReasoning(
            advice=advice,
            confidence_score=min(confidence, 0.95),
            predicted_change_usd=predicted_change,
            factors=factors
        )
