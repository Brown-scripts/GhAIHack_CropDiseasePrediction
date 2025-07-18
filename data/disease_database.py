"""
Disease database for crop disease treatment recommendations
"""
from typing import Dict, List
from models.request_models import DiseaseInfo, Treatment, TreatmentType, CropType


# Cashew Diseases Database
CASHEW_DISEASES = {
    "anthracnose": DiseaseInfo(
        name="anthracnose",
        crop_type=CropType.CASHEW,
        scientific_name="Colletotrichum gloeosporioides",
        symptoms=[
            "Dark brown to black spots on leaves",
            "Circular lesions with concentric rings",
            "Premature leaf drop",
            "Fruit rot with sunken lesions",
            "Twig dieback in severe cases"
        ],
        causes=[
            "Fungal infection",
            "High humidity and warm temperatures",
            "Poor air circulation",
            "Overhead irrigation",
            "Infected plant debris"
        ],
        prevention_methods=[
            "Proper spacing for air circulation",
            "Avoid overhead watering",
            "Remove infected plant debris",
            "Apply preventive fungicide sprays",
            "Use resistant varieties when available"
        ],
        treatments=[
            Treatment(
                name="Copper-based fungicide",
                type=TreatmentType.CHEMICAL,
                active_ingredients=["Copper hydroxide", "Copper oxychloride"],
                application_method="Foliar spray",
                dosage="2-3g per liter of water",
                frequency="Every 14 days during rainy season",
                precautions=["Wear protective clothing", "Avoid spraying during windy conditions"],
                effectiveness=85.0,
                cost_estimate_ghs=45.0
            ),
            Treatment(
                name="Mancozeb fungicide",
                type=TreatmentType.CHEMICAL,
                active_ingredients=["Mancozeb"],
                application_method="Foliar spray",
                dosage="2.5g per liter of water",
                frequency="Every 10-14 days",
                precautions=["Use protective equipment", "Do not spray before rain"],
                effectiveness=90.0,
                cost_estimate_ghs=35.0
            ),
            Treatment(
                name="Neem oil treatment",
                type=TreatmentType.ORGANIC,
                active_ingredients=["Azadirachtin"],
                application_method="Foliar spray",
                dosage="5ml per liter of water",
                frequency="Weekly application",
                precautions=["Apply in evening to avoid leaf burn"],
                effectiveness=70.0,
                cost_estimate_ghs=25.0
            )
        ],
        severity_indicators={
            "low": ["Few scattered spots on older leaves"],
            "moderate": ["Multiple spots on leaves, some fruit affected"],
            "high": ["Extensive leaf spotting, significant fruit rot"],
            "severe": ["Severe defoliation, major crop loss"]
        },
        economic_impact="Can cause 20-40% yield loss if not managed properly",
        seasonal_occurrence=["Rainy season", "High humidity periods"]
    ),
    
    "gumosis": DiseaseInfo(
        name="gumosis",
        crop_type=CropType.CASHEW,
        scientific_name="Phytophthora spp.",
        symptoms=[
            "Gum exudation from bark",
            "Dark staining on trunk",
            "Bark cracking and peeling",
            "Wilting of branches",
            "Reduced fruit production"
        ],
        causes=[
            "Fungal infection (Phytophthora)",
            "Poor drainage",
            "Mechanical injuries to bark",
            "Waterlogged conditions",
            "Stress factors"
        ],
        prevention_methods=[
            "Improve drainage around trees",
            "Avoid mechanical damage to bark",
            "Proper pruning for air circulation",
            "Apply protective fungicides",
            "Maintain tree vigor"
        ],
        treatments=[
            Treatment(
                name="Metalaxyl + Mancozeb",
                type=TreatmentType.CHEMICAL,
                active_ingredients=["Metalaxyl", "Mancozeb"],
                application_method="Trunk injection or soil drench",
                dosage="2g per liter for soil application",
                frequency="Monthly during wet season",
                precautions=["Avoid contact with skin", "Use proper protective equipment"],
                effectiveness=85.0,
                cost_estimate_ghs=60.0
            ),
            Treatment(
                name="Bordeaux mixture",
                type=TreatmentType.CHEMICAL,
                active_ingredients=["Copper sulfate", "Lime"],
                application_method="Trunk painting",
                dosage="1% solution",
                frequency="Every 2 months",
                precautions=["Prepare fresh solution", "Avoid application during flowering"],
                effectiveness=75.0,
                cost_estimate_ghs=20.0
            )
        ],
        severity_indicators={
            "low": ["Minor gum exudation"],
            "moderate": ["Visible gum flow, some bark damage"],
            "high": ["Extensive gumming, bark cracking"],
            "severe": ["Tree decline, major branch dieback"]
        },
        economic_impact="Can kill trees if not treated, causing 100% loss",
        seasonal_occurrence=["Wet season", "High rainfall periods"]
    ),
    
    "leaf_miner": DiseaseInfo(
        name="leaf_miner",
        crop_type=CropType.CASHEW,
        scientific_name="Eteoryctis gemoniella",
        symptoms=[
            "Serpentine mines in leaves",
            "White or brown tunnels in leaf tissue",
            "Premature leaf drop",
            "Reduced photosynthesis",
            "Stunted growth"
        ],
        causes=[
            "Insect larvae feeding inside leaves",
            "Poor pest management",
            "Favorable weather conditions",
            "Lack of natural predators"
        ],
        prevention_methods=[
            "Regular monitoring",
            "Remove affected leaves",
            "Encourage beneficial insects",
            "Proper sanitation",
            "Use pheromone traps"
        ],
        treatments=[
            Treatment(
                name="Imidacloprid",
                type=TreatmentType.CHEMICAL,
                active_ingredients=["Imidacloprid"],
                application_method="Foliar spray",
                dosage="0.5ml per liter of water",
                frequency="Every 15 days",
                precautions=["Avoid spraying during bee activity", "Use protective clothing"],
                effectiveness=90.0,
                cost_estimate_ghs=40.0
            ),
            Treatment(
                name="Neem-based insecticide",
                type=TreatmentType.ORGANIC,
                active_ingredients=["Azadirachtin"],
                application_method="Foliar spray",
                dosage="5ml per liter of water",
                frequency="Weekly",
                precautions=["Apply in evening hours"],
                effectiveness=75.0,
                cost_estimate_ghs=30.0
            )
        ],
        severity_indicators={
            "low": ["Few mines on scattered leaves"],
            "moderate": ["Multiple mines on many leaves"],
            "high": ["Extensive mining, leaf yellowing"],
            "severe": ["Severe defoliation, tree stress"]
        },
        economic_impact="Can reduce yield by 15-25% through reduced photosynthesis",
        seasonal_occurrence=["Dry season", "Hot weather periods"]
    ),
    
    "red_rust": DiseaseInfo(
        name="red_rust",
        crop_type=CropType.CASHEW,
        scientific_name="Cephaleuros virescens",
        symptoms=[
            "Orange-red spots on leaves",
            "Velvety appearance on leaf surface",
            "Premature leaf yellowing",
            "Reduced tree vigor",
            "Branch dieback in severe cases"
        ],
        causes=[
            "Algal infection",
            "High humidity",
            "Poor air circulation",
            "Wet conditions",
            "Stress factors"
        ],
        prevention_methods=[
            "Improve air circulation through pruning",
            "Reduce humidity around trees",
            "Proper spacing",
            "Avoid overhead irrigation",
            "Maintain tree health"
        ],
        treatments=[
            Treatment(
                name="Copper fungicide",
                type=TreatmentType.CHEMICAL,
                active_ingredients=["Copper hydroxide"],
                application_method="Foliar spray",
                dosage="2g per liter of water",
                frequency="Every 21 days",
                precautions=["Avoid spraying during hot hours", "Use protective equipment"],
                effectiveness=80.0,
                cost_estimate_ghs=35.0
            ),
            Treatment(
                name="Potassium bicarbonate",
                type=TreatmentType.ORGANIC,
                active_ingredients=["Potassium bicarbonate"],
                application_method="Foliar spray",
                dosage="5g per liter of water",
                frequency="Weekly",
                precautions=["Test on small area first"],
                effectiveness=65.0,
                cost_estimate_ghs=15.0
            )
        ],
        severity_indicators={
            "low": ["Few red spots on leaves"],
            "moderate": ["Multiple spots, some leaf yellowing"],
            "high": ["Extensive spotting, significant yellowing"],
            "severe": ["Severe defoliation, branch dieback"]
        },
        economic_impact="Can reduce photosynthesis and weaken trees, affecting long-term productivity",
        seasonal_occurrence=["Humid periods", "Rainy season"]
    ),
    
    "healthy": DiseaseInfo(
        name="healthy",
        crop_type=CropType.CASHEW,
        scientific_name=None,
        symptoms=["No visible disease symptoms", "Healthy green foliage", "Normal growth"],
        causes=[],
        prevention_methods=[
            "Continue good agricultural practices",
            "Regular monitoring",
            "Proper nutrition",
            "Adequate water management",
            "Preventive treatments"
        ],
        treatments=[
            Treatment(
                name="Preventive nutrition",
                type=TreatmentType.CULTURAL,
                active_ingredients=["NPK fertilizer"],
                application_method="Soil application",
                dosage="200g per mature tree",
                frequency="Twice per year",
                precautions=["Apply during rainy season"],
                effectiveness=95.0,
                cost_estimate_ghs=25.0
            )
        ],
        severity_indicators={},
        economic_impact="Optimal productivity expected",
        seasonal_occurrence=["Year-round with proper management"]
    )
}


