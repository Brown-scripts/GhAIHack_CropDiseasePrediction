"""
Price information API endpoints
Provides current market prices for agricultural treatments and chemicals in Ghana
"""
from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta
import random

from config.logging import get_logger
from config.settings import settings
from models.request_models import PriceRequest, PriceInfo, PricesResponse, ErrorResponse
from services.cache import get_cache, set_cache

logger = get_logger("prices_routes")
router = APIRouter()


@router.get("/prices/{treatment_name}", response_model=PricesResponse)
async def get_treatment_prices(
    treatment_name: str = Path(..., description="Treatment/product name"),
    location: Optional[str] = Query(None, description="Location filter (e.g., 'Accra')"),
    quantity: Optional[str] = Query(None, description="Quantity filter (e.g., '1kg', '500ml')"),
    max_results: int = Query(10, ge=1, le=50, description="Maximum number of price results")
):
    """Get current market prices for a specific treatment"""
    try:
        # Normalize treatment name
        treatment_key = treatment_name.lower().strip()
        
        # Check cache first
        cache_key = f"prices:{treatment_key}:{location}:{quantity}:{max_results}"
        cached_prices = await get_cache(cache_key)
        if cached_prices:
            logger.info(f"Prices retrieved from cache for treatment: {treatment_name}")
            return cached_prices
        
        # Get prices (would normally scrape from various sources)
        prices = await scrape_treatment_prices(treatment_key, location, quantity, max_results)
        
        # Calculate statistics
        price_values = [p.price_ghs for p in prices if p.price_ghs > 0]
        average_price = sum(price_values) / len(price_values) if price_values else None
        price_range = {
            "min": min(price_values) if price_values else None,
            "max": max(price_values) if price_values else None
        }
        
        response = PricesResponse(
            treatment_name=treatment_name,
            location=location,
            prices=prices,
            average_price_ghs=round(average_price, 2) if average_price else None,
            price_range_ghs=price_range if price_range["min"] is not None else None
        )
        
        # Cache the result
        await set_cache(cache_key, response, ttl=settings.cache_ttl_prices)
        
        logger.info(f"Found {len(prices)} prices for {treatment_name}")
        return response
        
    except Exception as e:
        logger.error(f"Error retrieving prices for {treatment_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/prices/compare", response_model=List[PricesResponse])
async def compare_treatment_prices(
    treatments: List[str] = Query(..., description="List of treatment names to compare"),
    location: Optional[str] = Query(None, description="Location filter"),
    max_results_per_treatment: int = Query(5, ge=1, le=20, description="Max results per treatment")
):
    """Compare prices for multiple treatments"""
    try:
        if len(treatments) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 treatments can be compared at once"
            )
        
        results = []
        for treatment in treatments:
            try:
                # Get prices for each treatment
                prices = await scrape_treatment_prices(
                    treatment.lower().strip(), 
                    location, 
                    None, 
                    max_results_per_treatment
                )
                
                # Calculate statistics
                price_values = [p.price_ghs for p in prices if p.price_ghs > 0]
                average_price = sum(price_values) / len(price_values) if price_values else None
                price_range = {
                    "min": min(price_values) if price_values else None,
                    "max": max(price_values) if price_values else None
                }
                
                response = PricesResponse(
                    treatment_name=treatment,
                    location=location,
                    prices=prices,
                    average_price_ghs=round(average_price, 2) if average_price else None,
                    price_range_ghs=price_range if price_range["min"] is not None else None
                )
                
                results.append(response)
                
            except Exception as e:
                logger.warning(f"Error getting prices for {treatment}: {e}")
                # Add empty result for failed treatment
                results.append(PricesResponse(
                    treatment_name=treatment,
                    location=location,
                    prices=[],
                    average_price_ghs=None,
                    price_range_ghs=None
                ))
        
        logger.info(f"Price comparison completed for {len(treatments)} treatments")
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing treatment prices: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/prices/market-trends/{treatment_name}")
async def get_price_trends(
    treatment_name: str = Path(..., description="Treatment name"),
    days: int = Query(30, ge=7, le=365, description="Number of days for trend analysis"),
    location: Optional[str] = Query(None, description="Location filter")
):
    """Get price trends for a treatment over time"""
    try:
        # This would normally query historical price data
        # For now, generate mock trend data
        trends = generate_mock_price_trends(treatment_name, days, location)
        
        logger.info(f"Price trends generated for {treatment_name} over {days} days")
        return trends
        
    except Exception as e:
        logger.error(f"Error retrieving price trends for {treatment_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/prices/suppliers/{supplier_name}")
