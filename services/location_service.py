import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

def get_coordinates(location: str):
    params = {
        "q": location,
        "format": "json",
        "limit": 1
    }
    headers = {"User-Agent": "CropRecommendationApp/1.0"}
    response = requests.get(NOMINATIM_URL, params=params, headers=headers)
    
    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return float(data["lat"]), float(data["lon"])
    return None
