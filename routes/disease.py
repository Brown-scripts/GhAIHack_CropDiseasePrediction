"""
Disease information API endpoints
"""
from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional, Dict, Any
import logging

from config.logging import get_logger
from config.settings import settings
from models.request_models import DiseaseInfo, ErrorResponse, CropType
from services.treatment_service import treatment_service
from services.cache import get_cache, set_cache

logger = get_logger("disease_routes")
router = APIRouter()


@router.get("/diseases", response_model=Dict[str, List[str]])
async def get_supported_diseases():
    """Get all supported diseases organized by crop type"""
    try:
        # Check cache first
        cache_key = "supported_diseases"
        cached_diseases = await get_cache(cache_key)
        if cached_diseases:
            return cached_diseases

        # Get from service
        diseases = treatment_service.get_supported_diseases()

        # Cache the result
        await set_cache(cache_key, diseases, ttl=settings.cache_ttl_disease_info)

        logger.info("Supported diseases retrieved successfully")
        return diseases

    except Exception as e:
        logger.error(f"Error retrieving supported diseases: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/diseases/{crop_type}", response_model=List[str])
async def get_diseases_by_crop(
    crop_type: CropType = Path(..., description="Crop type")
):
    """Get diseases for a specific crop type"""
    try:
        # Check cache first
        cache_key = f"diseases_by_crop:{crop_type.value}"
        cached_diseases = await get_cache(cache_key)
        if cached_diseases:
            return cached_diseases

        # Get all diseases and filter by crop
        all_diseases = treatment_service.get_supported_diseases()
        crop_diseases = all_diseases.get(crop_type.value, [])

        if not crop_diseases:
            raise HTTPException(
                status_code=404,
                detail=f"No diseases found for crop type: {crop_type.value}"
            )

        # Cache the result
        await set_cache(cache_key, crop_diseases, ttl=settings.cache_ttl_disease_info)

        logger.info(f"Diseases for {crop_type.value} retrieved successfully")
        return crop_diseases

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving diseases for crop {crop_type}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/symptoms/{disease_name}", response_model=Dict[str, Any])
async def get_disease_symptoms(
    disease_name: str = Path(..., description="Disease name"),
    include_severity: bool = Query(False, description="Include severity indicators")
):
    """Get detailed symptoms for a specific disease"""
    try:
        # Normalize disease name
        disease_key = disease_name.lower().strip()

        # Check cache first
        cache_key = f"symptoms:{disease_key}:{include_severity}"
        cached_symptoms = await get_cache(cache_key)
        if cached_symptoms:
            return cached_symptoms

        # Get disease info
        disease_info = treatment_service.get_disease_info(disease_key)
        if not disease_info:
            suggestions = treatment_service.get_disease_suggestions(disease_name)
            suggestion_text = ""
            if suggestions:
                suggestion_text = f" Did you mean: {', '.join(suggestions[:3])}?"

            raise HTTPException(
                status_code=404,
                detail=f"Disease not found: {disease_name}.{suggestion_text} Use GET /diseases to see all supported diseases."
            )

        # Prepare response
        response = {
            "disease_name": disease_info.name,
            "crop_type": disease_info.crop_type.value,
            "scientific_name": disease_info.scientific_name,
            "symptoms": disease_info.symptoms,
            "causes": disease_info.causes,
            "prevention_methods": disease_info.prevention_methods,
            "economic_impact": disease_info.economic_impact,
            "seasonal_occurrence": disease_info.seasonal_occurrence
        }

        # Include severity indicators if requested
        if include_severity:
            response["severity_indicators"] = disease_info.severity_indicators

        # Cache the result
        await set_cache(cache_key, response, ttl=settings.cache_ttl_disease_info)

        logger.info(f"Symptoms for {disease_name} retrieved successfully")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving symptoms for disease {disease_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/disease-info/{disease_name}", response_model=DiseaseInfo)
async def get_complete_disease_info(
    disease_name: str = Path(..., description="Disease name")
):
    """Get complete disease information including treatments"""
    try:
        # Normalize disease name
        disease_key = disease_name.lower().strip()

        # Get disease info
        disease_info = treatment_service.get_disease_info(disease_key)
        if not disease_info:
            # Get suggestions for similar disease names
            suggestions = treatment_service.get_disease_suggestions(disease_name)
            suggestion_text = ""
            if suggestions:
                suggestion_text = f" Did you mean: {', '.join(suggestions[:3])}?"

            raise HTTPException(
                status_code=404,
                detail=f"Disease not found: {disease_name}.{suggestion_text} Use GET /diseases to see all supported diseases."
            )

        logger.info(f"Complete disease info for {disease_name} retrieved successfully")
        return disease_info

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving complete disease info for {disease_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Mock disease prediction endpoint (for ML model integration)
@router.post("/predict")
async def predict_disease():
    """Mock disease prediction endpoint - to be replaced with actual ML model"""
    # This would integrate with your ML model
    return {
        "predicted_disease": "anthracnose",
        "crop_type": "cashew",
        "confidence": 0.92,
        "message": "This is a mock prediction. Replace with actual ML model integration."
    }