# Cassava Diseases Database
CASSAVA_DISEASES = {
    "bacterial_blight": DiseaseInfo(
        name="bacterial_blight",
        crop_type=CropType.CASSAVA,
        scientific_name="Xanthomonas axonopodis pv. manihotis",
        symptoms=[
            "Angular leaf spots with yellow halos",
            "Wilting of leaves",
            "Stem cankers",
            "Gum exudation from stems",
            "Plant death in severe cases"
        ],
        causes=[
            "Bacterial infection",
            "High humidity and temperature",
            "Contaminated planting material",
            "Mechanical damage",
            "Poor field sanitation"
        ],
        prevention_methods=[
            "Use disease-free planting material",
            "Proper field sanitation",
            "Avoid mechanical damage",
            "Crop rotation",
            "Remove infected plants"
        ],
        treatments=[
            Treatment(
                name="Copper bactericide",
                type=TreatmentType.CHEMICAL,
                active_ingredients=["Copper hydroxide"],
                application_method="Foliar spray",
                dosage="2.5g per liter of water",
                frequency="Every 14 days",
                precautions=["Use protective equipment", "Avoid spraying during rain"],
                effectiveness=75.0,
                cost_estimate_ghs=40.0
            ),
            Treatment(
                name="Streptomycin sulfate",
                type=TreatmentType.CHEMICAL,
                active_ingredients=["Streptomycin sulfate"],
                application_method="Foliar spray",
                dosage="1g per liter of water",
                frequency="Weekly during outbreak",
                precautions=["Rotate with other bactericides", "Follow withdrawal period"],
                effectiveness=85.0,
                cost_estimate_ghs=55.0
            )
        ],
        severity_indicators={
            "low": ["Few leaf spots"],
            "moderate": ["Multiple spots, some wilting"],
            "high": ["Extensive spotting, stem cankers"],
            "severe": ["Plant death, field spread"]
        },
        economic_impact="Can cause 50-100% yield loss in susceptible varieties",
        seasonal_occurrence=["Rainy season", "High humidity periods"]
    ),

    "brown_spot": DiseaseInfo(
        name="brown_spot",
        crop_type=CropType.CASSAVA,
        scientific_name="Cercospora henningsii",
        symptoms=[
            "Brown circular spots on leaves",
            "Yellow halos around spots",
            "Premature leaf drop",
            "Reduced photosynthesis",
            "Stunted growth"
        ],
        causes=[
            "Fungal infection",
            "High humidity",
            "Poor air circulation",
            "Nutrient deficiency",
            "Plant stress"
        ],
        prevention_methods=[
            "Improve air circulation",
            "Proper plant spacing",
            "Balanced nutrition",
            "Remove infected leaves",
            "Use resistant varieties"
        ],
        treatments=[
            Treatment(
                name="Mancozeb fungicide",
                type=TreatmentType.CHEMICAL,
                active_ingredients=["Mancozeb"],
                application_method="Foliar spray",
                dosage="2g per liter of water",
                frequency="Every 14 days",
                precautions=["Wear protective clothing", "Avoid drift to water sources"],
                effectiveness=85.0,
                cost_estimate_ghs=35.0
            ),
            Treatment(
                name="Baking soda spray",
                type=TreatmentType.ORGANIC,
                active_ingredients=["Sodium bicarbonate"],
                application_method="Foliar spray",
                dosage="5g per liter of water",
                frequency="Weekly",
                precautions=["Test on small area first", "Apply in cool hours"],
                effectiveness=60.0,
                cost_estimate_ghs=10.0
            )
        ],
        severity_indicators={
            "low": ["Few spots on lower leaves"],
            "moderate": ["Multiple spots, some yellowing"],
            "high": ["Extensive spotting, leaf drop"],
            "severe": ["Severe defoliation, plant stress"]
        },
        economic_impact="Can reduce yield by 20-30% through reduced photosynthesis",
        seasonal_occurrence=["Humid conditions", "Rainy season"]
    ),

    "green_mite": DiseaseInfo(
        name="green_mite",
        crop_type=CropType.CASSAVA,
        scientific_name="Mononychellus tanajoa",
        symptoms=[
            "Chlorotic spots on leaves",
            "Bronzing of leaf surface",
            "Leaf curling and distortion",
            "Premature leaf drop",
            "Reduced plant vigor"
        ],
        causes=[
            "Mite infestation",
            "Hot dry conditions",
            "Lack of natural predators",
            "Poor plant nutrition",
            "Dust accumulation"
        ],
        prevention_methods=[
            "Encourage natural predators",
            "Maintain adequate moisture",
            "Regular monitoring",
            "Proper nutrition",
            "Avoid dust accumulation"
        ],
        treatments=[
            Treatment(
                name="Abamectin",
                type=TreatmentType.CHEMICAL,
                active_ingredients=["Abamectin"],
                application_method="Foliar spray",
                dosage="1ml per liter of water",
                frequency="Every 10 days",
                precautions=["Highly toxic to bees", "Use protective equipment"],
                effectiveness=90.0,
                cost_estimate_ghs=50.0
            ),
            Treatment(
                name="Neem oil + soap",
                type=TreatmentType.ORGANIC,
                active_ingredients=["Neem oil", "Insecticidal soap"],
                application_method="Foliar spray",
                dosage="10ml neem oil + 5ml soap per liter",
                frequency="Every 5 days",
                precautions=["Apply in evening", "Ensure good coverage"],
                effectiveness=75.0,
                cost_estimate_ghs=25.0
            )
        ],
        severity_indicators={
            "low": ["Few chlorotic spots"],
            "moderate": ["Visible bronzing, some curling"],
            "high": ["Extensive bronzing, leaf distortion"],
            "severe": ["Severe defoliation, plant stunting"]
        },
        economic_impact="Can cause 30-50% yield reduction in severe infestations",
        seasonal_occurrence=["Dry season", "Hot weather"]
    )
}
