"""
Supplier location API endpoints
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
import logging

from config.logging import get_logger
from config.settings import settings
from models.request_models import (
    LocationRequest, Supplier, SuppliersResponse, ErrorResponse
)
from services.location_service import get_coordinates
from services.overpass_service import find_nearby_shops
from services.cache import get_cache, set_cache, clear_cache_pattern

logger = get_logger("suppliers_routes")
router = APIRouter()


@router.get("/suppliers/nearby", response_model=SuppliersResponse)
async def get_nearby_suppliers(
    location: str = Query(..., description="Location (e.g., 'Accra, Ghana')"),
    radius_km: int = Query(10, ge=1, le=1000, description="Search radius in kilometers"),
    product_type: Optional[str] = Query(None, description="Filter by product type (fertilizer, pesticide, etc.)"),
    verified_only: bool = Query(False, description="Show only verified suppliers")
):
    """Find nearby agricultural suppliers based on location"""
    try:
        # Check cache first
        cache_key = f"suppliers:{location}:{radius_km}:{product_type}:{verified_only}"
        cached_suppliers = await get_cache(cache_key)
        if cached_suppliers:
            logger.info(f"Suppliers retrieved from cache for location: {location}")
            return cached_suppliers
        
        # Get coordinates for the location
        coords = get_coordinates(location)
        if not coords:
            raise HTTPException(
                status_code=404,
                detail=f"Could not find coordinates for location: {location}"
            )
        
        lat, lon = coords
        
        # Find nearby shops using Overpass API
        radius_meters = radius_km * 1000
        shops = find_nearby_shops(lat, lon, radius_meters)
        logger.info(f"OSM returned {len(shops)} shops for location {lat},{lon} radius {radius_km}km")
        
        # Convert to Supplier objects and enhance with additional data
        suppliers = []
        for shop in shops:
            supplier = Supplier(
                name=shop.get("name", "Unknown Supplier"),
                address=f"Lat: {shop.get('latitude', 'N/A')}, Lon: {shop.get('longitude', 'N/A')}",
                phone=shop.get("phone"),  # May be None for OSM data
                email=shop.get("email"),  # May be None for OSM data
                latitude=shop.get("latitude"),
                longitude=shop.get("longitude"),
                distance_km=calculate_distance(lat, lon, shop.get("latitude", 0), shop.get("longitude", 0)),
                products=get_supplier_products(
                    shop.get("type", ""),
                    shop.get("product_hints", []),
                    shop.get("name", "")
                ),
                verified=False  # Would be determined by database lookup
            )
            
            # Filter by product type if specified
            if product_type and product_type.lower() not in [p.lower() for p in supplier.products]:
                continue
            
            # Filter by verification status
            if verified_only and not supplier.verified:
                continue
            
            suppliers.append(supplier)
        
        # Sort by distance
        suppliers.sort(key=lambda s: s.distance_km or float('inf'))

        logger.info(f"Final supplier count: {len(suppliers)} (OSM only, no mock data)")
        
        response = SuppliersResponse(
            location=location,
            radius_km=radius_km,
            suppliers=suppliers,
            total_count=len(suppliers)
        )
        
        # Cache the result
        await set_cache(cache_key, response, ttl=settings.cache_ttl_suppliers)
        
        logger.info(f"Found {len(suppliers)} suppliers near {location}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding suppliers near {location}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/suppliers/nearby", response_model=SuppliersResponse)
async def get_nearby_suppliers_by_coordinates(
    request: LocationRequest,
    product_type: Optional[str] = Query(None, description="Filter by product type"),
    verified_only: bool = Query(False, description="Show only verified suppliers")
):
    """Find nearby suppliers using exact coordinates"""
    try:
        # Check cache first
        cache_key = f"suppliers_coords:{request.latitude}:{request.longitude}:{request.radius_km}:{product_type}:{verified_only}"
        cached_suppliers = await get_cache(cache_key)
        if cached_suppliers:
            return cached_suppliers
        
        # Find nearby shops
        radius_meters = request.radius_km * 1000
        shops = find_nearby_shops(request.latitude, request.longitude, radius_meters)
        
        # Convert to suppliers (similar logic as above)
        suppliers = []
        for shop in shops:
            supplier = Supplier(
                name=shop.get("name", "Unknown Supplier"),
                address=f"Lat: {shop.get('latitude', 'N/A')}, Lon: {shop.get('longitude', 'N/A')}",
                phone=shop.get("phone"),  # May be None for OSM data
                email=shop.get("email"),  # May be None for OSM data
                latitude=shop.get("latitude"),
                longitude=shop.get("longitude"),
                distance_km=calculate_distance(
                    request.latitude, request.longitude,
                    shop.get("latitude", 0), shop.get("longitude", 0)
                ),
                products=get_supplier_products(
                    shop.get("type", ""),
                    shop.get("product_hints", []),
                    shop.get("name", "")
                ),
                verified=False
            )
            
            if product_type and product_type.lower() not in [p.lower() for p in supplier.products]:
                continue
            
            if verified_only and not supplier.verified:
                continue
            
            suppliers.append(supplier)
        
        suppliers.sort(key=lambda s: s.distance_km or float('inf'))
        
        response = SuppliersResponse(
            location=f"{request.latitude}, {request.longitude}",
            radius_km=request.radius_km,
            suppliers=suppliers,
            total_count=len(suppliers)
        )
        
        # Cache the result
        await set_cache(cache_key, response, ttl=settings.cache_ttl_suppliers)
        
        logger.info(f"Found {len(suppliers)} suppliers near coordinates")
        return response

    except Exception as e:
        logger.error(f"Error finding suppliers by coordinates: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/cache/clear")
async def clear_suppliers_cache():
    """Clear all suppliers cache entries"""
    try:
        cleared_count = await clear_cache_pattern("suppliers:*")
        logger.info(f"Cleared {cleared_count} supplier cache entries")
        return {"message": f"Cleared {cleared_count} cache entries", "status": "success"}
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")





def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points using Haversine formula"""
    import math
    
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth's radius in kilometers
    r = 6371
    
    return round(c * r, 2)


