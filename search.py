import math
from geopy.geocoders import Nominatim
from serpapi import GoogleSearch
from krish import API_KEY


def geocode_location(city: str, state: str, zip_code: str) -> tuple:
    geolocator = Nominatim(user_agent="center-finder-app/1.0")
    query = f"{zip_code} {city}, {state}"
    location = geolocator.geocode(query)
    if location is None:
        location = geolocator.geocode(f"{city}, {state}")
    if location is None:
        raise ValueError(f"Could not geocode location: {city}, {state} {zip_code}")
    return location.latitude, location.longitude


def haversine_miles(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def serpapi_search(query: str, lat: float, lng: float) -> list:
    params = {
        "api_key": API_KEY,
        "engine": "google_maps",
        "type": "search",
        "q": query,
        "ll": f"@{lat},{lng},13z",
        "hl": "en",
    }
    try:
        results = GoogleSearch(params).get_dict()
        return results.get("local_results", [])
    except Exception:
        return []


def extract_result(item: dict) -> dict:
    name = item.get("title", "")
    phone = item.get("phone", "N/A") or "N/A"

    hours_raw = item.get("hours")
    if hours_raw is None:
        hours = "N/A"
    elif isinstance(hours_raw, str):
        hours = hours_raw
    elif isinstance(hours_raw, dict):
        parts = []
        for day, times in hours_raw.items():
            if isinstance(times, list):
                parts.append(f"{day}: {', '.join(times)}")
            else:
                parts.append(f"{day}: {times}")
        hours = "; ".join(parts) if parts else "See listing"
    else:
        hours = "See listing"

    gps = item.get("gps_coordinates")
    return {
        "name": name,
        "phone": phone,
        "hours": hours,
        "address": item.get("address", "N/A") or "N/A",
        "website": item.get("website", "") or "",
        "lat": gps["latitude"] if gps else None,
        "lng": gps["longitude"] if gps else None,
    }


def filter_by_radius(results: list, center_lat: float, center_lng: float, max_miles: float = 15.0) -> list:
    filtered = []
    for r in results:
        if r["lat"] is None or r["lng"] is None:
            continue
        if haversine_miles(center_lat, center_lng, r["lat"], r["lng"]) <= max_miles:
            filtered.append(r)
    return filtered


def search_category(queries: list, lat: float, lng: float, max_results: int = 10, max_miles: float = 15.0) -> list:
    seen = set()
    merged = []
    for query in queries:
        for item in serpapi_search(query, lat, lng):
            result = extract_result(item)
            key = result["name"].strip().lower()
            if key and key not in seen:
                seen.add(key)
                merged.append(result)

    filtered = filter_by_radius(merged, lat, lng, max_miles)
    filtered.sort(key=lambda r: haversine_miles(lat, lng, r["lat"], r["lng"]))
    capped = filtered[:max_results]

    if not capped:
        return [{"name": "No results found", "phone": "", "hours": "", "address": "", "website": "", "distance": ""}]
    return [
        {
            "name": r["name"],
            "phone": r["phone"],
            "hours": r["hours"],
            "address": r["address"],
            "website": r["website"],
            "distance": f"{haversine_miles(lat, lng, r['lat'], r['lng']):.1f} mi",
        }
        for r in capped
    ]


def run_all_searches(lat: float, lng: float, max_miles: float = 15.0) -> dict:
    return {
        "Private Afterschools": search_category(["after school program"], lat, lng, max_miles=max_miles),
        "Elementary Schools": search_category(["elementary school"], lat, lng, max_miles=max_miles),
        "YMCAs + Boys & Girls Clubs": search_category(["YMCA", "Boys and Girls Club"], lat, lng, max_miles=max_miles),
        "Libraries": search_category(["public library"], lat, lng, max_miles=max_miles),
    }
