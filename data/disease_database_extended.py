"""
Extended disease database - continuation of disease_database.py
Contains maize and tomato diseases
"""
from typing import Dict, List
from models.request_models import DiseaseInfo, Treatment, TreatmentType, CropType


# Complete Cassava Diseases (remaining)
CASSAVA_DISEASES_EXTENDED = {
    "mosaic": DiseaseInfo(
        name="mosaic",
        crop_type=CropType.CASSAVA,
        scientific_name="Cassava mosaic virus",
        symptoms=[
            "Mosaic pattern on leaves",
            "Yellow and green patches",
            "Leaf distortion",
            "Stunted growth",
            "Reduced root yield"
        ],
        causes=[
            "Viral infection",
            "Whitefly transmission",
            "Infected planting material",
            "Poor vector control",
            "Contaminated tools"
        ],
        prevention_methods=[
            "Use virus-free planting material",
            "Control whitefly vectors",
            "Remove infected plants",
            "Disinfect tools",
            "Use resistant varieties"
        ],
        treatments=[
            Treatment(
                name="Whitefly control",
                type=TreatmentType.CHEMICAL,
                active_ingredients=["Imidacloprid"],
                application_method="Foliar spray",
                dosage="0.5ml per liter of water",
                frequency="Every 14 days",
                precautions=["Avoid spraying during flowering", "Protect beneficial insects"],
                effectiveness=70.0,
                cost_estimate_ghs=45.0
            ),
            Treatment(
                name="Reflective mulch",
                type=TreatmentType.CULTURAL,
                active_ingredients=["Aluminum foil mulch"],
                application_method="Ground covering",
                dosage="Cover soil around plants",
                frequency="Once per season",
                precautions=["Secure properly to avoid wind damage"],
                effectiveness=60.0,
                cost_estimate_ghs=30.0
            )
        ],
        severity_indicators={
            "low": ["Mild mosaic pattern"],
            "moderate": ["Clear mosaic, some distortion"],
            "high": ["Severe mosaic, stunting"],
            "severe": ["Extreme stunting, poor root development"]
        },
        economic_impact="Can reduce root yield by 50-90% in susceptible varieties",
        seasonal_occurrence=["Year-round with vector presence"]
    ),
    
    "healthy": DiseaseInfo(
        name="healthy",
        crop_type=CropType.CASSAVA,
        scientific_name=None,
        symptoms=["Healthy green foliage", "Normal growth", "No disease symptoms"],
        causes=[],
        prevention_methods=[
            "Continue good practices",
            "Regular monitoring",
            "Proper nutrition",
            "Disease-free planting material",
            "Vector control"
        ],
        treatments=[
            Treatment(
                name="Balanced fertilization",
                type=TreatmentType.CULTURAL,
                active_ingredients=["NPK 15-15-15"],
                application_method="Soil application",
                dosage="100g per plant",
                frequency="Twice per season",
                precautions=["Apply during rainy season"],
                effectiveness=95.0,
                cost_estimate_ghs=20.0
            )
        ],
        severity_indicators={},
        economic_impact="Optimal yield expected",
        seasonal_occurrence=["Year-round with proper management"]
    )
}


