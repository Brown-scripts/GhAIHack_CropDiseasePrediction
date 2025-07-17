import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Example: search for shops like agricultural stores within 10km
def find_nearby_shops(lat, lon, radius=10000):
    query = f"""
    [out:json];
    (
      node["shop"="agrarian"](around:{radius},{lat},{lon});
      node["shop"="farm"](around:{radius},{lat},{lon});
      node["amenity"="pharmacy"](around:{radius},{lat},{lon});
    );
    out center;
    """
    response = requests.post(OVERPASS_URL, data={"data": query})
    
    if response.status_code == 200:
        elements = response.json().get("elements", [])
        results = []
        for el in elements:
            name = el.get("tags", {}).get("name", "Unknown Shop")
            results.append({
                "name": name,
                "latitude": el.get("lat"),
                "longitude": el.get("lon"),
                "type": el.get("tags", {}).get("shop") or el.get("tags", {}).get("amenity")
            })
        return results
    return []
