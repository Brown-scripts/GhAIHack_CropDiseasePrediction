"""
Configuration settings
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Configuration
    app_name: str = Field(default="Crop Disease Treatment Recommendation API", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=False, description="Auto-reload on code changes")
    
    # Redis Configuration
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis database number")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    redis_enabled: bool = Field(default=True, description="Enable Redis caching")
    
    # Cache Configuration
    cache_ttl_default: int = Field(default=3600, description="Default cache TTL in seconds")
    cache_ttl_disease_info: int = Field(default=86400, description="Disease info cache TTL (24 hours)")
    cache_ttl_suppliers: int = Field(default=1800, description="Suppliers cache TTL (30 minutes)")
    cache_ttl_prices: int = Field(default=900, description="Prices cache TTL (15 minutes)")
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, description="Rate limit requests per minute")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")
    
    # External APIs
    nominatim_base_url: str = Field(default="https://nominatim.openstreetmap.org", description="Nominatim API base URL")
    overpass_base_url: str = Field(default="https://overpass-api.de/api/interpreter", description="Overpass API base URL")
    
    # Scraping Configuration
    scraping_timeout: int = Field(default=30, description="Scraping request timeout in seconds")
    scraping_delay: float = Field(default=1.0, description="Delay between scraping requests")
    scraping_retries: int = Field(default=3, description="Number of scraping retries")
    user_agent: str = Field(
        default="CropDiseaseAPI/1.0 (+https://github.com/your-repo)", 
        description="User agent for web scraping"
    )
    
    # Ghana-specific Configuration
    ghana_currency: str = Field(default="GHS", description="Ghana currency code")
    ghana_regions: List[str] = Field(
        default=[
            "Greater Accra", "Ashanti", "Western", "Central", "Eastern", 
            "Northern", "Upper East", "Upper West", "Volta", "Brong Ahafo",
            "Western North", "Ahafo", "Bono", "Bono East", "Oti", "Savannah", "North East"
        ],
        description="Ghana regions for location services"
    )
    
    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json or text)")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    
    # Database Configuration (for future use)
    database_url: Optional[str] = Field(default=None, description="Database URL")
    
    # Security
    api_key: Optional[str] = Field(default=None, description="API key for authentication")
    cors_origins: List[str] = Field(default=["*"], description="CORS allowed origins")
    
    # Disease Categories
    supported_crops: List[str] = Field(
        default=["cashew", "cassava", "maize", "tomato"],
        description="Supported crop types"
    )
    
    cashew_diseases: List[str] = Field(
        default=["anthracnose", "gumosis", "leaf_miner", "red_rust", "healthy"],
        description="Supported cashew diseases"
    )

    cassava_diseases: List[str] = Field(
        default=["bacterial_blight", "brown_spot", "green_mite", "mosaic", "healthy"],
        description="Supported cassava diseases"
    )

    maize_diseases: List[str] = Field(
        default=["fall_armyworm", "grasshopper", "leaf_beetle", "leaf_blight", "leaf_spot", "streak_virus", "healthy"],
        description="Supported maize diseases"
    )

    tomato_diseases: List[str] = Field(
        default=["leaf_blight", "leaf_curl", "septoria_leaf_spot", "verticillium_wilt", "healthy"],
        description="Supported tomato diseases"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_all_diseases() -> dict:
    """Get all supported diseases organized by crop"""
    return {
        "cashew": settings.cashew_diseases,
        "cassava": settings.cassava_diseases,
        "maize": settings.maize_diseases,
        "tomato": settings.tomato_diseases
    }


def is_valid_disease(crop: str, disease: str) -> bool:
    """Check if a disease is valid for a given crop"""
    all_diseases = get_all_diseases()
    return crop.lower() in all_diseases and disease.lower() in all_diseases[crop.lower()]


def get_crop_from_disease(disease: str) -> Optional[str]:
    """Get the crop type from a disease name"""
    disease_lower = disease.lower()
    all_diseases = get_all_diseases()
    
    for crop, diseases in all_diseases.items():
        if disease_lower in [d.lower() for d in diseases]:
            return crop
    return None
