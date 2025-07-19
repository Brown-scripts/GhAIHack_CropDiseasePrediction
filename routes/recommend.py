"""
Treatment recommendation API endpoints
"""
from fastapi import APIRouter, HTTPException, Path, Depends
from typing import Optional
import logging

from config.logging import get_logger
from config.settings import settings
from models.request_models import (
    RecommendRequest, RecommendationResponse, SeverityLevel, ErrorResponse
)
from services.treatment_service import treatment_service
from services.location_service import get_coordinates
from services.cache import get_cache, set_cache
from routes.suppliers import get_nearby_suppliers
from routes.prices import scrape_treatment_prices

logger = get_logger("recommend_routes")
router = APIRouter()


@router.post("/recommend/{disease_name}", response_model=RecommendationResponse)
async def get_comprehensive_recommendations(
    request: RecommendRequest,
    disease_name: str = Path(..., description="Disease name")
):
    """Get comprehensive treatment recommendations"""
    try:
        # Normalize disease name
        disease_key = disease_name.lower().strip()

        # Check cache first
        cache_key = f"recommend:{disease_key}:{request.user_location}:{request.severity}:{request.organic_preference}"
        cached_recommendation = await get_cache(cache_key)
        if cached_recommendation:
            logger.info(f"Recommendation retrieved from cache for disease: {disease_name}")
            return cached_recommendation

        # Get disease information
        disease_info = treatment_service.get_disease_info(disease_key)
        if not disease_info:
            raise HTTPException(
                status_code=404,
                detail=f"Disease not found: {disease_name}"
            )

        # Get recommended treatments based on criteria
        recommended_treatments = treatment_service.recommend_treatments(
            disease_name=disease_key,
            severity=request.severity or SeverityLevel.MODERATE,
            organic_preference=request.organic_preference
        )

        # Get coordinates for supplier search
        coords = get_coordinates(request.user_location)
        nearby_suppliers = []
        if coords:
            try:
                # Get nearby suppliers
                suppliers_response = await get_nearby_suppliers(
                    location=request.user_location,
                    radius_km=20,  # 20km radius
                    product_type="pesticides",  # General agricultural products
                    verified_only=False
                )
                nearby_suppliers = suppliers_response.suppliers[:5]  # Top 5 suppliers
            except Exception as e:
                logger.warning(f"Could not fetch suppliers: {e}")

        # Get price estimates for recommended treatments
        price_estimates = []
        total_cost = 0.0

        for treatment in recommended_treatments[:3]:  # Get prices for top 3 treatments
            try:
                prices = await scrape_treatment_prices(
                    treatment_name=treatment.name,
                    location=request.user_location,
                    quantity=None,
                    max_results=3
                )
                price_estimates.extend(prices)

                # Add to total cost estimate
                if treatment.cost_estimate_ghs:
                    total_cost += treatment.cost_estimate_ghs

            except Exception as e:
                logger.warning(f"Could not fetch prices for {treatment.name}: {e}")

        # Get emergency contacts
        emergency_contacts = treatment_service.get_emergency_contacts(request.user_location)

        # Get additional resources
        crop_type = disease_info.crop_type.value
        additional_resources = treatment_service.get_additional_resources(disease_name, crop_type)

        # Create comprehensive response
        response = RecommendationResponse(
            disease=disease_info.name,
            crop_type=crop_type,
            location=request.user_location,
            severity=request.severity.value if request.severity else SeverityLevel.MODERATE.value,
            disease_info=disease_info,
            recommended_treatments=recommended_treatments,
            nearby_suppliers=nearby_suppliers,
            price_estimates=price_estimates,
            total_estimated_cost_ghs=round(total_cost, 2) if total_cost > 0 else None,
            emergency_contacts=emergency_contacts,
            additional_resources=additional_resources
        )

        # Cache the result
        await set_cache(cache_key, response, ttl=settings.cache_ttl_default)

        logger.info(f"Comprehensive recommendation generated for {disease_name}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recommendation for {disease_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")



@router.get("/recommend/quick/{disease_name}")
async def get_quick_recommendation(
    disease_name: str = Path(..., description="Disease name"),
    location: str = "Ghana",
    severity: SeverityLevel = SeverityLevel.MODERATE,
    organic_only: bool = False
):
    """Get a quick treatment recommendation without full details"""
    try:
        # Get disease info
        disease_info = treatment_service.get_disease_info(disease_name.lower().strip())
        if not disease_info:
            raise HTTPException(
                status_code=404,
                detail=f"Disease not found: {disease_name}"
            )

        # Get top 3 treatments
        treatments = treatment_service.recommend_treatments(
            disease_name=disease_name.lower().strip(),
            severity=severity,
            organic_preference=organic_only
        )[:3]

        # Quick response
        response = {
            "disease": disease_info.name,
            "crop_type": disease_info.crop_type.value,
            "severity": severity.value,
            "top_treatments": [
                {
                    "name": t.name,
                    "type": t.type.value,
                    "application_method": t.application_method,
                    "dosage": t.dosage
                }
                for t in treatments
            ],
            "key_symptoms": disease_info.symptoms[:3],
            "prevention_tip": disease_info.prevention_methods[0] if disease_info.prevention_methods else None
        }

        logger.info(f"Quick recommendation generated for {disease_name}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating quick recommendation for {disease_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
