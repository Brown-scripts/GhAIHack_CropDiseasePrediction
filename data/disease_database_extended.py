"""
Extended disease database for maize and tomato crops
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
    ),

    "leaf_blight": DiseaseInfo(
        name="leaf_blight",
        crop_type=CropType.MAIZE,
        scientific_name="Exserohilum turcicum",
        symptoms=[
            "Large, elongated lesions on leaves",
            "Gray-green to tan colored spots",
            "Lesions with dark borders",
            "Premature leaf death",
            "Reduced grain yield"
        ],
        causes=[
            "Fungal infection",
            "High humidity and moderate temperatures",
            "Poor air circulation",
            "Infected crop residue",
            "Wind-blown spores"
        ],
        prevention_methods=[
            "Use resistant varieties",
            "Crop rotation with non-host crops",
            "Remove crop debris",
            "Improve field drainage",
            "Proper plant spacing"
        ],
        treatments=[
            Treatment(
                name="Propiconazole",
                type=TreatmentType.CHEMICAL,
                active_ingredients=["Propiconazole"],
                application_method="Foliar spray",
                dosage="1ml per liter of water",
                frequency="Every 14 days",
                precautions=["Apply before disease onset", "Use protective equipment"],
                effectiveness=90.0,
                cost_estimate_ghs=55.0
            ),
            Treatment(
                name="Copper-based fungicide",
                type=TreatmentType.CHEMICAL,
                active_ingredients=["Copper hydroxide"],
                application_method="Foliar spray",
                dosage="2g per liter of water",
                frequency="Every 10-14 days",
                precautions=["Avoid application during hot weather"],
                effectiveness=75.0,
                cost_estimate_ghs=40.0
            )
        ],
        severity_indicators={
            "low": ["Few lesions on lower leaves"],
            "moderate": ["Multiple lesions, some upper leaf infection"],
            "high": ["Extensive lesions, significant leaf death"],
            "severe": ["Severe defoliation, major yield loss"]
        },
        economic_impact="Can cause 30-50% yield loss in susceptible varieties",
        seasonal_occurrence=["Humid conditions", "Moderate temperatures"]
    ),

    "leaf_spot": DiseaseInfo(
        name="leaf_spot",
        crop_type=CropType.MAIZE,
        scientific_name="Cercospora zeae-maydis",
        symptoms=[
            "Small, rectangular spots on leaves",
            "Gray centers with dark borders",
            "Spots parallel to leaf veins",
            "Premature leaf yellowing",
            "Reduced photosynthesis"
        ],
        causes=[
            "Fungal infection",
            "High humidity",
            "Warm temperatures",
            "Poor air circulation",
            "Infected plant debris"
        ],
        prevention_methods=[
            "Use resistant varieties",
            "Proper field sanitation",
            "Crop rotation",
            "Balanced fertilization",
            "Avoid overhead irrigation"
        ],
        treatments=[
            Treatment(
                name="Azoxystrobin",
                type=TreatmentType.CHEMICAL,
                active_ingredients=["Azoxystrobin"],
                application_method="Foliar spray",
                dosage="1.5ml per liter of water",
                frequency="Every 14-21 days",
                precautions=["Rotate with other fungicide groups"],
                effectiveness=85.0,
                cost_estimate_ghs=60.0
            ),
            Treatment(
                name="Mancozeb",
                type=TreatmentType.CHEMICAL,
                active_ingredients=["Mancozeb"],
                application_method="Foliar spray",
                dosage="2g per liter of water",
                frequency="Every 14 days",
                precautions=["Use protective clothing"],
                effectiveness=80.0,
                cost_estimate_ghs=35.0
            )
        ],
        severity_indicators={
            "low": ["Few spots on lower leaves"],
            "moderate": ["Multiple spots, some upper leaves affected"],
            "high": ["Extensive spotting, leaf yellowing"],
            "severe": ["Severe leaf damage, reduced yield"]
        },
        economic_impact="Can reduce yield by 20-40% in severe infections",
        seasonal_occurrence=["Warm, humid weather", "Late growing season"]
    ),

    "streak_virus": DiseaseInfo(
        name="streak_virus",
        crop_type=CropType.MAIZE,
        scientific_name="Maize streak virus",
        symptoms=[
            "Yellow streaks parallel to leaf veins",
            "Stunted plant growth",
            "Reduced ear size",
            "Poor grain filling",
            "Plant death in severe cases"
        ],
        causes=[
            "Viral infection",
            "Leafhopper transmission",
            "Infected planting material",
            "Poor vector control",
            "Continuous cropping"
        ],
        prevention_methods=[
            "Use resistant varieties",
            "Control leafhopper vectors",
            "Early planting",
            "Remove infected plants",
            "Crop rotation"
        ],
        treatments=[
            Treatment(
                name="Vector control",
                type=TreatmentType.CHEMICAL,
                active_ingredients=["Imidacloprid"],
                application_method="Seed treatment or foliar spray",
                dosage="0.5ml per liter for foliar",
                frequency="As needed for vector control",
                precautions=["Protect beneficial insects"],
                effectiveness=70.0,
                cost_estimate_ghs=45.0
            ),
            Treatment(
                name="Reflective mulch",
                type=TreatmentType.CULTURAL,
                active_ingredients=["Reflective material"],
                application_method="Ground covering",
                dosage="Cover soil around plants",
                frequency="Once per season",
                precautions=["Secure against wind"],
                effectiveness=60.0,
                cost_estimate_ghs=25.0
            )
        ],
        severity_indicators={
            "low": ["Mild streaking on few plants"],
            "moderate": ["Clear streaking, some stunting"],
            "high": ["Severe streaking, significant stunting"],
            "severe": ["Plant death, field-wide infection"]
        },
        economic_impact="Can cause 50-100% yield loss in susceptible varieties",
        seasonal_occurrence=["Early growing season", "High vector activity"]
    ),

    "healthy": DiseaseInfo(
        name="healthy",
        crop_type=CropType.MAIZE,
        scientific_name=None,
        symptoms=["Healthy green foliage", "Normal growth", "No disease symptoms"],
        causes=[],
        prevention_methods=[
            "Continue good practices",
            "Regular monitoring",
            "Proper nutrition",
            "Adequate water management",
            "Preventive treatments"
        ],
        treatments=[
            Treatment(
                name="Balanced fertilization",
                type=TreatmentType.CULTURAL,
                active_ingredients=["NPK 20-10-10"],
                application_method="Soil application",
                dosage="150kg per hectare",
                frequency="At planting and mid-season",
                precautions=["Apply based on soil test"],
                effectiveness=95.0,
                cost_estimate_ghs=80.0
            )
        ],
        severity_indicators={},
        economic_impact="Optimal yield expected",
        seasonal_occurrence=["Year-round with proper management"]
    )
}


# Tomato Diseases Database
TOMATO_DISEASES = {
    "leaf_blight": DiseaseInfo(
        name="leaf_blight",
        crop_type=CropType.TOMATO,
        scientific_name="Alternaria solani",
        symptoms=[
            "Dark brown spots with concentric rings",
            "Target-like lesions on leaves",
            "Yellowing around spots",
            "Premature leaf drop",
            "Stem and fruit lesions"
        ],
        causes=[
            "Fungal infection",
            "High humidity and warm temperatures",
            "Poor air circulation",
            "Overhead watering",
            "Plant stress"
        ],
        prevention_methods=[
            "Improve air circulation",
            "Avoid overhead watering",
            "Use resistant varieties",
            "Proper plant spacing",
            "Remove infected debris"
        ],
        treatments=[
            Treatment(
                name="Chlorothalonil",
                type=TreatmentType.CHEMICAL,
                active_ingredients=["Chlorothalonil"],
                application_method="Foliar spray",
                dosage="2ml per liter of water",
                frequency="Every 7-14 days",
                precautions=["Use protective equipment", "Avoid drift"],
                effectiveness=85.0,
                cost_estimate_ghs=50.0
            ),
            Treatment(
                name="Baking soda spray",
                type=TreatmentType.ORGANIC,
                active_ingredients=["Sodium bicarbonate"],
                application_method="Foliar spray",
                dosage="5g per liter of water",
                frequency="Weekly",
                precautions=["Test on small area first"],
                effectiveness=65.0,
                cost_estimate_ghs=10.0
            )
        ],
        severity_indicators={
            "low": ["Few spots on lower leaves"],
            "moderate": ["Multiple spots, some defoliation"],
            "high": ["Extensive spotting, significant leaf loss"],
            "severe": ["Severe defoliation, fruit infection"]
        },
        economic_impact="Can reduce yield by 30-60% if not controlled",
        seasonal_occurrence=["Warm, humid conditions", "Rainy season"]
    ),

    "leaf_curl": DiseaseInfo(
        name="leaf_curl",
        crop_type=CropType.TOMATO,
        scientific_name="Tomato leaf curl virus",
        symptoms=[
            "Upward curling of leaves",
            "Yellowing of leaf margins",
            "Stunted plant growth",
            "Reduced fruit size",
            "Poor fruit quality"
        ],
        causes=[
            "Viral infection",
            "Whitefly transmission",
            "High temperatures",
            "Water stress",
            "Poor vector control"
        ],
        prevention_methods=[
            "Control whitefly vectors",
            "Use resistant varieties",
            "Proper irrigation management",
            "Remove infected plants",
            "Use reflective mulches"
        ],
        treatments=[
            Treatment(
                name="Whitefly control spray",
                type=TreatmentType.CHEMICAL,
                active_ingredients=["Thiamethoxam"],
                application_method="Foliar spray",
                dosage="0.3ml per liter of water",
                frequency="Every 10 days",
                precautions=["Rotate insecticides", "Protect beneficial insects"],
                effectiveness=75.0,
                cost_estimate_ghs=55.0
            ),
            Treatment(
                name="Neem oil treatment",
                type=TreatmentType.ORGANIC,
                active_ingredients=["Neem oil"],
                application_method="Foliar spray",
                dosage="10ml per liter of water",
                frequency="Every 7 days",
                precautions=["Apply in evening hours"],
                effectiveness=60.0,
                cost_estimate_ghs=30.0
            )
        ],
        severity_indicators={
            "low": ["Mild leaf curling"],
            "moderate": ["Noticeable curling, some yellowing"],
            "high": ["Severe curling, stunted growth"],
            "severe": ["Extreme stunting, poor fruit development"]
        },
        economic_impact="Can reduce yield by 40-80% in severe cases",
        seasonal_occurrence=["Hot, dry conditions", "High whitefly activity"]
    ),

    "septoria_leaf_spot": DiseaseInfo(
        name="septoria_leaf_spot",
        crop_type=CropType.TOMATO,
        scientific_name="Septoria lycopersici",
        symptoms=[
            "Small, circular spots with gray centers",
            "Dark brown borders around spots",
            "Black specks in spot centers",
            "Yellowing and dropping of leaves",
            "Bottom-up progression"
        ],
        causes=[
            "Fungal infection",
            "High humidity",
            "Warm temperatures",
            "Overhead watering",
            "Poor air circulation"
        ],
        prevention_methods=[
            "Avoid overhead watering",
            "Improve air circulation",
            "Mulch around plants",
            "Remove lower leaves",
            "Crop rotation"
        ],
        treatments=[
            Treatment(
                name="Copper fungicide",
                type=TreatmentType.CHEMICAL,
                active_ingredients=["Copper sulfate"],
                application_method="Foliar spray",
                dosage="2g per liter of water",
                frequency="Every 10-14 days",
                precautions=["Avoid application during hot weather"],
                effectiveness=80.0,
                cost_estimate_ghs=40.0
            ),
            Treatment(
                name="Organic compost tea",
                type=TreatmentType.ORGANIC,
                active_ingredients=["Beneficial microorganisms"],
                application_method="Foliar spray and soil drench",
                dosage="100ml per liter of water",
                frequency="Weekly",
                precautions=["Use fresh preparation"],
                effectiveness=55.0,
                cost_estimate_ghs=15.0
            )
        ],
        severity_indicators={
            "low": ["Few spots on lower leaves"],
            "moderate": ["Multiple spots, some defoliation"],
            "high": ["Extensive spotting, significant leaf loss"],
            "severe": ["Severe defoliation, plant stress"]
        },
        economic_impact="Can reduce yield by 25-50% through defoliation",
        seasonal_occurrence=["Humid conditions", "Mid to late season"]
    ),

    "verticillium_wilt": DiseaseInfo(
        name="verticillium_wilt",
        crop_type=CropType.TOMATO,
        scientific_name="Verticillium dahliae",
        symptoms=[
            "Yellowing of lower leaves",
            "Wilting during hot days",
            "Brown discoloration in stem",
            "Stunted growth",
            "Plant death in severe cases"
        ],
        causes=[
            "Soil-borne fungal infection",
            "Contaminated soil",
            "Poor drainage",
            "Plant stress",
            "Infected transplants"
        ],
        prevention_methods=[
            "Use resistant varieties",
            "Soil solarization",
            "Crop rotation with non-hosts",
            "Improve soil drainage",
            "Use disease-free transplants"
        ],
        treatments=[
            Treatment(
                name="Soil fumigation",
                type=TreatmentType.CHEMICAL,
                active_ingredients=["Metam sodium"],
                application_method="Soil treatment",
                dosage="Follow label instructions",
                frequency="Pre-planting treatment",
                precautions=["Professional application recommended"],
                effectiveness=85.0,
                cost_estimate_ghs=100.0
            ),
            Treatment(
                name="Beneficial microorganisms",
                type=TreatmentType.BIOLOGICAL,
                active_ingredients=["Trichoderma spp."],
                application_method="Soil drench",
                dosage="5g per liter of water",
                frequency="Monthly",
                precautions=["Store in cool, dry place"],
                effectiveness=65.0,
                cost_estimate_ghs=45.0
            )
        ],
        severity_indicators={
            "low": ["Mild yellowing of lower leaves"],
            "moderate": ["Noticeable wilting, some stunting"],
            "high": ["Severe wilting, significant stunting"],
            "severe": ["Plant death, field spread"]
        },
        economic_impact="Can cause 50-100% plant loss in infected fields",
        seasonal_occurrence=["Warm soil conditions", "Stressed plants"]
    ),

    "healthy": DiseaseInfo(
        name="healthy",
        crop_type=CropType.TOMATO,
        scientific_name=None,
        symptoms=["Healthy green foliage", "Normal growth", "Good fruit development"],
        causes=[],
        prevention_methods=[
            "Continue good practices",
            "Regular monitoring",
            "Proper nutrition",
            "Adequate water management",
            "Disease prevention"
        ],
        treatments=[
            Treatment(
                name="Balanced fertilization",
                type=TreatmentType.CULTURAL,
                active_ingredients=["NPK 10-10-10"],
                application_method="Soil application",
                dosage="50g per plant",
                frequency="Every 3 weeks",
                precautions=["Avoid over-fertilization"],
                effectiveness=95.0,
                cost_estimate_ghs=30.0
            )
        ],
        severity_indicators={},
        economic_impact="Optimal yield expected",
        seasonal_occurrence=["Year-round with proper management"]
    )
}
