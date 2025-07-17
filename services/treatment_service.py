"""
Comprehensive treatment service for crop disease management
Integrates with disease databases and provides treatment recommendations
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from config.logging import get_logger
from config.settings import settings, get_crop_from_disease, is_valid_disease
from models.request_models import (
    DiseaseInfo, Treatment, RecommendationResponse,
    SeverityLevel, TreatmentType, CropType
)
from data.disease_database import CASHEW_DISEASES, CASSAVA_DISEASES
from data.disease_database_extended import CASSAVA_DISEASES_EXTENDED, MAIZE_DISEASES
from services.cache import get_from_cache, set_to_cache

logger = get_logger("treatment_service")


# Combine all disease databases
ALL_DISEASES = {
    **CASHEW_DISEASES,
    **CASSAVA_DISEASES,
    **CASSAVA_DISEASES_EXTENDED,
    **MAIZE_DISEASES,
    # TODO: Add tomato diseases and remaining maize diseases
}


class TreatmentService:
    """Service for managing disease treatment recommendations"""

    def __init__(self):
        self.diseases_db = ALL_DISEASES
        logger.info(f"TreatmentService initialized with {len(self.diseases_db)} diseases")

    def get_disease_info(self, disease_name: str) -> Optional[DiseaseInfo]:
        """Get detailed disease information"""
        disease_key = disease_name.lower().strip()

        # Check cache first
        cache_key = f"disease_info:{disease_key}"
        cached_info = get_from_cache(cache_key)
        if cached_info:
            logger.debug(f"Disease info retrieved from cache: {disease_key}")
            return cached_info

        # Get from database
        disease_info = self.diseases_db.get(disease_key)
        if disease_info:
            # Cache the result
            set_to_cache(cache_key, disease_info, ttl=settings.cache_ttl_disease_info)
            logger.info(f"Disease info found: {disease_key}")
            return disease_info

        logger.warning(f"Disease not found: {disease_key}")
        return None

    def get_treatments_by_type(self, disease_name: str, treatment_type: Optional[TreatmentType] = None) -> List[Treatment]:
        """Get treatments filtered by type"""
        disease_info = self.get_disease_info(disease_name)
        if not disease_info:
            return []

        treatments = disease_info.treatments
        if treatment_type:
            treatments = [t for t in treatments if t.type == treatment_type]

        return treatments

    def get_organic_treatments(self, disease_name: str) -> List[Treatment]:
        """Get organic treatment options"""
        return self.get_treatments_by_type(disease_name, TreatmentType.ORGANIC)

    def get_chemical_treatments(self, disease_name: str) -> List[Treatment]:
        """Get chemical treatment options"""
        return self.get_treatments_by_type(disease_name, TreatmentType.CHEMICAL)

    def filter_treatments_by_budget(self, treatments: List[Treatment], budget_range: str) -> List[Treatment]:
        """Filter treatments by budget range (e.g., '100-500')"""
        if not budget_range or not treatments:
            return treatments

        try:
            # Parse budget range
            if '-' in budget_range:
                min_budget, max_budget = map(float, budget_range.split('-'))
            else:
                # Single value budget
                max_budget = float(budget_range)
                min_budget = 0

            # Filter treatments within budget
            filtered = []
            for treatment in treatments:
                if treatment.cost_estimate_ghs is not None:
                    if min_budget <= treatment.cost_estimate_ghs <= max_budget:
                        filtered.append(treatment)
                else:
                    # Include treatments without cost estimate
                    filtered.append(treatment)

            return filtered

        except (ValueError, AttributeError) as e:
            logger.warning(f"Invalid budget range format: {budget_range}, error: {e}")
            return treatments

    def get_severity_indicators(self, disease_name: str, severity: SeverityLevel) -> List[str]:
        """Get severity indicators for a disease"""
        disease_info = self.get_disease_info(disease_name)
        if not disease_info:
            return []

        return disease_info.severity_indicators.get(severity.value, [])

    def recommend_treatments(
        self,
        disease_name: str,
        severity: SeverityLevel = SeverityLevel.MODERATE,
        organic_preference: bool = False,
        budget_range: Optional[str] = None
    ) -> List[Treatment]:
        """Get recommended treatments based on criteria"""

        disease_info = self.get_disease_info(disease_name)
        if not disease_info:
            return []

        treatments = disease_info.treatments.copy()

        # Filter by organic preference
        if organic_preference:
            organic_treatments = [t for t in treatments if t.type == TreatmentType.ORGANIC]
            if organic_treatments:
                treatments = organic_treatments
            else:
                # If no organic treatments available, include biological
                bio_treatments = [t for t in treatments if t.type == TreatmentType.BIOLOGICAL]
                treatments = organic_treatments + bio_treatments

        # Filter by budget
        if budget_range:
            treatments = self.filter_treatments_by_budget(treatments, budget_range)

        # Sort by effectiveness and cost
        treatments.sort(key=lambda t: (-t.effectiveness, t.cost_estimate_ghs or 0))

        # Limit based on severity
        if severity == SeverityLevel.LOW:
            treatments = treatments[:2]  # Top 2 treatments for low severity
        elif severity == SeverityLevel.MODERATE:
            treatments = treatments[:3]  # Top 3 treatments for moderate severity
        elif severity in [SeverityLevel.HIGH, SeverityLevel.SEVERE]:
            treatments = treatments[:5]  # More options for severe cases

        logger.info(f"Recommended {len(treatments)} treatments for {disease_name} (severity: {severity})")
        return treatments

    def get_emergency_contacts(self, location: str) -> List[Dict[str, str]]:
        """Get emergency agricultural contacts for the location"""
        # This would typically come from a database or external service
        # For now, return Ghana-specific contacts
        contacts = [
            {
                "name": "Ghana Ministry of Food and Agriculture",
                "phone": "+233-302-663-396",
                "email": "info@mofa.gov.gh",
                "type": "Government Extension Service"
            },
            {
                "name": "CSIR - Plant Genetic Resources Research Institute",
                "phone": "+233-302-777-651",
                "email": "pgrri@csir.gh",
                "type": "Research Institute"
            },
            {
                "name": "Agricultural Development Bank",
                "phone": "+233-302-662-762",
                "email": "info@adbghana.com",
                "type": "Agricultural Finance"
            }
        ]

        # Add region-specific contacts based on location
        if "accra" in location.lower():
            contacts.append({
                "name": "Greater Accra Regional Agriculture Office",
                "phone": "+233-302-666-212",
                "email": "accra.agric@mofa.gov.gh",
                "type": "Regional Extension"
            })

        return contacts

    def get_additional_resources(self, disease_name: str, crop_type: str) -> List[Dict[str, str]]:
        """Get additional resources and information links"""
        resources = [
            {
                "title": "Ghana Agricultural Information Network",
                "url": "https://gain.org.gh",
                "description": "Agricultural information and resources"
            },
            {
                "title": "CABI Crop Protection Compendium",
                "url": "https://www.cabi.org/cpc",
                "description": "Comprehensive pest and disease information"
            },
            {
                "title": "FAO Plant Health Portal",
                "url": "http://www.fao.org/plant-health",
                "description": "International plant health resources"
            }
        ]

        # Add crop-specific resources
        if crop_type == "maize":
            resources.append({
                "title": "IITA Maize Research",
                "url": "https://www.iita.org/cropsnew/maize/",
                "description": "International Institute of Tropical Agriculture - Maize"
            })
        elif crop_type == "cassava":
            resources.append({
                "title": "IITA Cassava Research",
                "url": "https://www.iita.org/cropsnew/cassava/",
                "description": "International Institute of Tropical Agriculture - Cassava"
            })

        return resources

    def get_supported_diseases(self) -> Dict[str, List[str]]:
        """Get all supported diseases organized by crop"""
        crop_diseases = {}
        for disease_name, disease_info in self.diseases_db.items():
            crop = disease_info.crop_type.value
            if crop not in crop_diseases:
                crop_diseases[crop] = []
            crop_diseases[crop].append(disease_name)

        return crop_diseases


# Global service instance
treatment_service = TreatmentService()


def get_treatment_info(disease: str) -> Optional[DiseaseInfo]:
    """Legacy function for backward compatibility"""
    return treatment_service.get_disease_info(disease)
