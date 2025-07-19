import requests
import re
from typing import List, Dict, Optional

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

def find_nearby_shops(lat, lon, radius=10000):
    """
    Enhanced OSM shop finder with better data extraction
    """
    # query = f"""
    # [out:json];
    # (
    #   node["shop"="agrarian"](around:{radius},{lat},{lon});
    #   node["shop"="farm"](around:{radius},{lat},{lon});
    #   node["shop"="garden_centre"](around:{radius},{lat},{lon});
    #   node["shop"="hardware"](around:{radius},{lat},{lon});
    #   node["amenity"="pharmacy"](around:{radius},{lat},{lon});
    #   node["shop"="doityourself"](around:{radius},{lat},{lon});
    #   way["shop"="agrarian"](around:{radius},{lat},{lon});
    #   way["shop"="farm"](around:{radius},{lat},{lon});
    #   way["shop"="garden_centre"](around:{radius},{lat},{lon});
    # );
    # out center;
    # """
    query = f"""
        [out:json];
        (
        node["shop"="agrarian"](around:{radius},{lat},{lon});
        node["shop"="garden_centre"](around:{radius},{lat},{lon});
        node["agricultural_supply"="yes"](around:{radius},{lat},{lon});
        node["craft"="agricultural_engineering"](around:{radius},{lat},{lon});
        node["product"~"fertilizer|pesticide|seed|agro|chemical"](around:{radius},{lat},{lon});

        way["shop"="agrarian"](around:{radius},{lat},{lon});
        way["shop"="garden_centre"](around:{radius},{lat},{lon});
        way["agricultural_supply"="yes"](around:{radius},{lat},{lon});
        way["craft"="agricultural_engineering"](around:{radius},{lat},{lon});
        way["product"~"fertilizer|pesticide|seed|agro|chemical"](around:{radius},{lat},{lon});
        );
        out center;
        """

    try:
        response = requests.post(OVERPASS_URL, data={"data": query}, timeout=10)

        if response.status_code == 200:
            elements = response.json().get("elements", [])
            results = []

            for el in elements:
                tags = el.get("tags", {})

                # Extract enhanced shop data
                shop_data = {
                    "name": tags.get("name", "Unknown Shop"),
                    "latitude": el.get("lat") or el.get("center", {}).get("lat"),
                    "longitude": el.get("lon") or el.get("center", {}).get("lon"),
                    "type": tags.get("shop") or tags.get("amenity"),
                    "phone": tags.get("phone"),
                    "email": tags.get("email"),
                    "website": tags.get("website"),
                    "opening_hours": tags.get("opening_hours"),
                    "description": tags.get("description"),
                    "note": tags.get("note"),
                    "brand": tags.get("brand"),
                    "operator": tags.get("operator"),
                }

                # Extract product hints from description/note
                text_for_hints = tags.get("description", "") + " " + tags.get("note", "") + " " + tags.get("name", "")
                product_hints = extract_product_hints_from_text(text_for_hints)
                shop_data["product_hints"] = product_hints

                # Enhanced product mapping applied

                results.append(shop_data)

            return results

    except requests.RequestException as e:
        print(f"Error fetching OSM data: {e}")

    return []


def extract_product_hints_from_text(text: str) -> List[str]:
    """
    Extract product hints from shop descriptions, notes, or names
    """
    if not text:
        return []

    text_lower = text.lower()
    product_hints = []

    # Enhanced agricultural product keywords
    product_keywords = {
        "fertilizer": ["fertilizer", "fertiliser", "manure", "compost", "npk", "nitrogen", "phosphorus", "potassium"],
        "pesticide": ["pesticide", "insecticide", "herbicide", "fungicide", "spray", "chemical", "pest control", "weed killer"],
        "seeds": ["seed", "seeds", "seedling", "planting", "varieties", "hybrid", "certified seed"],
        "tools": ["tools", "equipment", "machinery", "tractor", "plow", "hoe", "cultivator", "harvester"],
        "irrigation": ["irrigation", "watering", "sprinkler", "drip", "pump", "water system", "hose"],
        "animal_feed": ["feed", "fodder", "hay", "grain", "livestock", "cattle feed", "poultry", "animal nutrition"],
        "organic": ["organic", "bio", "natural", "eco", "biological", "sustainable"],
        "greenhouse": ["greenhouse", "polytunnel", "nursery", "growing", "hothouse", "glasshouse"],
        "veterinary": ["veterinary", "vet", "animal health", "livestock medicine", "animal care"],
    }

    # Check for product mentions in text
    for category, keywords in product_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                if category not in product_hints:
                    product_hints.append(category)
                break

    return product_hints