# Maize Diseases Database
MAIZE_DISEASES = {
    "fall_armyworm": DiseaseInfo(
        name="fall_armyworm",
        crop_type=CropType.MAIZE,
        scientific_name="Spodoptera frugiperda",
        symptoms=[
            "Holes in leaves",
            "Feeding damage on whorl",
            "Frass (insect droppings) visible",
            "Stunted growth",
            "Reduced yield"
        ],
        causes=[
            "Insect pest infestation",
            "Favorable weather conditions",
            "Poor pest monitoring",
            "Lack of natural enemies",
            "Continuous cropping"
        ],
        prevention_methods=[
            "Early planting",
            "Regular field monitoring",
            "Encourage natural enemies",
            "Crop rotation",
            "Use resistant varieties"
        ],
        treatments=[
            Treatment(
                name="Chlorantraniliprole",
                type=TreatmentType.CHEMICAL,
                active_ingredients=["Chlorantraniliprole"],
                application_method="Foliar spray or granular",
                dosage="0.4ml per liter of water",
                frequency="Every 10-14 days",
                precautions=["Follow pre-harvest interval", "Avoid drift to water bodies"],
                effectiveness=95.0,
                cost_estimate_ghs=65.0
            ),
            Treatment(
                name="Bt-based biopesticide",
                type=TreatmentType.BIOLOGICAL,
                active_ingredients=["Bacillus thuringiensis"],
                application_method="Foliar spray",
                dosage="2g per liter of water",
                frequency="Every 7 days",
                precautions=["Apply in evening", "Store in cool place"],
                effectiveness=80.0,
                cost_estimate_ghs=40.0
            ),
            Treatment(
                name="Neem + soap solution",
                type=TreatmentType.ORGANIC,
                active_ingredients=["Neem extract", "Soap"],
                application_method="Foliar spray",
                dosage="20ml neem + 5ml soap per liter",
                frequency="Every 5 days",
                precautions=["Apply in cool hours", "Ensure good coverage"],
                effectiveness=65.0,
                cost_estimate_ghs=25.0
            )
        ],
        severity_indicators={
            "low": ["Few holes in leaves"],
            "moderate": ["Visible feeding damage, some frass"],
            "high": ["Extensive leaf damage, whorl feeding"],
            "severe": ["Severe plant damage, yield loss"]
        },
        economic_impact="Can cause 20-70% yield loss if not controlled",
        seasonal_occurrence=["Throughout growing season", "Peak during warm weather"]
    ),
    
    "grasshopper": DiseaseInfo(
        name="grasshopper",
        crop_type=CropType.MAIZE,
        scientific_name="Various Acrididae species",
        symptoms=[
            "Chewed leaf margins",
            "Defoliation",
            "Stem damage",
            "Reduced plant vigor",
            "Yield reduction"
        ],
        causes=[
            "Grasshopper infestation",
            "Dry weather conditions",
            "Poor vegetation management",
            "Migration from other areas",
            "Lack of natural predators"
        ],
        prevention_methods=[
            "Early detection and monitoring",
            "Maintain field hygiene",
            "Encourage natural predators",
            "Use barrier crops",
            "Proper timing of planting"
        ],
        treatments=[
            Treatment(
                name="Malathion",
                type=TreatmentType.CHEMICAL,
                active_ingredients=["Malathion"],
                application_method="Foliar spray",
                dosage="2ml per liter of water",
                frequency="As needed during infestation",
                precautions=["Highly toxic", "Use full protective equipment"],
                effectiveness=90.0,
                cost_estimate_ghs=35.0
            ),
            Treatment(
                name="Diatomaceous earth",
                type=TreatmentType.ORGANIC,
                active_ingredients=["Food grade diatomaceous earth"],
                application_method="Dusting",
                dosage="Apply thin layer on plants",
                frequency="After rain or irrigation",
                precautions=["Use food grade only", "Avoid inhalation"],
                effectiveness=70.0,
                cost_estimate_ghs=20.0
            )
        ],
        severity_indicators={
            "low": ["Minor leaf chewing"],
            "moderate": ["Visible defoliation"],
            "high": ["Significant plant damage"],
            "severe": ["Severe defoliation, plant death"]
        },
        economic_impact="Can cause 30-60% yield loss in severe infestations",
        seasonal_occurrence=["Dry season", "Hot weather periods"]
    ),
    
    "leaf_beetle": DiseaseInfo(
        name="leaf_beetle",
        crop_type=CropType.MAIZE,
        scientific_name="Diabrotica spp.",
        symptoms=[
            "Holes in leaves",
            "Skeletonized leaves",
            "Root damage (larvae)",
            "Stunted growth",
            "Lodging in severe cases"
        ],
        causes=[
            "Beetle infestation",
            "Continuous maize cropping",
            "Poor crop rotation",
            "Favorable weather",
            "Lack of natural enemies"
        ],
        prevention_methods=[
            "Crop rotation",
            "Early planting",
            "Use resistant varieties",
            "Encourage beneficial insects",
            "Proper field sanitation"
        ],
        treatments=[
            Treatment(
                name="Thiamethoxam",
                type=TreatmentType.CHEMICAL,
                active_ingredients=["Thiamethoxam"],
                application_method="Seed treatment or foliar spray",
                dosage="0.3ml per liter for foliar",
                frequency="As needed",
                precautions=["Toxic to bees", "Follow label instructions"],
                effectiveness=85.0,
                cost_estimate_ghs=50.0
            ),
            Treatment(
                name="Kaolin clay",
                type=TreatmentType.ORGANIC,
                active_ingredients=["Kaolin clay"],
                application_method="Foliar spray",
                dosage="50g per liter of water",
                frequency="Weekly during beetle activity",
                precautions=["May affect photosynthesis if overused"],
                effectiveness=60.0,
                cost_estimate_ghs=15.0
            )
        ],
        severity_indicators={
            "low": ["Few holes in leaves"],
            "moderate": ["Visible leaf damage"],
            "high": ["Extensive leaf damage, root feeding"],
            "severe": ["Severe defoliation, plant lodging"]
        },
        economic_impact="Can reduce yield by 15-40% through leaf and root damage",
        seasonal_occurrence=["Growing season", "Warm weather"]
    )
}
