import os
import httpx
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from app.core.schema import Itinerary, SearchIntent, Leg, Airport, PriceBreakdown, Baggage, RiskFlag, CabinClass, ProviderMetadata, FareRules
from app.core.cache import cache_manager

logger = logging.getLogger(__name__)

class AmadeusProvider:
    """
    Integration with Amadeus Flight Offers Search API
    """
    
    BASE_URL = "https://test.api.amadeus.com"  # Sandwich/Test env by default
    AUTH_URL = "/v1/security/oauth2/token"
    SEARCH_URL = "/v2/shopping/flight-offers"
    
    def __init__(self):
        self.client_id = os.getenv("AMADEUS_CLIENT_ID")
        self.client_secret = os.getenv("AMADEUS_CLIENT_SECRET")
        self.token = None
        self.token_expiry = datetime.min
        
    async def get_token(self) -> str:
        """Get or refresh OAuth2 access token"""
        if self.token and datetime.now() < self.token_expiry:
            return self.token
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.BASE_URL}{self.AUTH_URL}",
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                response.raise_for_status()
                data = response.json()
                
                self.token = data["access_token"]
                # Set expiry with 60s buffer
                self.token_expiry = datetime.now() + timedelta(seconds=data["expires_in"] - 60)
                return self.token
                
            except Exception as e:
                logger.error(f"Failed to authenticate with Amadeus: {e}")
                raise

    async def search(self, intent: SearchIntent) -> List[Itinerary]:
        """Search for flights using Amadeus API"""
        if not self.client_id or not self.client_secret:
            logger.warning("Amadeus credentials not configured")
            return []
            
        token = await self.get_token()
        
        # Map parameters to Amadeus format
        params = {
            "originLocationCode": intent.origins[0],
            "destinationLocationCode": intent.destinations[0],
            "departureDate": intent.departure_date.strftime("%Y-%m-%d"),
            "adults": intent.num_travelers,
            "travelClass": intent.cabin_class.value.upper(),
            "currencyCode": "USD",
            "max": 20  # Limit results for performance
        }
        
        # Add optional return date
        if intent.return_date:
            params["returnDate"] = intent.return_date.strftime("%Y-%m-%d")
            
        # Add non-stop filter
        if intent.nonstop_only:
            params["nonStop"] = "true"
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}{self.SEARCH_URL}",
                    params=params,
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code != 200:
                    logger.error(f"Amadeus API Error: {response.text}")
                    return []
                    
                data = response.json()
                return self._map_response(data, intent)
                
            except Exception as e:
                logger.error(f"Amadeus search failed: {e}")
                return []

    def _map_response(self, data: Dict[str, Any], intent: SearchIntent) -> List[Itinerary]:
        """Map Amadeus JSON response to internal Itinerary schema"""
        itineraries = []
        dictionaries = data.get("dictionaries", {})
        
        for offer in data.get("data", []):
            try:
                itin = self._map_single_offer(offer, dictionaries)
                itineraries.append(itin)
            except Exception as e:
                logger.warning(f"Failed to map offer {offer.get('id')}: {e}")
                continue
                
        return itineraries
        
    def _map_single_offer(self, offer: Dict[str, Any], dictionaries: Dict[str, Any]) -> Itinerary:
        """Map a single flight offer to Itinerary object"""
        legs = []
        total_duration = 0
        
        # Amadeus separates "itineraries" (direction) and "segments" (legs)
        # For one-way, there's 1 itinerary. For round-trip, there are 2.
        # We flatten this for our schema or handle per leg?
        # Our schema expects a list of Legs.
        
        for flight_itin in offer["itineraries"]:
            # duration format is PT2H30M. Need to parse.
            # We'll calculate total duration from segments for accuracy or use theirs
            pass 
            
            for segment in flight_itin["segments"]:
                # Map segment to Leg
                departure = segment["departure"]
                arrival = segment["arrival"]
                
                leg = Leg(
                    leg_id=f"{offer['id']}-{segment['id']}",
                    origin=Airport(
                        code=departure["iataCode"],
                        name=dictionaries.get("locations", {}).get(departure["iataCode"], {}).get("cityCode", departure["iataCode"]), # Fallback
                        city=dictionaries.get("locations", {}).get(departure["iataCode"], {}).get("cityCode", "Unknown"),
                        country="Unknown" # Amadeus dictionaries don't always give full country name easily
                    ),
                    destination=Airport(
                        code=arrival["iataCode"],
                        name=dictionaries.get("locations", {}).get(arrival["iataCode"], {}).get("cityCode", arrival["iataCode"]),
                        city=dictionaries.get("locations", {}).get(arrival["iataCode"], {}).get("cityCode", "Unknown"),
                        country="Unknown"
                    ),
                    departure_time=datetime.fromisoformat(departure["at"]),
                    arrival_time=datetime.fromisoformat(arrival["at"]),
                    duration_minutes=self._parse_duration(segment["duration"]),
                    airline=dictionaries.get("carriers", {}).get(segment["carrierCode"], segment["carrierCode"]),
                    airline_code=segment["carrierCode"],
                    flight_number=f"{segment['carrierCode']}{segment['number']}",
                    cabin_class=CabinClass.ECONOMY, # Default map, refine later
                    aircraft=segment.get("aircraft", {}).get("code")
                )
                legs.append(leg)
                total_duration += leg.duration_minutes

        # Price
        price_total = float(offer["price"]["total"])
        price_base = float(offer["price"]["base"])
        
        return Itinerary(
            itinerary_id=f"amd_{offer['id']}",
            legs=legs,
            num_stops=len(legs) - 1, # Rough estimate per direction
            total_duration_minutes=total_duration, # This is sum of flight times, excludes layovers if not careful.
            # Better: arrival of last leg - departure of first leg
            is_direct=len(legs) == 1,
            price=PriceBreakdown(
                base_fare_usd=price_base,
                taxes_usd=price_total - price_base,
                total_usd=price_total,
                currency=offer["price"]["currency"]
            ),
            fare_rules=FareRules(
                changeable=True, # Default (safe)
                refundable=False,
                change_fee_usd=0.0
            ),
            provider=ProviderMetadata(
                provider_name="Amadeus",
                provider_id=offer["id"],
                deeplink="https://www.amadeus.com", # Placeholder
                last_updated=datetime.now()
            )
        )

    def _parse_duration(self, pt_duration: str) -> int:
        """Parse ISO 8601 duration (PT2H30M) to minutes"""
        # Simple parsing logic or use isodate library
        # For now, minimal implementation
        import re
        hours = 0
        minutes = 0
        match = re.search(r'(\d+)H', pt_duration)
        if match:
            hours = int(match.group(1))
        match = re.search(r'(\d+)M', pt_duration)
        if match:
             minutes = int(match.group(1))
        return hours * 60 + minutes
