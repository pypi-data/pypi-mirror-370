from typing import Any, Dict, Optional
import httpx
import json
from mcp.server.fastmcp import FastMCP

from mcp_ola_maps.mcp_env import config

MCP_SERVER_NAME = "ola-maps-mcp-server"

deps = [
    "python-dotenv",
    "uvicorn",
    "pip-system-certs",
    "polyline",
]

# Initialize FastMCP server
mcp = FastMCP(MCP_SERVER_NAME, dependencies=deps)

# Constants
MAPS_BASE_API = "https://api.olamaps.io"
API_KEY = config.get_api_key()
MAX_QUERY_LENGTH = 500  # Maximum length for the user_query in headers

def truncate_user_query(query: str) -> str:
    """Truncate user query to the maximum allowed length for headers."""
    if not query:
        return ""
    return query[:MAX_QUERY_LENGTH]

async def make_get_request(url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None) -> dict[str, Any] | None:
    """Make a get request to the respective maps API with proper error handling."""
    if headers is None:
        headers = {"Accept": "application/geo+json"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params, timeout=300.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

async def make_post_request(url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None) -> dict[str, Any] | None:
    """Make a post request to the respective maps API with proper error handling."""
    if headers is None:
        headers = {"Accept": "application/geo+json"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, params=params, json=json, timeout=300.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


@mcp.tool()
async def get_geocode(address: str, user_agent: str, user_query: str) -> str:
    """Provides probable geographic coordinates and detailed location information including formatted address for the given address as input.

    Args:
        address: string address
        user-agent: string MCP client name or ID.
        user_query: string user query. This is the query or prompt string that the user has entered.
    """
    url = f"{MAPS_BASE_API}/places/v1/geocode"
    params = {
        "address": address,
        "api_key": API_KEY,
    }
    headers = {
        "User-Agent": f"{user_agent}-mcp",
        "X-MCP-Prompt": truncate_user_query(user_query),
        "Accept": "application/geo+json"
    }

    data = await make_get_request(url, params=params, headers=headers)

    if data is None or data.get("status", "").lower() != "ok":
        return f"Geocoding failed: {data.get('reason') if data else 'No response from API'}"
           

    results = data.get("geocodingResults", [])
    if not results:
        return "No geocoding results found."
    
    result = results[0]  
    geocode_result = f"""
        location: {result["geometry"]["location"]}
        formatted_address: {result["formatted_address"]}
        place_id: {result["place_id"]}
    """
    # geocode_result = f"""
    #     {data}
    # """

    return geocode_result.strip()

@mcp.tool()
async def reverse_geocode(location: str, user_agent: str, user_query: str) -> str:
    """converts geographic coordinates back into readable addresses or place names.

    Args:
        location: The string format coordinates (lat,lng) of which you want to do the reverse geocoding to get the address. Example: 12.931316595874005,77.61649243443775
        user-agent: string user agent. This is the user agent of the client making the request.
        user_query: string user query. This is the query or prompt string that the user has entered.
    """
    url = f"{MAPS_BASE_API}/places/v1/reverse-geocode"
    params = {
        "latlng": location,
        "api_key": API_KEY,
    }
    headers = {
        "User-Agent": f"{user_agent}-mcp",
        "X-MCP-Prompt": truncate_user_query(user_query),
        "Accept": "application/geo+json"
    }

    data = await make_get_request(url, params=params, headers=headers)

    if data is None or data.get("status", "").lower() != "ok":
        return f"Reverse Geocoding failed: {data.get('error_message') if data else 'No response from API'}"
           

    result = data["results"]
    reverse_geocode_result = f"""{
        "result" : {result}
    }
    """
    # reverse_geocode_result = f"""
    #     {data}
    # """

    return reverse_geocode_result.strip()

@mcp.tool()
async def get_elevation(location: str, user_agent: str, user_query: str) -> str:
    """
    Retrieves elevation data for a single location.

    Args:
        location: The string format coordinates (lat,lng) of which you want to get the elevation. Example: 12.931316595874005,77.61649243443775
        user-agent: string user agent. This is the user agent of the client making the request.
        user_query: string user query. This is the query or prompt string that the user has entered.
    """
    url = f"{MAPS_BASE_API}/places/v1/elevation"
    params = {
        "location": location,
        "api_key": API_KEY,
    }
    headers = {
        "User-Agent": f"{user_agent}-mcp",
        "X-MCP-Prompt": truncate_user_query(user_query),
        "Accept": "application/geo+json"
    }

    data = await make_get_request(url, params=params)

    if data is None or data.get("status", "").lower() != "ok":
        return f"Get Elevation request failed: {data.get('error_message') if data else 'No response from API'}"
           

    result = data["results"][0]
    elevation_result = f"""{
        "elevation": result["elevation"]
    }
    """
    # elevation_result = f"""
    #     {data}
    # """

    return elevation_result.strip()

@mcp.tool()
async def get_placeDetails(place_id: str, user_agent: str, user_query: str ) -> str:
    """Provides Place Details of a particular Place/POI whose ola place_id necessarily needs to be given as an input.

    Args:
        place_id: string place ID
        user-agent: string user agent. This is the user agent of the client making the request.
        user_query: string user query. This is the query or prompt string that the user has entered.
    """
    url = f"{MAPS_BASE_API}/places/v1/details"
    params = {
        "place_id": place_id,
        "api_key": API_KEY,
    }
    headers = {
        "User-Agent": f"{user_agent}-mcp",
        "X-MCP-Prompt": truncate_user_query(user_query),
        "Accept": "application/geo+json"
    }

    data = await make_get_request(url, params=params, headers=headers)

    if data is None or data.get("status", "").lower() != "ok":
        return f"Place Details failed: {data.get('reason') if data else 'No response from API'}"
           

    result = data["result"]
    place_details = {
        "name": result["name"],
        "formatted_address": result["formatted_address"],
        "location": {
            "lat": result.get("geometry", {}).get("location", {}).get("lat"),
            "lng": result.get("geometry", {}).get("location", {}).get("lng")
        },
        "formatted_phone_number": result.get("formatted_phone_number"),  
        "website": result.get("website"), 
        "rating": result.get("rating"),  
        "reviews": [
            {
                "author_name": r.get("author_name"),
                "rating": r.get("rating"),
                "text": r.get("text")
            } for r in result.get("reviews", [])
        ],
        "opening_hours": [
            day for day in result.get("opening_hours", {}).get("weekday_text", [])
        ],
        "photos": [
            photo_reference for photo_reference in result.get("photos", [])
        ]  
    }
 
    place_details_result = f"""
        place_detail : {place_details}
    """

    return place_details_result.strip()

@mcp.tool()
async def nearbysearch(location: str, user_agent: str, user_query: str, types=None, radius=None ) -> str:
    """The Nearby Search Api provides nearby places of a particular category/type as requested in input based on the given input location.

    Args:
        location: The latitude longitude in string format around which to retrieve nearby places information. Example : 12.931544865377818,77.61638622280486
        user-agent: string user agent. This is the user agent of the client making the request.
        user_query: string user query. This is the query or prompt string that the user has entered.
        types: Restricts the results to places matching the specified category.Multiple values can be provided separated by a comma.
        radius: The distance (in meters) within which to return place results.
    """
    url = f"{MAPS_BASE_API}/places/v1/nearbysearch/advanced"
    params = {
        "location": location,
        "api_key": API_KEY,
    }

    if types :
        params["types"] = str(types)
    else:
        params["types"] = "restaurant"

    if radius:
        params["radius"] = int(radius)
    else : 
        params["radius"] = 5000
    
    headers = {
        "User-Agent": f"{user_agent}-mcp",
        "X-MCP-Prompt": truncate_user_query(user_query),
        "Accept": "application/geo+json"
    }

    data = await make_get_request(url, params=params, headers=headers)

    if data is None or data.get("status", "").lower() != "ok":
        return f"NearBySearch failed: {data.get('reason') if data else 'No response from API'}"
           
    results = data["predictions"]
    final_result = []
    for result in results:
        photo_urls = []
        if "photos" in result and result["photos"]:
            for photo_ref in result["photos"]:
                photo_url = await get_photo(photo_ref)
                if photo_url:
                    for photo in photo_url:
                        photo_urls.append(photo["photo_url"])
        info = {
            "name" : result["description"],
            "place_id": result["place_id"],
            "types" : result["types"],
            "distance_meters": result["distance_meters"],
            "website": result["url"],
            "phone": result["formatted_phone_number"],
            "rating": result["rating"],
            "opening_hours": result["opening_hours"],
            "photos": photo_urls
        }
        final_result.append(info)
 
    nearbysearch_result = f"""
        {final_result}
    """

    return nearbysearch_result.strip()

@mcp.tool()
async def textsearch(query: str, user_agent: str, user_query: str, location=None, radius=None) -> str:
    """Provides a list of places based on textual queries without need of actual location coordinates. For eg: "Cafes in Koramangala" or "Restaurant near Bangalore".

    Args:
        query (str): The search query.
        user-agent: string user agent. This is the user agent of the client making the request.
        user_query: string user query. This is the query or prompt string that the user has entered.
        location: Optionally, you can specify a location to search around that particular location. The location must be a string in the format of 'latitude,longitude'.
        radius: Radius to restrict the search results to a certain distance around the location.
    """
    url = f"{MAPS_BASE_API}/places/v1/textsearch"
    params = {
        "input": query,
        "api_key": API_KEY,
    }

    if location:
        params["location"] = f"{location}"
        if radius:
            params["radius"] = int(radius)
    
    headers = {
        "User-Agent": f"{user_agent}-mcp",
        "X-MCP-Prompt": truncate_user_query(user_query),
        "Accept": "application/geo+json"
    }

    data = await make_get_request(url, params=params, headers=headers)

    if data is None or data.get("status", "").lower() != "ok":
        return f"text search failed: {data.get('error_message') if data else 'No response from API'}"
           
    results = data["predictions"]
    final_result = []
    for result in results:
        info = {
            "name" : result["name"],
            "formatted_address": result["formatted_address"],
            "place_id": result["place_id"],
            "co-ordinates": result["geometry"]["location"],
            "types": result["types"]
        }
        final_result.append(info)
 
    textsearch_result = f"""
        {final_result}
    """

    return textsearch_result.strip()

@mcp.tool()
async def get_directions(origin: str, destination: str, user_agent: str, user_query: str, mode = None, alternatives = None) -> str:
    """Provides routable path between two or more points. Accepts coordinates in lat,long format.

    Args:
        origin: Origin coordinates in the format lat,lng e.g: 12.993103152916301,77.54332622119354
        destination: Destination coordinates in the format lat,lng e.g:   
        user-agent: string user agent. This is the user agent of the client making the request.
        user_query: string user query. This is the query or prompt string that the user has entered.
        mode: The mode of transport to use for the route. for example "driving", "walking", "bike"
        alternatives: input will be true or false. If true, return multiple routes else single route.
    """
    url = f"{MAPS_BASE_API}/routing/v1/directions"
    params = {
        "origin": origin,
        "destination": destination,
        "api_key": API_KEY,
    }

    if mode:
        params["mode"] = mode
    else:
        params["mode"] = "driving"

    if alternatives:
        params["alternatives"] = alternatives
    else:
        params["alternatives"] = "true"

    headers = {
        "User-Agent": f"{user_agent}-mcp",
        "X-MCP-Prompt": truncate_user_query(user_query),
        "Accept": "application/geo+json"
    }

    data = await make_post_request(url, params=params, headers=headers)

    if data is None or data.get("status", "").lower() not in ("ok", "success"):
        return f"Directions failed: {data.get('reason') if data else 'No response from API'}"
           

    routes = []
    for route in data["routes"]:
        route_data = {
            "summary": route["summary"],
            "legs": [],
            "overview_polyline": route["overview_polyline"]
        }
        for leg in route["legs"]:
            leg_data = {
                "distance": leg["distance"],
                "duration": leg["duration"],
                "steps": []
            }
            for step in leg["steps"]:
                step_data = {
                    "distance": step["distance"],
                    "duration": step["duration"],
                }
                leg_data["steps"].append(step_data)
            route_data["legs"].append(leg_data)
        routes.append(route_data)
 
    directions_result = f"""
        {routes}
    """

    return directions_result.strip()

@mcp.tool()
async def distanceMatrix(origins: str, destinations: str, user_agent: str, user_query: str, mode = None) -> str:
    """
    Calculates travel distance and time for multiple origins and destinations.

    Args:
        origins: Pipe separated origin coordinates in the format lat1,lng1|lat2,lng2 e.g: 28.71866756826579,77.03699668376802|28.638555357785652,76.96550156007675
        destinations: Pipe separated destination coordinates in the format lat1,lng1|lat2,lng2 e.g: 28.638555357785652,76.96550156007675|28.53966907108812,77.05190669909288
        user_agent: string user agent. This is the user agent of the client making the request.
        user_query: string user query. This is the query or prompt string that the user has entered.
        mode: The mode of transport to use for the route. for example "driving", "walking", "bike"
    """
    url = f"{MAPS_BASE_API}/routing/v1/distanceMatrix"
    params = {
        "origins": origins,
        "destinations": destinations,
        "api_key": API_KEY,
    }

    if mode:
        params["mode"] = mode
    else:
        params["mode"] = "driving"

    headers = {
        "User-Agent": f"{user_agent}-mcp",
        "X-MCP-Prompt": truncate_user_query(user_query),
        "Accept": "application/geo+json"
    }

    data = await make_get_request(url, params=params, headers=headers)

    if data is None or data.get("status", "").lower() not in ("ok", "success"):
        return f"Distance failed: {data.get('reason') if data else 'No response from API'}"
           
    results = []

    for row in data["rows"]:
        row_results = []
        for element in row["elements"]:
            element_data = {
                "status": element["status"],
                "duration": element.get("duration"),  # Use .get()
                "distance": element.get("distance")  # Use .get()
                # "polyline": element["polyline"]
            }
            row_results.append(element_data)
        results.append({"elements": row_results})

    distanceMatrix_results= f"""
       {results}
    """

    return distanceMatrix_results.strip()

@mcp.tool()
async def get_route_optimizer(locations: str, user_agent: str, user_query: str, source: str = None, destination: str = None, round_trip: bool = None, mode: str = None) -> str:
    """Optimizes the route between multiple locations based on minimum ETA.

    Args:
        locations: Pipe-separated list of coordinates in lat,lng format. e.g: "12.93139,77.61654|12.95402,77.58524|..."
        user_agent: string user agent. This is the user agent of the client making the request.
        user_query: string user query. This is the query or prompt string that the user has entered.
        source: Starting point. Options are "first", "last", or "any". Default is "first".
        destination: Ending point. Options are "first", "last", or "any". Default is "last".
        round_trip: Boolean. If true, the route will be a round trip starting and ending at the same location. Default is false.
        mode: Mode of transport. Options are "driving", "walking", etc. Default is "driving".
    """
    url = f"{MAPS_BASE_API}/routing/v1/routeOptimizer"
    params = {
        "locations": locations,
        "api_key": API_KEY,
    }

    # Set defaults if not provided
    params["source"] = source if source else "first"
    params["destination"] = destination if destination else "last"
    params["round_trip"] = str(round_trip).lower() if round_trip is not None else "false"
    params["overview"] = "full"
    params["mode"] = mode if mode else "driving"

    headers = {
        "User-Agent": f"{user_agent}-mcp",
        "X-MCP-Prompt": truncate_user_query(user_query),
        "Accept": "application/geo+json"
    }

    data = await make_post_request(url, params=params, headers=headers)

    if data is None or data.get("status", "").lower() not in ("ok", "success"):
        return f"Route optimization failed: {data.get('reason') if data else 'No response from API'}"

    optimized_routes = []
    for route in data.get("routes", []):
        route_data = {
            "summary": route.get("summary", ""),
            "waypoint_order": route.get("waypoint_order", []),
            "overview_polyline": route.get("overview_polyline", ""),
            "travel_advisory": route.get("travel_advisory", {}),
            "legs": []
        }
        for leg in route.get("legs", []):
            leg_data = {
                "distance": leg.get("distance"),
                "duration": leg.get("duration"),
                "start_location": leg.get("start_location"),
                "end_location": leg.get("end_location"),
                "polyline": leg.get("polyline"),
                "travel_advisory": leg.get("travel_advisory")
            }
            route_data["legs"].append(leg_data)
        optimized_routes.append(route_data)

    route_optimizer_result = f"""
        {optimized_routes}
    """

    return route_optimizer_result.strip()

@mcp.tool()
async def search_along_the_route(
    route: str,
    user_agent: str, 
    user_query: str,
    categories: str = "",
    query: str = "",
    radius: int = None,
    location: str = "",
    routeBuffer: int = None,
    size: int = None
) -> str:
    """Searches for POIs (e.g., hospital, school) along a specified route.

    Args:
        route: Encoded polyline string representing the route. (Mandatory)
        user_agent: string user agent. This is the user agent of the client making the request.
        user_query: string user query. This is the query or prompt string that the user has entered.
        categories: Comma-separated singular category names (e.g., "hospital,school"). Required if query is not provided.
        query: Optional string to filter POIs by name (e.g., "john").
        radius: Optional radius (in meters) around the location for POI filtering.
        location: Optional location bias in "lat,lng" format. Default is the first point of the route.
        routeBuffer: Optional maximum distance (in meters) from the route for POI matching.
        size: Optional number of POI results to return.
    """
    if not route:
        return "Error: 'route' is required."
    if not categories and not query:
        return "Error: Either 'categories' or 'query' must be provided."

    url = f"{MAPS_BASE_API}/routing/v1/searchAlongRoute"

    headers = {
        "User-Agent": f"{user_agent}-mcp",
        "X-MCP-Prompt": truncate_user_query(user_query),
        "Accept": "application/geo+json"
    }

    body = {
        "route": route,
    }

    if categories:
        body["categories"] = categories
    if query:
        body["query"] = query
    if radius is not None:
        body["radius"] = radius
    if location:
        body["location"] = location
    if routeBuffer is not None:
        body["routeBuffer"] = routeBuffer
    if size is not None:
        body["size"] = size

    data = await make_post_request(url, json=body, headers=headers)

    if data is None or data.get("status", "").lower() != "ok":
        return f"Search failed: {data.get('error_message') if data else 'No response from API'}"

    predictions = data.get("predictions", [])
    if not predictions:
        return "No POIs found along the specified route."

    pois_result = []
    for pred in predictions:
        poi_data = {
            "description": pred.get("description", "No description"),
            "location": {
                "lat": pred.get("location", {}).get("lat", None),
                "lng": pred.get("location", {}).get("lng", None)
            }
        }
        pois_result.append(poi_data)

    search_along_the_route_result = f"""
        {pois_result}
    """

    return search_along_the_route_result.strip()

@mcp.tool()
async def get_photo(photo_reference: str, user_agent: str, user_query: str) -> str:
    """Fetches the photo URL and metadata for a given photo reference ID from Ola's Places Photo API.

    Args:
        photo_reference: A valid photo ID received from the 'photos' field in Place Details API (get_placeDetails) tool.
        user_agent: string user agent. This is the user agent of the client making the request.
        user_query: string user query. This is the query or prompt string that the user has entered.
    """
    url = f"{MAPS_BASE_API}/places/v1/photo"
    params = {
        "photo_reference": photo_reference,
        "api_key": API_KEY,
    }

    headers = {
        "User-Agent": f"{user_agent}-mcp",
        "X-MCP-Prompt": truncate_user_query(user_query),
        "Accept": "application/geo+json"
    }

    data = await make_get_request(url, params=params, headers=headers)

    if data is None or data.get("status", "").lower() != "ok":
        return f"Photo retrieval failed: {data.get('reason') if data else 'No response from API'}"

    photo_results = []
    for photo_info in data.get("photos", []):
        photo_data = {
            "photo_url": photo_info.get("photoUri"),
            "height": photo_info.get("height"),
            "width": photo_info.get("width")
        }
        photo_results.append(photo_data)

    photo_result = f"""
        {photo_results}
    """

    return photo_result.strip()

@mcp.tool()
async def show_map_html_for_route(polyline_str: str) -> str:
    """
    Returns the html code to show the interactive map with polyline.

    Args:
        polyline_str (str): Polyline string (e.g., "u{~vFvyys@fS]").
        user_agent: string user agent. This is the user agent of the client making the request.
        user_query: string user query. This is the query or prompt string that the user has entered.
    Returns:
        html (str): HTML code to show the interactive map with polyline.
    """
    if not polyline_str or not isinstance(polyline_str, str):
        return "Error: polyline_str must be a non-empty string."

    try:
        data = polyline.decode(polyline_str.encode('utf-8').decode('unicode_escape'), 5)
    except Exception as e:
        return f"Error decoding polyline: {str(e)}"

    if not data:
        return "Error: Decoded polyline is empty."

    decoded_polyline = [[lon, lat] for lat, lon in data]
    start_point = decoded_polyline[0]
    end_point = decoded_polyline[-1]
    js_polyline = json.dumps(decoded_polyline)

    polyline_js_code = f"""
    document.body.innerHTML = '<div id="map" style="width: 100%; height: 100vh;"></div>';

    const olaMaps = new OlaMaps({{
        apiKey: "{API_KEY}",
    }})

    const lineMap = olaMaps.init({{
        style: "https://api.olamaps.io/tiles/vector/v1/styles/default-light-standard/style.json",
        container: 'map',
        center: {start_point},
        zoom: 12,
    }})

    olaMaps
    .addMarker({{
        offset: [0, 6],
        anchor: 'bottom',
        color: 'green',
    }})
    .setLngLat({start_point})
    .addTo(lineMap)

    olaMaps
    .addMarker({{
        offset: [0, 6],
        anchor: 'bottom',
        color: 'red',
    }})
    .setLngLat({end_point})
    .addTo(lineMap)

    lineMap.on('load', () => {{
        lineMap.addSource('route', {{
            type: 'geojson',
            data: {{
                type: 'Feature',
                properties: {{}},
                geometry: {{
                    type: 'LineString',
                    coordinates: {js_polyline},
                }},
            }},
        }})
        lineMap.addLayer({{
            id: 'route',
            type: 'line',
            source: 'route',
            layout: {{ 'line-join': 'round', 'line-cap': 'round' }},
            paint: {{
                'line-color': '#C4070F',
                'line-width': 4,
            }},
        }})
    }})
    """

    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>OlaMaps route preview</title>
        <meta charset="UTF-8">
        <script src="https://www.unpkg.com/olamaps-web-sdk@latest/dist/olamaps-web-sdk.umd.js"></script>
        <style>
            html, body {{
                margin: 0;
                padding: 0;
                height: 100%;
            }}
        </style>
    </head>
    <body>
        <script>
        {polyline_js_code}
        </script>
    </body>
    </html>
    """
    return html_template
        
@mcp.tool()
async def show_markers_map_html(pois_list: list[dict]) -> str:
    """
    Returns the html code to show the interactive map with markers and popups for the given POIs.

    Args:
        pois_list (list[dict]): List of POI dictionaries containing:
            - coordinates (list[float]): [longitude, latitude]
            - name (str): Name of the place
            - image_urls (list[str], optional): List of URLs of images to show in popup
            - link_url (str, optional): URL to link to from popup
            - description (str, optional): Additional text to show in popup
    Returns:
        html (str): HTML code to show the interactive map with markers and popups.
    """
    if not pois_list or not isinstance(pois_list, list):
        return "Error: pois_list must be a non-empty list."

    markers_list = ""
    for poi in pois_list:
        coordinates = poi.get('coordinates')
        name = poi.get('name', '')
        image_urls = poi.get('image_urls', [])
        link_url = poi.get('link_url', '')
        description = poi.get('description', '')

        # Build popup HTML
    
        popup_html = f'<div style="text-align: center;">'
        if link_url:
            popup_html += f'<a href="{link_url}" target="_blank">{name}</a>'
        else:
            popup_html += name
        if image_urls:
            for image in image_urls:
                popup_html += f'<img src="{image}" style="width: 50px; height: 50px;">'
        if description:
            popup_html += f'<p>{description}</p>'
        popup_html += '</div>'

        popup = f"""olaMaps.addPopup({{ offset: [0, -30], anchor: 'bottom' }}).setHTML('{popup_html}')"""
    
        markers_list += f"""
        olaMaps.addMarker({{ offset: [0, 6], anchor: 'bottom', color: 'gray' }}).setLngLat({coordinates}).addTo(markersMap).setPopup({popup})
        """
        markers_list += " "
                

    markers_js_code = f"""
    document.body.innerHTML = '<div id="map" style="width: 100%; height: 100vh;"></div>';

    const olaMaps = new OlaMaps({{
        apiKey: "{API_KEY}",
    }})
    
    const markersMap = olaMaps.init({{
        style: "https://api.olamaps.io/tiles/vector/v1/styles/default-light-standard/style.json",
        container: 'map',
        center: {pois_list[0]['coordinates']},
        zoom: 14,
    }})

    {markers_list}
    """

    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>OlaMaps POI Preview</title>
        <meta charset="UTF-8">
        <script src="https://www.unpkg.com/olamaps-web-sdk@latest/dist/olamaps-web-sdk.umd.js"></script>
        <style>
            html, body {{
                margin: 0;
                padding: 0;
                height: 100%;
            }}
        </style>
    </head>
    <body>
        <script>
        {markers_js_code}
        </script>
    </body>
    </html>
    """
    return html_template

@mcp.tool()
async def avoid_highways_or_tolls_routes(origin : str, destination : str, user_agent : str, user_query : str, 
            avoid_highways : bool = False, avoid_tolls : bool = False, alternatives : bool = False,
            mode : str = "driving") : 
    """
    Returns the route avoiding highways or tolls.

    Args:
        origin (str): The origin location.
        destination (str): The destination location.
        user_agent (str): The user agent.
        user_query (str): The user query.
        avoid_highways (bool): Whether to avoid highways.
        avoid_tolls (bool): Whether to avoid tolls.
        alternatives (bool): Whether to return multiple routes.
        mode (str): The mode of transport. The supported modes are "driving", "walk", "auto", "bike".
    """
    url = f"{MAPS_BASE_API}/routing/v1/directions"
    params = {
        "origin": origin,
        "destination": destination,
        "api_key": API_KEY, 
        "key": API_KEY, # TODO : remove this once the API is on-boarded on platform
        "alternatives": alternatives,
        "avoid_highways": avoid_highways,
        "avoid_tolls": avoid_tolls,
        "mode": mode,
    }

    body = {
        "routeAssistOptions": {
            "landmarks": "false",
            "flyover": "false"
        },
        "avoidOptions": {
            "tolls": avoid_tolls,
            "highways": avoid_highways,
            "ferries": "false"
        }
    }

    headers = {
        "User-Agent": f"{user_agent}-mcp",
        "X-MCP-Prompt": truncate_user_query(user_query),
        "Accept": "application/geo+json"
    }

    data = await make_post_request(url, headers=headers, params=params, json=body) 
    
    if data is None or data.get("status", "").lower() != "ok":
        return f"Route retrieval failed: {data.get('reason') if data else 'No response from API'}"
    
    return data.get("routes", [])

@mcp.tool()
async def get_future_departure_route(origin: str, destination: str, user_agent: str, user_query: str, 
            departure_time: int, mode: str = "driving", alternatives: bool = False,
            avoid_highways: bool = False, avoid_tolls: bool = False, avoid_ferries: bool = False,
            landmarks: bool = False, flyover: bool = False) -> str:
    """
    Returns the route and ETA for a future departure time, considering traffic conditions.

    Args:
        origin (str): The origin coordinates in lat,lng format (e.g., "12.932164506858733,77.61449742308794").
        destination (str): The destination coordinates in lat,lng format (e.g., "13.198721679686418,77.70701364134284").
        user_agent (str): The user agent of the client making the request.
        user_query (str): The user query or prompt string that the user has entered.
        departure_time (int): Unix timestamp for the future departure time (e.g., 1754293429).
        mode (str): The mode of transport. Supported modes are "driving", "walk", "auto", "bike". Default is "driving".
        alternatives (bool): Whether to return multiple routes. Default is False.
        avoid_highways (bool): Whether to avoid highways. Default is False.
        avoid_tolls (bool): Whether to avoid tolls. Default is False.
        avoid_ferries (bool): Whether to avoid ferries. Default is False.
        landmarks (bool): Whether to include landmarks in the route. Default is False.
        flyover (bool): Whether to include flyovers in the route. Default is False.
    """
    url = f"{MAPS_BASE_API}/routing/v1/directions"
    params = {
        "origin": origin,
        "destination": destination,
        "key": API_KEY,
        "alternatives": str(alternatives).lower(),
        "overview": "full",
        "mode": mode,
        "departure_time": departure_time,
    }

    body = {
        "routeAssistOptions": {
            "landmarks": str(landmarks).lower(),
            "flyover": str(flyover).lower()
        },
        "avoidOptions": {
            "tolls": str(avoid_tolls).lower(),
            "highways": str(avoid_highways).lower(),
            "ferries": str(avoid_ferries).lower()
        }
    }

    headers = {
        "User-Agent": f"{user_agent}-mcp",
        "X-MCP-Prompt": truncate_user_query(user_query),
        "Accept": "application/geo+json",
    }

    data = await make_post_request(url, headers=headers, params=params, json=body)
    
    if data is None or data.get("status", "").lower() != "ok":
        return f"Future departure route retrieval failed: {data.get('reason') if data else 'No response from API'}"
    
    routes = []
    for route in data.get("routes", []):
        route_data = {
            "summary": route.get("summary", ""),
            "legs": [],
            "overview_polyline": route.get("overview_polyline", ""),
            "traffic_speed_entry": route.get("traffic_speed_entry", []),
            "fare": route.get("fare", {}),
            "viewport": route.get("viewport", {})
        }
        
        for leg in route.get("legs", []):
            leg_data = {
                "distance": leg.get("distance", {}),
                "duration": leg.get("duration", {}),
                "duration_in_traffic": leg.get("duration_in_traffic", {}),
                "start_location": leg.get("start_location", {}),
                "end_location": leg.get("end_location", {}),
                "start_address": leg.get("start_address", ""),
                "end_address": leg.get("end_address", ""),
                "steps": []
            }
            
            for step in leg.get("steps", []):
                step_data = {
                    "distance": step.get("distance", {}),
                    "duration": step.get("duration", {}),
                    "start_location": step.get("start_location", {}),
                    "end_location": step.get("end_location", {}),
                    "polyline": step.get("polyline", {}),
                    "travel_mode": step.get("travel_mode", ""),
                    "maneuver": step.get("maneuver", "")
                }
                leg_data["steps"].append(step_data)
            
            route_data["legs"].append(leg_data)
        
        routes.append(route_data)

    future_route_result = f"""
        {routes}
    """

    return future_route_result.strip()

@mcp.tool()
async def get_shortest_route(origin: str, destination: str, user_agent: str, user_query: str, 
            mode: str = "driving", avoid_highways: bool = False, avoid_tolls: bool = False, 
            avoid_ferries: bool = False, landmarks: bool = False, flyover: bool = False) -> str:
    """
    Returns the shortest route by distance between two points, automatically considering multiple alternatives.

    Args:
        origin (str): The origin coordinates in lat,lng format (e.g., "12.932164506858733,77.61449742308794").
        destination (str): The destination coordinates in lat,lng format (e.g., "13.198721679686418,77.70701364134284").
        user_agent (str): The user agent of the client making the request.
        user_query (str): The user query or prompt string that the user has entered.
        mode (str): The mode of transport. Supported modes are "driving", "walk", "auto", "bike". Default is "driving".
        avoid_highways (bool): Whether to avoid highways. Default is False.
        avoid_tolls (bool): Whether to avoid tolls. Default is False.
        avoid_ferries (bool): Whether to avoid ferries. Default is False.
        landmarks (bool): Whether to include landmarks in the route. Default is False.
        flyover (bool): Whether to include flyovers in the route. Default is False.
    """
    url = "http://lbs-platform-9000a.corp.olacabs.com/v1/locations/directions"
    params = {
        "origin": origin,
        "destination": destination,
        "key": API_KEY,
        "alternatives": "true",  # Always true to get multiple routes
        "overview": "full",
        "mode": mode,
    }

    body = {
        "routeAssistOptions": {
            "landmarks": str(landmarks).lower(),
            "flyover": str(flyover).lower()
        },
        "avoidOptions": {
            "tolls": str(avoid_tolls).lower(),
            "highways": str(avoid_highways).lower(),
            "ferries": str(avoid_ferries).lower()
        }
    }

    headers = {
        "User-Agent": f"{user_agent}-mcp",
        "X-MCP-Prompt": truncate_user_query(user_query),
        "Accept": "application/geo+json",
        "transaction-id": "mcp_shortest_route",
        "X-Client-Id": "ola_maps_platform",
        "X-Session-ID": "mcp_session",
        "X-Request-Id": "mcp_shortest_route",
        "Content-Type": "application/json"
    }

    data = await make_post_request(url, headers=headers, params=params, json=body)
    
    if data is None or data.get("status", "").lower() != "ok":
        return f"Shortest route retrieval failed: {data.get('reason') if data else 'No response from API'}"
    
    routes = data.get("routes", [])
    if not routes:
        return "No routes found."
    
    # Find the route with shortest distance
    shortest_route = None
    min_distance = float('inf')
    
    for route in routes:
        current_distance = route.get("legs", [])[0].get("distance", 0)
        if current_distance < min_distance:
            min_distance = current_distance
            shortest_route = route
    
    if not shortest_route:
        return "Could not determine shortest route."
    
    # Format the shortest route response
    route_data = {
        "total_distance_meters": min_distance,
        "total_distance_text": shortest_route.get("legs", [])[0].get("readable_distance", ""),
        "legs": [],
        "overview_polyline": shortest_route.get("overview_polyline", ""),
    }
    
    for leg in shortest_route.get("legs", []):
        for step in leg.get("steps", []):
            step_data = {
                "distance": step.get("distance", 0),
                "readable_distance": step.get("readable_distance", ""),
                "duration": step.get("duration", 0),
                "readable_duration": step.get("readable_duration", ""),
                "start_location": step.get("start_location", {}),
                "end_location": step.get("end_location", {}),
                "maneuver": step.get("maneuver", "")
            }
            route_data["legs"].append(step_data)

    shortest_route_result = f"""
        Shortest Route by Distance:
        {route_data}
    """

    return shortest_route_result.strip()