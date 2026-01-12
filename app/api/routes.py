"""
API Routes for SkyMind
Handles search and explanation endpoints
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import List
import time
from datetime import datetime

from app.core.schema import SearchIntent, SearchResponse, Itinerary, ExplanationResponse
from app.services.orchestrator import SearchOrchestrator

router = APIRouter(prefix="/api/v1", tags=["search"])

# Initialize orchestrator
orchestrator = SearchOrchestrator()


@router.post("/search", response_model=SearchResponse)
async def search_flights(search_intent: SearchIntent, request: Request):
    """
    Search for flights based on user intent
    Returns ranked itineraries with scores and explanations
    
    Rate limited to 10 requests/minute per IP
    """
    start_time = time.time()
    
    try:
        # Orchestrate search (with caching)
        itineraries, cache_hit = await orchestrator.search(search_intent)
        
        # Calculate search time
        search_time_ms = (time.time() - start_time) * 1000
        
        response = SearchResponse(
            itineraries=itineraries[:20],  # Top 20
            total_results=len(itineraries),
            search_intent=search_intent,
            search_time_ms=round(search_time_ms, 2),
            providers_queried=["sample_data"]  # Will be dynamic in Phase 2+
        )
        
        # Add cache hit header for monitoring
        return JSONResponse(
            content=response.model_dump(mode='json'),
            headers={
                "X-Cache-Hit": str(cache_hit),
                "X-Search-Time": f"{search_time_ms:.2f}ms"
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain", response_model=List[ExplanationResponse])
async def explain_results(search_intent: SearchIntent):
    """
    Get detailed explanations for top results
    Includes tradeoffs and alternatives
    """
    try:
        # Get search results
        itineraries, _ = await orchestrator.search(search_intent)
        
        if not itineraries:
            return []
        
        # Generate explanations for top 5
        explanations = []
        top_5 = itineraries[:5]
        
        for idx, itin in enumerate(top_5):
            # Determine category
            categories = orchestrator.get_categories(itineraries)
            category = "other"
            
            if categories.get("best_overall") and itin.itinerary_id == categories["best_overall"].itinerary_id:
                category = "best_overall"
            elif categories.get("cheapest") and itin.itinerary_id == categories["cheapest"].itinerary_id:
                category = "cheapest"
            elif categories.get("fastest") and itin.itinerary_id == categories["fastest"].itinerary_id:
                category = "fastest"
            
            # Generate tradeoffs
            tradeoffs = _generate_tradeoffs(itin, itineraries)
            
            # Generate alternatives
            alternatives = _generate_alternatives(itin, itineraries)
            
            explanations.append(ExplanationResponse(
                itinerary_id=itin.itinerary_id,
                rank=idx + 1,
                score=itin.score or 0,
                category=category,
                explanation=itin.explanation or "No explanation available",
                tradeoffs=tradeoffs,
                alternatives=alternatives
            ))
        
        return explanations
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _generate_tradeoffs(itinerary: Itinerary, all_itineraries: List[Itinerary]) -> List[str]:
    """Generate tradeoff suggestions"""
    tradeoffs = []
    
    # Find cheaper options
    cheaper = [i for i in all_itineraries 
               if i.price.total_usd < itinerary.price.total_usd]
    
    if cheaper:
        cheapest = min(cheaper, key=lambda x: x.price.total_usd)
        savings = itinerary.price.total_usd - cheapest.price.total_usd
        extra_time = cheapest.total_duration_minutes - itinerary.total_duration_minutes
        
        if extra_time > 0:
            tradeoffs.append(
                f"Save ${savings:.0f} by accepting {extra_time//60}h {extra_time%60}m longer travel time"
            )
        else:
            tradeoffs.append(f"Save ${savings:.0f} with similar travel time")
    
    # Find faster options
    faster = [i for i in all_itineraries 
              if i.total_duration_minutes < itinerary.total_duration_minutes]
    
    if faster:
        fastest = min(faster, key=lambda x: x.total_duration_minutes)
        time_saved = itinerary.total_duration_minutes - fastest.total_duration_minutes
        extra_cost = fastest.price.total_usd - itinerary.price.total_usd
        
        if extra_cost > 0:
            tradeoffs.append(
                f"Save {time_saved//60}h {time_saved%60}m by paying ${extra_cost:.0f} more"
            )
        else:
            tradeoffs.append(f"Save {time_saved//60}h {time_saved%60}m at similar price")
    
    return tradeoffs[:3]  # Max 3 tradeoffs


def _generate_alternatives(itinerary: Itinerary, all_itineraries: List[Itinerary]) -> List[dict]:
    """Generate alternative suggestions"""
    alternatives = []
    
    # Find direct flights if current has stops
    if not itinerary.is_direct:
        direct = [i for i in all_itineraries if i.is_direct]
        if direct:
            best_direct = min(direct, key=lambda x: x.price.total_usd)
            alternatives.append({
                "type": "direct_flight",
                "itinerary_id": best_direct.itinerary_id,
                "description": f"Direct flight for ${best_direct.price.total_usd:.0f}"
            })
    
    # Find options with better baggage
    has_checked = any(b.included and b.type.value == "checked" for b in itinerary.baggage)
    if not has_checked:
        with_baggage = [i for i in all_itineraries 
                       if any(b.included and b.type.value == "checked" for b in i.baggage)]
        if with_baggage:
            best_baggage = min(with_baggage, key=lambda x: x.price.total_usd)
            alternatives.append({
                "type": "includes_baggage",
                "itinerary_id": best_baggage.itinerary_id,
                "description": f"Includes checked bag for ${best_baggage.price.total_usd:.0f}"
            })
    
    return alternatives[:2]  # Max 2 alternatives
