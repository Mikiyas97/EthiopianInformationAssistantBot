import requests
import logging


WIKI_API_URL = "https://en.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "EthiopiaInfoBot/1.0"}

def get_wikipedia_image(place_name):
    """
    Searches Wikipedia for the place_name and returns:
    (image_url, caption)
    Returns (None, None) if not found.
    """
    
    search_params = {
        "action": "query",
        "list": "search",
        "srsearch": place_name + " Ethiopia", 
        "format": "json"
    }

    try:
        search_response = requests.get(WIKI_API_URL, params=search_params, headers=HEADERS, timeout=5)
        search_data = search_response.json()
        
        search_results = search_data.get("query", {}).get("search", [])
        if not search_results:
            return None, None

        title = search_results[0]["title"]

        
        image_params = {
            "action": "query",
            "titles": title,
            "prop": "pageimages",
            "pithumbsize": 800, 
            "format": "json"
        }

        image_response = requests.get(WIKI_API_URL, params=image_params, headers=HEADERS, timeout=5)
        image_data = image_response.json()

        pages = image_data.get("query", {}).get("pages", {})
        
        for page in pages.values():
            if "thumbnail" in page:
                image_url = page["thumbnail"]["source"]
                
                page_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
                caption = f"📍 **{title}**\n🌐 [Read more on Wikipedia]({page_url})"
                return image_url, caption

    except Exception as e:
        print(f"Error fetching Wiki image: {e}")
        return None, None

    return None, None