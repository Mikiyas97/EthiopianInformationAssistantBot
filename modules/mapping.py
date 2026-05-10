import requests

def get_coordinates(place_name):
  
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": place_name + ", Ethiopia",
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "EthiopiaInfoBot/1.0"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        data = response.json()

        if data and len(data) > 0:
            return float(data[0]["lat"]), float(data[0]["lon"])
            
    except Exception as e:
        print(f"Error fetching coordinates: {e}")

    return None, None

def get_google_maps_link(user_lat, user_lon, dest_lat, dest_lon):
    """Generates a direction link."""
    return f"https://www.google.com/maps/dir/{user_lat},{user_lon}/{dest_lat},{dest_lon}"