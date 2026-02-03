#!/usr/bin/env python3
"""
Google Maps Static Image Generator for Shuttle Routes
Generates static map images showing shuttle routes and stops
"""
import pandas as pd
import os
import urllib.parse
import requests
from typing import List, Dict, Tuple

class GoogleMapsGenerator:
    """Generate Google Maps static images for shuttle routes"""
    
    def __init__(self, api_key: str):
        """
        Initialize with Google Maps API key
        
        Args:
            api_key: Google Maps Static Maps API key
        """
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/staticmap"
        self.max_markers = 25  # Google Maps limit for static maps
        self.max_path_points = 25
    
    def load_locations(self, lat_lon_file: str) -> Dict[str, Tuple[float, float]]:
        """Load location coordinates from CSV"""
        df = pd.read_csv(lat_lon_file)
        locations = {}
        for idx, row in df.iterrows():
            name = row['Name'].strip()
            try:
                lat = float(row['Latitude'])
                lon = float(row['Longitude'])
                locations[name] = (lat, lon)
            except (ValueError, TypeError) as e:
                print(f"Warning: Failed to parse coordinates for {name}: {e}")
        return locations
    
    def load_routes(self, routes_file: str) -> List[Dict]:
        """Load shuttle routes from CSV"""
        df = pd.read_csv(routes_file)
        return df.to_dict('records')
    
    def generate_route_url(self, route: Dict, locations: Dict, width: int = 800, height: int = 600) -> str:
        """
        Generate Google Maps URL for a single route
        
        Args:
            route: Route record from shuttle_routes.csv
            locations: Dictionary of location coordinates
            width: Map width in pixels
            height: Map height in pixels
            
        Returns:
            URL string for Google Maps static image
        """
        # Parse route sequence
        route_stops = [stop.strip() for stop in route['route_sequence'].split('->')]
        
        # Build parameters with fixed center and zoom for Ohio State campus
        params = {
            'size': f'{width}x{height}',
            'key': self.api_key,
            'style': 'feature:all|element:labels|visibility:on',
        }
        
        # Add markers for stops (different colors for start/end/intermediate)
        markers = []
        
        for idx, stop_name in enumerate(route_stops):
            stop_name_clean = stop_name.strip()
            if stop_name_clean in locations:
                lat, lon = locations[stop_name_clean]
                # Format: color:color|label:label|lat,lon
                if idx == 0:
                    # Start point - green
                    markers.append(f"color:green|label:S|{lat},{lon}")
                elif idx == len(route_stops) - 1:
                    # End point - red
                    markers.append(f"color:red|label:E|{lat},{lon}")
                else:
                    # Intermediate stops - blue
                    markers.append(f"color:blue|label:{idx}|{lat},{lon}")
            else:
                print(f"Warning: Location '{stop_name_clean}' not found in location map")
        
        if markers:
            params['markers'] = markers
        
        # Add path (route line)
        path_points = []
        for stop_name in route_stops:
            stop_name_clean = stop_name.strip()
            if stop_name_clean in locations:
                lat, lon = locations[stop_name_clean]
                path_points.append(f"{lat},{lon}")
        
        if path_points:
            path_str = "color:0x0000ff|weight:5|" + "|".join(path_points)
            params['path'] = path_str
        
        # Generate URL - handle markers as separate parameters
        query_parts = []
        for key, value in params.items():
            if key == 'markers':
                # markers is a list, add each one as separate parameter
                continue
            query_parts.append(f"{key}={urllib.parse.quote(str(value), safe=',|')}")
        
        # Add markers
        for marker in markers:
            query_parts.append(f"markers={urllib.parse.quote(marker, safe=',|')}")
        
        query_string = "&".join(query_parts)
        return f"{self.base_url}?{query_string}"
    
    def generate_all_routes_url(self, routes: List[Dict], locations: Dict, 
                                width: int = 1200, height: int = 800) -> str:
        """
        Generate Google Maps URL showing all routes and stops
        
        Args:
            routes: List of route records
            locations: Dictionary of location coordinates
            width: Map width in pixels
            height: Map height in pixels
            
        Returns:
            URL string for Google Maps static image
        """
        params = {
            'size': f'{width}x{height}',
            'key': self.api_key,
            'center': '40.0046,-83.0028',  # Center of all locations (mean coordinates)
            'zoom': '12',  # Zoom level to show all campus + airport + easton area
            'style': 'feature:all|element:labels|visibility:on',
        }
        
        # Add all stops as markers
        markers = []
        for location_name, (lat, lon) in locations.items():
            markers.append(f"color:purple|{lat},{lon}")
        
        # Generate URL - handle markers as separate parameters
        query_parts = []
        for key, value in params.items():
            query_parts.append(f"{key}={urllib.parse.quote(str(value), safe=',|')}")
        
        # Add markers
        for marker in markers:
            query_parts.append(f"markers={urllib.parse.quote(marker, safe=',|')}")
        
        query_string = "&".join(query_parts)
        return f"{self.base_url}?{query_string}"
    
    def save_route_map(self, route: Dict, locations: Dict, output_path: str) -> bool:
        """
        Download and save a single route map image
        
        Args:
            route: Route record
            locations: Dictionary of location coordinates
            output_path: File path to save the image
            
        Returns:
            True if successful, False otherwise
        """
        try:
            url = self.generate_route_url(route, locations)
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                print(f"Error downloading map: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error saving map: {str(e)}")
            return False
    
    def save_all_routes_map(self, routes: List[Dict], locations: Dict, output_path: str) -> bool:
        """
        Download and save a map showing all routes
        
        Args:
            routes: List of route records
            locations: Dictionary of location coordinates
            output_path: File path to save the image
            
        Returns:
            True if successful, False otherwise
        """
        try:
            url = self.generate_all_routes_url(routes, locations)
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                print(f"Error downloading map: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error saving map: {str(e)}")
            return False


