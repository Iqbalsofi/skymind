"""
Canonical Schema for Travel Decision Engine

This module defines the single source of truth for all itinerary data.
Every provider must map their data to this schema.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CabinClass(str, Enum):
    """Flight cabin classes"""
    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"


class BaggageType(str, Enum):
    """Baggage types"""
    CARRY_ON = "carry_on"
    CHECKED = "checked"
    PERSONAL_ITEM = "personal_item"


class RiskFlag(str, Enum):
    """Risk flags for itineraries"""
    SELF_TRANSFER = "self_transfer"  # Not all on same ticket
    TIGHT_CONNECTION = "tight_connection"  # < 90 min connection
    OVERNIGHT_LAYOVER = "overnight_layover"  # Layover > 12 hours
    SEPARATE_TICKETS = "separate_tickets"  # Multiple bookings required
    AIRPORT_CHANGE = "airport_change"  # Change airports during connection
    LONG_LAYOVER = "long_layover"  # 6-12 hour layover
    RED_EYE = "red_eye"  # Late night departure


class Baggage(BaseModel):
    """Baggage allowance and restrictions"""
    type: BaggageType
    quantity: int = Field(default=0, description="Number of pieces allowed")
    weight_kg: Optional[int] = Field(default=None, description="Weight limit in kg")
    included: bool = Field(default=False, description="Included in price")
    price_usd: Optional[float] = Field(default=None, description="Additional cost")
    restrictions: List[str] = Field(default_factory=list)


class FareRules(BaseModel):
    """Fare change and cancellation rules"""
    changeable: bool = Field(default=False)
    change_fee_usd: Optional[float] = None
    refundable: bool = Field(default=False)
    cancellation_fee_usd: Optional[float] = None
    notes: List[str] = Field(default_factory=list)


class Airport(BaseModel):
    """Airport information"""
    code: str = Field(..., description="IATA airport code")
    name: str
    city: str
    country: str
    timezone: Optional[str] = None


class Leg(BaseModel):
    """Single flight leg/segment"""
    leg_id: str = Field(..., description="Unique leg identifier")
    origin: Airport
    destination: Airport
    departure_time: datetime
    arrival_time: datetime
    duration_minutes: int
    
    # Flight details
    airline: str = Field(..., description="Airline name")
    airline_code: str = Field(..., description="IATA airline code")
    flight_number: str
    aircraft: Optional[str] = None
    cabin_class: CabinClass
    
    # Operational
    operating_airline: Optional[str] = Field(
        default=None, 
        description="Actual operator if codeshare"
    )
    on_time_percent: Optional[float] = Field(
        default=None, 
        description="Historical on-time performance"
    )


class Layover(BaseModel):
    """Connection/layover information"""
    airport: Airport
    duration_minutes: int
    overnight: bool = Field(default=False)
    airport_change: bool = Field(default=False, description="Requires changing airports")
    notes: List[str] = Field(default_factory=list)


class PriceBreakdown(BaseModel):
    """Detailed price breakdown"""
    base_fare_usd: float
    taxes_usd: float
    fees_usd: float = 0.0
    total_usd: float
    currency: str = "USD"
    price_per_traveler: Optional[float] = None
    num_travelers: int = 1


class ProviderMetadata(BaseModel):
    """Provider-specific metadata"""
    provider_name: str
    provider_id: str = Field(..., description="Itinerary ID in provider's system")
    deeplink: str = Field(..., description="Booking URL")
    last_updated: datetime
    trust_score: float = Field(
        default=1.0, 
        ge=0.0, 
        le=1.0, 
        description="Provider reliability score"
    )
    notes: List[str] = Field(default_factory=list)


class Signals(BaseModel):
    """Quality signals for ranking"""
    on_time_proxy: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Aggregated on-time performance"
    )
    airport_quality: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Airport experience rating"
    )
    seat_availability: Optional[str] = Field(
        default=None,
        description="Seats remaining (few, some, many)"
    )
    popularity: Optional[float] = Field(
        default=None,
        description="How often this route is booked"
    )


class ScoreBreakdown(BaseModel):
    """Detailed scoring breakdown"""
    price_score: float = Field(ge=0.0, le=100.0)
    duration_score: float = Field(ge=0.0, le=100.0)
    stops_score: float = Field(ge=0.0, le=100.0)
    layover_score: float = Field(ge=0.0, le=100.0)
    baggage_score: float = Field(ge=0.0, le=100.0)
    risk_score: float = Field(ge=0.0, le=100.0)
    reliability_score: float = Field(ge=0.0, le=100.0)
    
    weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "price": 0.25,
            "duration": 0.20,
            "stops": 0.15,
            "layover": 0.10,
            "baggage": 0.10,
            "risk": 0.15,
            "reliability": 0.05
        }
    )


class Itinerary(BaseModel):
    """
    Canonical itinerary schema - single source of truth
    Every provider must map to this format
    """
    # Identity
    itinerary_id: str = Field(..., description="Unique identifier")
    
    # Flight structure
    legs: List[Leg] = Field(..., min_items=1, description="Flight segments")
    layovers: List[Layover] = Field(default_factory=list)
    
    # Metadata
    num_stops: int
    total_duration_minutes: int
    is_direct: bool = Field(default=False)
    
    # Pricing
    price: PriceBreakdown
    
    # Terms
    baggage: List[Baggage] = Field(default_factory=list)
    fare_rules: FareRules
    
    # Risk assessment
    risk_flags: List[RiskFlag] = Field(default_factory=list)
    
    # Quality signals
    signals: Signals = Field(default_factory=Signals)
    
    # Provider info
    provider: ProviderMetadata
    
    # Scoring (populated by ranking agent)
    score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    score_breakdown: Optional[ScoreBreakdown] = None
    explanation: Optional[str] = Field(
        default=None,
        description="Human-readable explanation of why this itinerary scored as it did"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "itinerary_id": "itin_abc123",
                "legs": [{
                    "leg_id": "leg_1",
                    "origin": {"code": "JFK", "name": "John F Kennedy Intl", "city": "New York", "country": "USA"},
                    "destination": {"code": "LAX", "name": "Los Angeles Intl", "city": "Los Angeles", "country": "USA"},
                    "departure_time": "2024-06-15T08:00:00",
                    "arrival_time": "2024-06-15T11:30:00",
                    "duration_minutes": 330,
                    "airline": "American Airlines",
                    "airline_code": "AA",
                    "flight_number": "AA123",
                    "cabin_class": "economy"
                }],
                "num_stops": 0,
                "total_duration_minutes": 330,
                "is_direct": True,
                "price": {
                    "base_fare_usd": 250.0,
                    "taxes_usd": 45.0,
                    "total_usd": 295.0
                }
            }
        }


class SearchIntent(BaseModel):
    """User search intent (extracted by Intent Agent)"""
    origins: List[str] = Field(..., description="Origin airport codes")
    destinations: List[str] = Field(..., description="Destination airport codes")
    departure_date: datetime
    return_date: Optional[datetime] = None
    
    # Flexibility
    flexible_dates: bool = Field(default=False)
    date_flexibility_days: int = Field(default=0, ge=0, le=7)
    nearby_airports: bool = Field(default=False)
    
    # Preferences
    cabin_class: CabinClass = CabinClass.ECONOMY
    num_travelers: int = Field(default=1, ge=1, le=9)
    max_stops: Optional[int] = Field(default=None)
    nonstop_only: bool = Field(default=False)
    
    # Constraints
    max_price_usd: Optional[float] = None
    max_duration_hours: Optional[float] = None
    no_red_eyes: bool = Field(default=False)
    no_overnight_layovers: bool = Field(default=False)
    
    # Preference weights (for ranking)
    priority: str = Field(
        default="balanced",
        description="cheap, fast, comfort, or balanced"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "origins": ["JFK"],
                "destinations": ["LAX"],
                "departure_date": "2024-06-15T00:00:00",
                "cabin_class": "economy",
                "num_travelers": 1,
                "priority": "cheap"
            }
        }


class SearchResponse(BaseModel):
    """API search response"""
    itineraries: List[Itinerary]
    total_results: int
    search_intent: SearchIntent
    search_time_ms: float
    providers_queried: List[str]


class ExplanationResponse(BaseModel):
    """Explanation for ranking decisions"""
    itinerary_id: str
    rank: int
    score: float
    category: str = Field(description="best_overall, fastest, cheapest, best_value, etc.")
    explanation: str
    tradeoffs: List[str] = Field(default_factory=list)
    alternatives: List[Dict[str, Any]] = Field(default_factory=list)