async def get_supplier_prices(
    supplier_name: str = Path(..., description="Supplier name"),
    product_category: Optional[str] = Query(None, description="Product category filter")
):
    """Get all prices from a specific supplier"""
    try:
        # This would query supplier-specific pricing
        prices = await get_mock_supplier_prices(supplier_name, product_category)
        
        logger.info(f"Retrieved {len(prices)} prices from supplier: {supplier_name}")
        return {
            "supplier_name": supplier_name,
            "product_category": product_category,
            "prices": prices,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving prices from supplier {supplier_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def scrape_treatment_prices(
    treatment_name: str, 
    location: Optional[str], 
    quantity: Optional[str], 
    max_results: int
) -> List[PriceInfo]:
    """Scrape treatment prices from various sources (mock implementation)"""
    
    # This would normally scrape from:
    # - Agricultural supplier websites
    # - Market price databases
    # - Government price monitoring systems
    # - E-commerce platforms
    
    # For now, return mock data based on common treatments
    mock_prices = get_mock_treatment_prices(treatment_name, location, quantity)
    
    # Limit results
    return mock_prices[:max_results]


def get_mock_treatment_prices(treatment_name: str, location: Optional[str], quantity: Optional[str]) -> List[PriceInfo]:
    """Generate mock price data for treatments"""
    
    # Base prices for common treatments (in GHS)
    base_prices = {
        "mancozeb": 35.0,
        "copper": 45.0,
        "imidacloprid": 40.0,
        "neem": 25.0,
        "abamectin": 50.0,
        "chlorantraniliprole": 65.0,
        "metalaxyl": 60.0,
        "streptomycin": 55.0,
        "thiamethoxam": 50.0,
        "malathion": 35.0
    }
    
    # Find base price
    base_price = None
    for key, price in base_prices.items():
        if key in treatment_name.lower():
            base_price = price
            break
    
    if base_price is None:
        base_price = 40.0  # Default price
    
    # Generate mock suppliers and prices
    suppliers = [
        "Yara Ghana Limited",
        "Chemico Limited", 
        "Dizengoff Ghana Limited",
        "Agro-Chemical Association",
        "Local Agricultural Store",
        "Farm Supply Center",
        "Crop Protection Ltd",
        "Ghana Agro Supplies"
    ]
    
    locations = ["Accra", "Kumasi", "Tamale", "Cape Coast", "Tema", "Takoradi"]
    quantities = ["500ml", "1L", "1kg", "5kg", "250ml", "2.5L"]
    
    prices = []
    for i, supplier in enumerate(suppliers):
        # Add price variation
        price_variation = random.uniform(0.8, 1.3)
        price = round(base_price * price_variation, 2)
        
        # Select location
        supplier_location = location if location else random.choice(locations)
        
        # Select quantity
        product_quantity = quantity if quantity else random.choice(quantities)
        
        # Availability status
        availability_options = ["in_stock", "limited_stock", "out_of_stock", "pre_order"]
        availability = random.choice(availability_options)
        
        # Last updated (within last 7 days)
        last_updated = datetime.now() - timedelta(days=random.randint(0, 7))
        
        price_info = PriceInfo(
            product_name=f"{treatment_name.title()} - {product_quantity}",
            price_ghs=price,
            quantity=product_quantity,
            supplier=supplier,
            location=supplier_location,
            last_updated=last_updated.isoformat(),
            availability=availability
        )
        
        prices.append(price_info)
    
    return prices


def generate_mock_price_trends(treatment_name: str, days: int, location: Optional[str]) -> Dict[str, Any]:
    """Generate mock price trend data"""
    
    base_price = 40.0  # Default base price
    trends = []
    
    current_date = datetime.now()
    for i in range(days):
        date = current_date - timedelta(days=days - i - 1)
        
        # Add some realistic price variation
        daily_variation = random.uniform(0.95, 1.05)
        seasonal_factor = 1 + 0.1 * random.sin(i * 2 * 3.14159 / 30)  # Monthly cycle
        
        price = round(base_price * daily_variation * seasonal_factor, 2)
        
        trends.append({
            "date": date.strftime("%Y-%m-%d"),
            "average_price_ghs": price,
            "min_price_ghs": round(price * 0.9, 2),
            "max_price_ghs": round(price * 1.1, 2),
            "sample_size": random.randint(3, 15)
        })
    
    return {
        "treatment_name": treatment_name,
        "location": location,
        "period_days": days,
        "trends": trends,
        "summary": {
            "average_price": round(sum(t["average_price_ghs"] for t in trends) / len(trends), 2),
            "price_volatility": "moderate",
            "trend_direction": "stable"
        }
    }


async def get_mock_supplier_prices(supplier_name: str, product_category: Optional[str]) -> List[PriceInfo]:
    """Get mock prices from a specific supplier"""
    
    products = [
        ("Mancozeb Fungicide", "fungicides", 35.0, "1kg"),
        ("Copper Hydroxide", "fungicides", 45.0, "500g"),
        ("Imidacloprid Insecticide", "insecticides", 40.0, "250ml"),
        ("Neem Oil", "organic", 25.0, "500ml"),
        ("NPK Fertilizer 15-15-15", "fertilizers", 80.0, "50kg"),
        ("Urea Fertilizer", "fertilizers", 120.0, "50kg"),
        ("Glyphosate Herbicide", "herbicides", 55.0, "1L"),
        ("2,4-D Herbicide", "herbicides", 45.0, "1L")
    ]
    
    # Filter by category if specified
    if product_category:
        products = [p for p in products if p[1] == product_category.lower()]
    
    prices = []
    for product_name, category, base_price, quantity in products:
        # Add some price variation
        price = round(base_price * random.uniform(0.95, 1.05), 2)
        
        price_info = PriceInfo(
            product_name=product_name,
            price_ghs=price,
            quantity=quantity,
            supplier=supplier_name,
            location="Accra",  # Default location
            last_updated=datetime.now().isoformat(),
            availability=random.choice(["in_stock", "limited_stock"])
        )
        
        prices.append(price_info)
    
    return prices
