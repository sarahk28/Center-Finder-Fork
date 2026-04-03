from serpapi import GoogleSearch
import json
import os
from pprint import pprint

API_KEY = os.environ.get("SERPAPI_KEY")

def search_businesses():
    print("\n=== Google Maps Business Search ===")
    typeOfBusiness = str(input("What type of business are you looking for? "))
    locationOfBusiness = str(input("Where are you looking? "))
    radius = str(input("Search radius in kilometers (press Enter for default): ") or "5")
    
    # Set up the search parameters
    params = {
        "api_key": API_KEY,
        "engine": "google_maps",
        "type": "search",
        "q": f"{typeOfBusiness}",
        "location": locationOfBusiness,
        "hl": "en",
        "z": "13"  # 'z' is the zoom level parameter (13 is a good default for city-level view)
    }

    try:
        # Create the search client and get raw results
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Print the entire raw JSON response
        print("\nRaw JSON response from SerpAPI:")
        pprint(results)
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Make sure you've replaced the API_KEY with your actual SerpApi key.")

# Run the search
if __name__ == "__main__":
    search_businesses()
