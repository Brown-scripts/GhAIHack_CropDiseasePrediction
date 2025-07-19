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
from data.disease_database_extended import CASSAVA_DISEASES_EXTENDED, MAIZE_DISEASES, TOMATO_DISEASES
from services.cache import get_from_cache, set_to_cache

logger = get_logger("treatment_service")


def combine_disease_databases():
    """Combine all disease databases, handling duplicate keys properly"""
    combined = {}

    databases = [
        ("cashew", CASHEW_DISEASES),
        ("cassava", CASSAVA_DISEASES),
        ("cassava", CASSAVA_DISEASES_EXTENDED),
        ("maize", MAIZE_DISEASES),
        ("tomato", TOMATO_DISEASES)
    ]

    for crop_name, database in databases:
        for disease_name, disease_info in database.items():
            if disease_name in combined:
                unique_key = f"{crop_name}_{disease_name}"
                combined[unique_key] = disease_info
            else:
                combined[disease_name] = disease_info

    return combined

ALL_DISEASES = combine_disease_databases()


class TreatmentService:
    """Service for managing disease treatment recommendations"""

    def __init__(self):
        self.diseases_db = ALL_DISEASES
        logger.info(f"TreatmentService initialized with {len(self.diseases_db)} diseases")

    def _normalize_disease_name(self, disease_name: str) -> str:
        """Normalize disease name for consistent matching"""
        normalized = disease_name.lower().strip()
        normalized = normalized.replace(" ", "_")
        normalized = normalized.replace("-", "_").replace(".", "")

        while "__" in normalized:
            normalized = normalized.replace("__", "_")

        normalized = normalized.strip("_")
        return normalized

    def _find_disease_fuzzy(self, disease_name: str) -> Optional[DiseaseInfo]:
        """Find disease using fuzzy matching"""
        normalized_input = self._normalize_disease_name(disease_name)

        # Try exact match first
        disease_info = self.diseases_db.get(normalized_input)
        if disease_info:
            return disease_info

        # Try with crop prefixes
        for crop in ["cashew", "cassava", "maize", "tomato"]:
            prefixed_key = f"{crop}_{normalized_input}"
            disease_info = self.diseases_db.get(prefixed_key)
            if disease_info:
                return disease_info

        # Try fuzzy matching - check if input is contained in any disease name
        for db_key, disease_info in self.diseases_db.items():
            db_key_normalized = self._normalize_disease_name(db_key)

            # Check if input matches the database key (removing crop prefix if present)
            clean_db_key = db_key_normalized
            for crop in ["cashew", "cassava", "maize", "tomato"]:
                if clean_db_key.startswith(f"{crop}_"):
                    clean_db_key = clean_db_key[len(f"{crop}_"):]
                    break

            # Check various matching patterns
            if (normalized_input == clean_db_key or
                normalized_input in clean_db_key or
                clean_db_key in normalized_input or
                normalized_input.replace("_", "") == clean_db_key.replace("_", "")):
                return disease_info

        # Try partial matching with original disease name from DiseaseInfo
        for disease_info in self.diseases_db.values():
            original_name = self._normalize_disease_name(disease_info.name)
            if (normalized_input == original_name or
                normalized_input in original_name or
                original_name in normalized_input):
                return disease_info

        return None

    def get_disease_info(self, disease_name: str) -> Optional[DiseaseInfo]:
        """Get detailed disease information with fuzzy matching"""
        original_input = disease_name
        disease_key = self._normalize_disease_name(disease_name)

        # Check cache first
        cache_key = f"disease_info:{disease_key}"
        cached_info = get_from_cache(cache_key)
        if cached_info:
            logger.debug(f"Disease info retrieved from cache: {disease_key}")
            return cached_info

        # Try fuzzy matching
        disease_info = self._find_disease_fuzzy(disease_name)

        if disease_info:
            # Cache the result
            set_to_cache(cache_key, disease_info, ttl=settings.cache_ttl_disease_info)
            logger.info(f"Disease info found: '{original_input}' -> {disease_info.name} ({disease_info.crop_type.value})")
            return disease_info

        logger.warning(f"Disease not found: '{original_input}' (normalized: '{disease_key}')")
        return None

    def get_disease_suggestions(self, disease_name: str, max_suggestions: int = 5) -> List[str]:
        """Get suggestions for similar disease names"""
        normalized_input = self._normalize_disease_name(disease_name)
        suggestions = []

        # Get all disease names (clean versions)
        all_diseases = []
        for db_key, disease_info in self.diseases_db.items():
            # Use the original disease name from DiseaseInfo
            clean_name = disease_info.name
            all_diseases.append(clean_name)

        # Remove duplicates and sort
        unique_diseases = sorted(list(set(all_diseases)))

        # Find similar diseases using various matching strategies
        scored_suggestions = []

        for disease in unique_diseases:
            normalized_disease = self._normalize_disease_name(disease)
            score = 0

            # Exact match (shouldn't happen if we're here, but just in case)
            if normalized_input == normalized_disease:
                score = 100
            # Substring match
            elif normalized_input in normalized_disease or normalized_disease in normalized_input:
                score = 80
            # Partial word match
            elif any(word in normalized_disease for word in normalized_input.split("_")):
                score = 60
            # Similar length and some common characters
            elif abs(len(normalized_input) - len(normalized_disease)) <= 3:
                common_chars = set(normalized_input) & set(normalized_disease)
                if len(common_chars) >= min(3, len(normalized_input) // 2):
                    score = 40

            if score > 0:
                scored_suggestions.append((disease, score))

        # Sort by score and return top suggestions
        scored_suggestions.sort(key=lambda x: x[1], reverse=True)
        suggestions = [disease for disease, score in scored_suggestions[:max_suggestions]]

        return suggestions

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

            # Filter treatments within budget - only apply upper limit
            # Include all treatments that cost less than max_budget
            filtered = []
            for treatment in treatments:
                if treatment.cost_estimate_ghs is not None:
                    if treatment.cost_estimate_ghs <= max_budget:
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
        organic_preference: bool = False
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
        """Get all supported diseases organized by crop with clean names"""
        crop_diseases = {}
        for disease_name, disease_info in self.diseases_db.items():
            crop = disease_info.crop_type.value
            if crop not in crop_diseases:
                crop_diseases[crop] = []

            # Clean up disease name (remove crop prefix if present)
            clean_name = disease_name
            if disease_name.startswith(f"{crop}_"):
                clean_name = disease_name[len(f"{crop}_"):]

            crop_diseases[crop].append(clean_name)

        return crop_diseases


# Global service instance
treatment_service = TreatmentService()


def get_treatment_info(disease: str) -> Optional[DiseaseInfo]:
    """Legacy function for backward compatibility"""
    return treatment_service.get_disease_info(disease)