def get_supplier_products(shop_type: str, product_hints: List[str] = None, shop_name: str = "") -> List[str]:
    """
    Enhanced product mapping using shop type, extracted hints, and shop name analysis
    """
    # Enhanced product mapping with multiple data sources
    # Enhanced product mapping with multiple data sources
    # Conservative base product mapping - only assign products when we're confident
    base_product_mapping = {
        "agrarian": ["fertilizers", "pesticides", "seeds", "farm tools"],
        "farm": ["fertilizers", "pesticides", "seeds", "farm tools", "irrigation equipment", "animal feed"],
        "garden_centre": ["fertilizers", "pesticides", "seeds", "organic treatments", "garden tools"],
        "hardware": ["farm tools", "irrigation equipment", "general supplies"],
        "doityourself": ["farm tools", "irrigation equipment", "general supplies"],
        # Conservative approach: let name/description analysis determine if pharmacy sells agricultural products
        "pharmacy": [],
        "chemist": [],
    }

    # Start with base products for shop type
    products = base_product_mapping.get(shop_type, []).copy()

    # Only add general agricultural supplies for truly unknown shop types (not pharmacies/chemists)
    if not products and shop_type not in ["pharmacy", "chemist"]:
        products = ["general_agricultural_supplies"]

    # Base products assigned

    # Enhance with product hints from OSM data
    if product_hints:
        hint_to_product = {
            "fertilizer": "fertilizers",
            "pesticide": "pesticides",
            "seeds": "seeds",
            "tools": "farm_tools",
            "irrigation": "irrigation equipment",
            "animal_feed": "animal feed",
            "organic": "organic treatments",
            "greenhouse": "greenhouse supplies",
            "veterinary": "veterinary supplies",
        }

        for hint in product_hints:
            product = hint_to_product.get(hint)
            if product and product not in products:
                products.append(product)

    # Analyze shop name for additional product clues
    if shop_name:
        name_lower = shop_name.lower()

        # Enhanced name analysis with more specific keywords
        name_product_mapping = {
            "fertilizers": ["fertilizer", "fertiliser", "manure", "compost", "npk"],
            "pesticides": ["pest", "spray", "chemical", "insecticide", "herbicide", "fungicide"],
            "seeds": ["seed", "nursery", "plant", "seedling"],
            "irrigation_equipment": ["irrigation", "water", "pump", "sprinkler"],
            "organic_treatments": ["organic", "bio", "natural", "eco"],
            "farm_tools": ["tool", "equipment", "machinery", "tractor", "implement"],
            "animal_feed": ["feed", "livestock", "cattle", "poultry", "fodder"],
        }

        # Apply name analysis for all shop types
        for product, keywords in name_product_mapping.items():
            if any(keyword in name_lower for keyword in keywords):
                if product not in products:
                    products.append(product)

        # Special handling for pharmacies - be very conservative
        if shop_type in ["pharmacy", "chemist"]:
            # Only keep agricultural products if the name is very specific
            very_specific_agri_indicators = [
                "agro", "agricultural", "farm", "veterinary", "vet",
                "livestock", "animal health", "agri"
            ]

            # If no specific agricultural indicators, remove agricultural products
            if not any(indicator in name_lower for indicator in very_specific_agri_indicators):
                # Remove agricultural products from regular pharmacies
                products = [p for p in products if p not in ["pesticides", "fungicides", "herbicides", "fertilizers", "seeds"]]

    # Ensure we always have at least some products
    if not products:
        products = ["general_agricultural_supplies"]

    # Limit to reasonable number of products (max 6)
    return products[:6]


# Mock suppliers removed - using only real OSM data
