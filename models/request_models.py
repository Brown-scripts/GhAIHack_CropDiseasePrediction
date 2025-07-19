"""
Request and response models for the API
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum

from config.settings import get_all_diseases, is_valid_disease


class CropType(str, Enum):
    """Supported crop types"""
    CASHEW = "cashew"
    CASSAVA = "cassava"
    MAIZE = "maize"
    TOMATO = "tomato"


class TreatmentType(str, Enum):
    """Treatment types"""
    CHEMICAL = "chemical"
    ORGANIC = "organic"
    BIOLOGICAL = "biological"
    CULTURAL = "cultural"


class SeverityLevel(str, Enum):
    """Disease severity levels"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"


class RecommendRequest(BaseModel):
    """Request model for disease treatment recommendations"""
    disease: str = Field(..., description="Disease name")
    user_location: str = Field(..., description="User location (e.g., 'Accra, Ghana')")
    crop_type: Optional[CropType] = Field(None, description="Crop type (optional, will be inferred from disease)")
    severity: Optional[SeverityLevel] = Field(SeverityLevel.MODERATE, description="Disease severity level")
    organic_preference: bool = Field(False, description="Prefer organic treatments")

    @validator('disease')
    def validate_disease(cls, v):
        """Validate disease name"""
        if not v or not v.strip():
            raise ValueError("Disease name cannot be empty")
        return v.strip().lower()

    @validator('user_location')
    def validate_location(cls, v):
        """Validate user location"""
        if not v or not v.strip():
            raise ValueError("User location cannot be empty")
        return v.strip()


class LocationRequest(BaseModel):
    """Request model for location-based queries"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    radius_km: Optional[int] = Field(10, ge=1, le=1000, description="Search radius in kilometers")


class PriceRequest(BaseModel):
    """Request model for price queries"""
    treatment_name: str = Field(..., description="Treatment/product name")
    location: Optional[str] = Field(None, description="Location for price comparison")
    quantity: Optional[str] = Field(None, description="Quantity (e.g., '1kg', '500ml')")


class Treatment(BaseModel):
    """Treatment information model"""
    name: str = Field(..., description="Treatment name")
    type: TreatmentType = Field(..., description="Treatment type")
    active_ingredients: List[str] = Field(default_factory=list, description="Active ingredients")
    application_method: str = Field(..., description="How to apply the treatment")
    dosage: str = Field(..., description="Recommended dosage")
    frequency: str = Field(..., description="Application frequency")
    precautions: List[str] = Field(default_factory=list, description="Safety precautions")
    effectiveness: float = Field(..., ge=0, le=100, description="Effectiveness percentage")
    cost_estimate_ghs: Optional[float] = Field(None, description="Estimated cost in Ghana Cedis")


class Supplier(BaseModel):
    """Supplier information model"""
    name: str = Field(..., description="Supplier name")
    address: str = Field(..., description="Supplier address")
    phone: Optional[str] = Field(None, description="Phone number")
    email: Optional[str] = Field(None, description="Email address")
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")
    distance_km: Optional[float] = Field(None, description="Distance from user in kilometers")
    products: List[str] = Field(default_factory=list, description="Available products")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Supplier rating")
    verified: bool = Field(False, description="Whether supplier is verified")


class PriceInfo(BaseModel):
    """Price information model"""
    product_name: str = Field(..., description="Product name")
    price_ghs: float = Field(..., description="Price in Ghana Cedis")
    quantity: str = Field(..., description="Quantity/unit")
    supplier: str = Field(..., description="Supplier name")
    location: str = Field(..., description="Location")
    last_updated: str = Field(..., description="Last price update timestamp")
    availability: str = Field("unknown", description="Product availability status")


class DiseaseInfo(BaseModel):
    """Disease information model"""
    name: str = Field(..., description="Disease name")
    crop_type: CropType = Field(..., description="Affected crop type")
    scientific_name: Optional[str] = Field(None, description="Scientific name of pathogen")
    symptoms: List[str] = Field(..., description="Disease symptoms")
    causes: List[str] = Field(default_factory=list, description="Disease causes")
    prevention_methods: List[str] = Field(default_factory=list, description="Prevention methods")
    treatments: List[Treatment] = Field(default_factory=list, description="Available treatments")
    severity_indicators: Dict[str, List[str]] = Field(default_factory=dict, description="Severity level indicators")
    economic_impact: Optional[str] = Field(None, description="Economic impact description")
    seasonal_occurrence: List[str] = Field(default_factory=list, description="Seasons when disease is common")


class RecommendationResponse(BaseModel):
    """Response model for treatment recommendations"""
    disease: str = Field(..., description="Disease name")
    crop_type: str = Field(..., description="Crop type")
    location: str = Field(..., description="User location")
    severity: str = Field(..., description="Disease severity")
    disease_info: DiseaseInfo = Field(..., description="Detailed disease information")
    recommended_treatments: List[Treatment] = Field(..., description="Recommended treatments")
    nearby_suppliers: List[Supplier] = Field(default_factory=list, description="Nearby suppliers")
    price_estimates: List[PriceInfo] = Field(default_factory=list, description="Price estimates")
    total_estimated_cost_ghs: Optional[float] = Field(None, description="Total estimated treatment cost")
    emergency_contacts: List[Dict[str, str]] = Field(default_factory=list, description="Emergency agricultural contacts")
    additional_resources: List[Dict[str, str]] = Field(default_factory=list, description="Additional resources and links")


class SuppliersResponse(BaseModel):
    """Response model for supplier queries"""
    location: str = Field(..., description="Search location")
    radius_km: int = Field(..., description="Search radius")
    suppliers: List[Supplier] = Field(..., description="Found suppliers")
    total_count: int = Field(..., description="Total number of suppliers found")


class PricesResponse(BaseModel):
    """Response model for price queries"""
    treatment_name: str = Field(..., description="Treatment name")
    location: Optional[str] = Field(None, description="Location filter")
    prices: List[PriceInfo] = Field(..., description="Price information")
    average_price_ghs: Optional[float] = Field(None, description="Average price")
    price_range_ghs: Optional[Dict[str, float]] = Field(None, description="Price range (min/max)")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")