def generate_all_route_maps(api_key: str, data_dir: str = None) -> Dict[str, str]:
    """
    Generate maps for all shuttle routes
    
    Args:
        api_key: Google Maps API key
        data_dir: Data directory path
        
    Returns:
        Dictionary mapping trip_id to map file paths
    """
    if data_dir is None:
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    
    maps_dir = os.path.join(data_dir, 'maps')
    os.makedirs(maps_dir, exist_ok=True)
    
    generator = GoogleMapsGenerator(api_key)
    
    # Load data
    lat_lon_file = os.path.join(data_dir, 'lat-lon.csv')
    routes_file = os.path.join(data_dir, 'shuttle_routes.csv')
    
    locations = generator.load_locations(lat_lon_file)
    routes = generator.load_routes(routes_file)
    
    result = {}
    
    # Generate individual route maps
    print(f"Generating maps for {len(routes)} routes...")
    for route in routes:
        trip_id = route['trip_id']
        output_path = os.path.join(maps_dir, f"{trip_id}.png")
        
        if generator.save_route_map(route, locations, output_path):
            result[trip_id] = output_path
            print(f"✅ Generated map for {trip_id}")
        else:
            print(f"❌ Failed to generate map for {trip_id}")
    
    # Generate overall map
    overall_output = os.path.join(maps_dir, 'all_routes.png')
    if generator.save_all_routes_map(routes, locations, overall_output):
        result['all_routes'] = overall_output
        print(f"✅ Generated overall map")
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python map_generator.py <GOOGLE_MAPS_API_KEY>")
        print("\nSet your API key as an environment variable or pass it as argument")
        sys.exit(1)
    
    api_key = sys.argv[1]
    maps = generate_all_route_maps(api_key)
    
    print(f"\n✅ Generated {len(maps)} maps")
    for trip_id, path in maps.items():
        print(f"  - {trip_id}: {path}")
