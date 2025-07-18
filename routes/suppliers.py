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
from services.cache import get_cache, set_cache

logger = get_logger("suppliers_routes")
router = APIRouter()


@router.get("/suppliers/nearby", response_model=SuppliersResponse)
async def get_nearby_suppliers(
    location: str = Query(..., description="Location (e.g., 'Accra, Ghana')"),
    radius_km: int = Query(10, ge=1, le=100, description="Search radius in kilometers"),
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
        
        # Convert to Supplier objects and enhance with additional data
        suppliers = []
        for shop in shops:
            supplier = Supplier(
                name=shop.get("name", "Unknown Supplier"),
                address=f"Lat: {shop.get('latitude', 'N/A')}, Lon: {shop.get('longitude', 'N/A')}",
                latitude=shop.get("latitude"),
                longitude=shop.get("longitude"),
                distance_km=calculate_distance(lat, lon, shop.get("latitude", 0), shop.get("longitude", 0)),
                products=get_supplier_products(shop.get("type", "")),
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
        
        # Add some mock verified suppliers for Ghana
        if not suppliers or len(suppliers) < 3:
            mock_suppliers = get_mock_ghana_suppliers(location, lat, lon)
            suppliers.extend(mock_suppliers)
            suppliers.sort(key=lambda s: s.distance_km or float('inf'))
        
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
                latitude=shop.get("latitude"),
                longitude=shop.get("longitude"),
                distance_km=calculate_distance(
                    request.latitude, request.longitude, 
                    shop.get("latitude", 0), shop.get("longitude", 0)
                ),
                products=get_supplier_products(shop.get("type", "")),
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


def get_supplier_products(shop_type: str) -> List[str]:
    """Get products based on shop type"""
    product_mapping = {
        "agrarian": ["fertilizers", "pesticides", "seeds", "farm_tools"],
        "farm": ["fertilizers", "pesticides", "seeds", "farm_tools", "irrigation_equipment"],
        "pharmacy": ["pesticides", "fungicides", "herbicides"],
        "hardware": ["farm_tools", "irrigation_equipment"],
        "garden_centre": ["fertilizers", "pesticides", "seeds", "organic_treatments"]
    }
    
    return product_mapping.get(shop_type, ["general_agricultural_supplies"])


def get_mock_ghana_suppliers(location: str, lat: float, lon: float) -> List[Supplier]:
    """Get mock suppliers for Ghana (would be replaced with real database)"""
    mock_suppliers = [
        Supplier(
            name="Yara Ghana Limited",
            address="Tema Industrial Area, Tema, Ghana",
            phone="+233-303-211-004",
            email="info.ghana@yara.com",
            latitude=5.6698,
            longitude=-0.0166,
            distance_km=calculate_distance(lat, lon, 5.6698, -0.0166),
            products=["fertilizers", "soil_amendments", "crop_nutrition"],
            rating=4.5,
            verified=True
        ),
        Supplier(
            name="Chemico Limited",
            address="Spintex Road, Accra, Ghana",
            phone="+233-302-815-380",
            email="info@chemico.com.gh",
            latitude=5.6037,
            longitude=-0.1870,
            distance_km=calculate_distance(lat, lon, 5.6037, -0.1870),
            products=["pesticides", "fungicides", "herbicides", "insecticides"],
            rating=4.2,
            verified=True
        ),
        Supplier(
            name="Dizengoff Ghana Limited",
            address="East Legon, Accra, Ghana",
            phone="+233-302-511-379",
            email="info@dizengoff.com.gh",
            latitude=5.6500,
            longitude=-0.1500,
            distance_km=calculate_distance(lat, lon, 5.6500, -0.1500),
            products=["irrigation_equipment", "greenhouse_technology", "seeds"],
            rating=4.3,
            verified=True
        ),
        Supplier(
            name="Agro-Chemical Association of Ghana",
            address="Osu, Accra, Ghana",
            phone="+233-302-761-742",
            latitude=5.5500,
            longitude=-0.1800,
            distance_km=calculate_distance(lat, lon, 5.5500, -0.1800),
            products=["pesticides", "fungicides", "herbicides", "fertilizers"],
            rating=4.0,
            verified=True
        )
    ]
    
    # Filter suppliers that are within reasonable distance (< 200km)
    nearby_suppliers = [s for s in mock_suppliers if s.distance_km < 200]
    
    return nearby_suppliers
